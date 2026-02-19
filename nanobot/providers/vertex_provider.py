"""Vertex AI provider using the google-genai SDK."""

from __future__ import annotations

import uuid
from typing import Any

from google import genai
from google.genai import types

from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


def _openai_tools_to_genai(tools: list[dict[str, Any]]) -> list[types.Tool]:
    """Convert OpenAI-format tool definitions to google-genai FunctionDeclarations."""
    declarations = []
    for tool in tools:
        if tool.get("type") != "function":
            continue
        fn = tool["function"]
        declarations.append(types.FunctionDeclaration(
            name=fn["name"],
            description=fn.get("description", ""),
            parameters_json_schema=fn.get("parameters"),
        ))
    return [types.Tool(function_declarations=declarations)] if declarations else []


def _openai_messages_to_genai(
    messages: list[dict[str, Any]],
) -> tuple[str | None, list[types.Content]]:
    """Convert OpenAI-format messages to google-genai Contents.

    Returns (system_instruction, contents).
    Preserves Gemini thought signatures on function call parts.
    """
    system_parts: list[str] = []
    contents: list[types.Content] = []

    for msg in messages:
        role = msg.get("role", "user")

        if role == "system":
            system_parts.append(msg.get("content", ""))
            continue

        if role == "assistant":
            parts: list[types.Part] = []
            # Text content
            if msg.get("content"):
                parts.append(types.Part.from_text(text=msg["content"]))
            # Tool calls the model previously made
            for tc in msg.get("tool_calls", []):
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    import json_repair
                    args = json_repair.loads(args)
                meta = tc.get("metadata", {})
                part = types.Part(function_call=types.FunctionCall(
                    name=fn.get("name", ""),
                    args=args,
                ))
                # Replay thought signature if present (required by Gemini 3+)
                if meta.get("thought_signature"):
                    part.thought_signature = meta["thought_signature"]
                if meta.get("thought"):
                    part.thought = meta["thought"]
                parts.append(part)
            if parts:
                contents.append(types.Content(role="model", parts=parts))
            continue

        if role == "tool":
            # Tool result being sent back
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=msg.get("name", msg.get("tool_call_id", "unknown")),
                    response={"result": msg.get("content", "")},
                )],
            ))
            continue

        # user message
        content = msg.get("content", "")
        if isinstance(content, list):
            # Multimodal content (text + images)
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(types.Part.from_text(text=part))
                elif isinstance(part, dict):
                    if part.get("type") == "text":
                        parts.append(types.Part.from_text(text=part.get("text", "")))
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:"):
                            import base64
                            header, b64data = url.split(",", 1)
                            mime = header.split(":")[1].split(";")[0]
                            parts.append(types.Part.from_bytes(
                                data=base64.b64decode(b64data),
                                mime_type=mime,
                            ))
                        else:
                            parts.append(types.Part.from_uri(file_uri=url, mime_type="image/jpeg"))
            contents.append(types.Content(role="user", parts=parts))
        else:
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=content)],
            ))

    system_instruction = "\n\n".join(system_parts) if system_parts else None
    return system_instruction, contents


class VertexAIProvider(LLMProvider):
    """Google Vertex AI provider using the google-genai SDK."""

    def __init__(
        self,
        project: str,
        location: str = "us-central1",
        default_model: str = "gemini-2.5-flash",
    ):
        super().__init__(api_key=project, api_base=location)
        self.default_model = default_model
        self._client = genai.Client(vertexai=True, project=project, location=location)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        model_name = (model or self.default_model).removeprefix("vertex_ai/")

        system_instruction, contents = _openai_messages_to_genai(messages)
        genai_tools = _openai_tools_to_genai(tools) if tools else []

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max(1, max_tokens),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            thinking_config=types.ThinkingConfig(thinking_budget=2048),
        )
        if genai_tools:
            config.tools = genai_tools
        if system_instruction:
            config.system_instruction = system_instruction

        try:
            response = await self._client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            return self._parse_response(response)
        except Exception as e:
            return LLMResponse(content=f"Error calling Vertex AI: {e}", finish_reason="error")

    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse google-genai response into LLMResponse."""
        tool_calls: list[ToolCallRequest] = []
        text_parts: list[str] = []

        candidate = response.candidates[0] if response.candidates else None
        if candidate and candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.text:
                    text_parts.append(part.text)
                if part.function_call:
                    # Capture thought signature for Gemini 3+ models
                    meta: dict[str, Any] = {}
                    if getattr(part, "thought_signature", None):
                        meta["thought_signature"] = part.thought_signature
                    if getattr(part, "thought", None):
                        meta["thought"] = part.thought
                    tool_calls.append(ToolCallRequest(
                        id=f"call_{uuid.uuid4().hex[:24]}",
                        name=part.function_call.name,
                        arguments=dict(part.function_call.args) if part.function_call.args else {},
                        metadata=meta,
                    ))

        finish_reason = "stop"
        if candidate and candidate.finish_reason:
            reason = str(candidate.finish_reason).lower()
            if "tool" in reason or "function" in reason:
                finish_reason = "tool_calls"
            elif "stop" in reason:
                finish_reason = "stop"
            elif "length" in reason or "max" in reason:
                finish_reason = "length"

        usage = {}
        if response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(um, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(um, "total_token_count", 0) or 0,
            }

        return LLMResponse(
            content="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    def get_default_model(self) -> str:
        return self.default_model
