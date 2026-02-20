"""HTTP relay channel for SSE-based message streaming.

This channel exposes a single POST /message endpoint that accepts inbound messages
from the router and streams outbound assistant messages/events via Server-Sent Events.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import uuid4

from aiohttp import web
from loguru import logger

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import HttpRelayConfig


class HttpRelayChannel(BaseChannel):
    """HTTP relay channel with SSE streaming output."""

    name = "http_relay"

    def __init__(self, config: HttpRelayConfig, bus: MessageBus):
        super().__init__(config, bus)
        self.config: HttpRelayConfig = config
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._pending: dict[str, asyncio.Queue[OutboundMessage]] = {}
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the HTTP server and keep running while gateway is active."""
        self._running = True
        app = web.Application()
        app.router.add_post("/message", self._handle_message_post)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner, self.config.host, int(self.config.port)
        )
        await self._site.start()

        logger.info(
            "HTTP relay channel started on {}:{}",
            self.config.host,
            self.config.port,
        )

        while self._running:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """Stop the relay HTTP server and clean up pending requests."""
        self._running = False
        for queue in self._pending.values():
            while not queue.empty():
                queue.get_nowait()
        self._pending.clear()

        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
            self._site = None

    async def send(self, msg: OutboundMessage) -> None:
        """Route outbound messages from the agent back to matching relay requests."""
        request_id = self._extract_request_id(msg)
        if not request_id:
            return

        queue: asyncio.Queue[OutboundMessage] | None
        async with self._lock:
            queue = self._pending.get(request_id)
        if queue is None:
            logger.debug(
                "No pending HTTP relay request for request_id={}",
                request_id,
            )
            return
        await queue.put(msg)

    async def _handle_message_post(self, request: web.Request) -> web.StreamResponse:
        body = await self._parse_request_body(request)
        if not isinstance(body, dict):
            return body

        sender_id = body.get("senderId") or body.get("sender_id")
        chat_id = body.get("chatId") or body.get("chat_id")
        content = body.get("content")
        metadata = body.get("metadata") or {}

        if not sender_id or not chat_id or content is None:
            return web.json_response(
                {"error": "Missing sender_id/chat_id/content"},
                status=400,
            )

        request_id = uuid4().hex
        metadata = self._normalize_metadata(metadata)
        metadata.setdefault("http_relay", {})
        metadata["http_relay"]["request_id"] = request_id

        queue: asyncio.Queue[OutboundMessage] = asyncio.Queue()
        async with self._lock:
            self._pending[request_id] = queue

        try:
            response = web.StreamResponse(
                status=200,
                reason="OK",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
            await response.prepare(request)
            try:
                await self._handle_message(
                    sender_id=str(sender_id),
                    chat_id=str(chat_id),
                    content=str(content),
                    media=[],
                    metadata=metadata,
                )
            except Exception as exc:
                logger.error(
                    "Failed to enqueue inbound message for HTTP relay request {}: {}",
                    request_id,
                    exc,
                )
                await self._write_sse_event(
                    response,
                    "response",
                    {"content": "I could not process this message. Please retry."},
                )
                return response

            while True:
                try:
                    outbound = await asyncio.wait_for(queue.get(), timeout=900)
                except asyncio.TimeoutError:
                    await self._write_sse_event(
                        response,
                        "response",
                        {"content": "Upstream response timed out."},
                    )
                    return response

                is_progress = bool(
                    (outbound.metadata or {})
                    .get("progress", {})
                    .get("is_progress")
                )
                event_type = "progress" if is_progress else "response"
                await self._write_sse_event(
                    response,
                    event_type,
                    {"content": outbound.content},
                )
                if not is_progress:
                    return response

        finally:
            async with self._lock:
                self._pending.pop(request_id, None)

    async def _parse_request_body(self, request: web.Request) -> dict[str, Any] | web.Response:
        try:
            body = await request.json()
        except Exception as e:
            logger.warning(f"Invalid JSON in /message payload: {e}")
            return web.json_response({"error": "Invalid JSON body"}, status=400)

        if not isinstance(body, dict):
            return web.json_response({"error": "Payload must be an object"}, status=400)

        return body

    @staticmethod
    def _normalize_metadata(metadata: Any) -> dict[str, Any]:
        return dict(metadata) if isinstance(metadata, dict) else {}

    @staticmethod
    def _extract_request_id(msg: OutboundMessage) -> str | None:
        progress = (msg.metadata or {}).get("progress", {})
        if isinstance(progress, dict):
            request_id = progress.get("request_id")
            if isinstance(request_id, str) and request_id:
                return request_id

        relay = (msg.metadata or {}).get("http_relay", {})
        if isinstance(relay, dict):
            request_id = relay.get("request_id")
            if isinstance(request_id, str) and request_id:
                return request_id
        return None

    @staticmethod
    async def _write_sse_event(
        response: web.StreamResponse,
        event: str,
        payload: dict[str, Any],
    ) -> None:
        await response.write(
            f"event: {event}\n"
            f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()
        )
