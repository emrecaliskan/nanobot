"""Helpers for parsing one-time reminder times with timezone support."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

_TZ_ALIASES = {
    "UTC": "UTC",
    "GMT": "UTC",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "ET": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "CT": "America/Chicago",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "MT": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "PT": "America/Los_Angeles",
}

_TIME_ONLY_RE = re.compile(
    r"^\s*(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>[AaPp][Mm])?\s*$"
)
_AT_WITH_TZ_SUFFIX_RE = re.compile(r"^\s*(?P<base>.+?)\s+(?P<tz>[A-Za-z]{2,5})\s*$")


def normalize_tz(tz: str | None) -> str | None:
    """Normalize timezone strings and common abbreviations."""
    if not tz:
        return None
    value = tz.strip()
    if not value:
        return None
    return _TZ_ALIASES.get(value.upper(), value)


def validate_tz(tz: str | None) -> str | None:
    """Validate and return a normalized timezone, or None."""
    normalized = normalize_tz(tz)
    if not normalized:
        return None
    try:
        ZoneInfo(normalized)
    except Exception as e:
        raise ValueError(f"unknown timezone '{tz}'") from e
    return normalized


def _parse_time_only(value: str) -> tuple[int, int] | None:
    m = _TIME_ONLY_RE.fullmatch(value)
    if not m:
        return None

    hour = int(m.group("hour"))
    minute = int(m.group("minute") or "0")
    ampm = (m.group("ampm") or "").lower()

    if minute > 59:
        raise ValueError("invalid minute in time")

    if ampm:
        if hour < 1 or hour > 12:
            raise ValueError("invalid hour in time")
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
    elif hour > 23:
        raise ValueError("invalid hour in time")

    return hour, minute


def parse_one_time_at(at: str, tz: str | None = None) -> tuple[int, str | None]:
    """
    Parse a one-time reminder target and return (epoch_ms, resolved_tz).

    Supported inputs:
    - ISO datetime (e.g. 2026-02-19T11:00:00 or 2026-02-19T11:00:00-05:00)
    - Time only (e.g. 11am, 18:30) -> schedules next occurrence
    - Optional timezone suffix in at (e.g. "2026-02-19T11:00:00 EST")
    """
    text = (at or "").strip()
    if not text:
        raise ValueError("at is required")

    resolved_tz = validate_tz(tz)

    if not resolved_tz:
        suffix = _AT_WITH_TZ_SUFFIX_RE.fullmatch(text)
        if suffix:
            maybe_tz = suffix.group("tz")
            try:
                resolved_tz = validate_tz(maybe_tz)
                text = suffix.group("base").strip()
            except ValueError:
                # Keep original text if suffix is not a valid timezone.
                pass

    time_only = _parse_time_only(text)
    if time_only:
        hour, minute = time_only
        tzinfo = ZoneInfo(resolved_tz) if resolved_tz else datetime.now().astimezone().tzinfo
        if tzinfo is None:
            raise ValueError("failed to determine local timezone")

        now = datetime.now(tzinfo)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return int(target.timestamp() * 1000), resolved_tz

    normalized = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as e:
        raise ValueError(f"invalid datetime '{at}'") from e

    if dt.tzinfo is None and resolved_tz:
        dt = dt.replace(tzinfo=ZoneInfo(resolved_tz))

    now_ms = int(datetime.now(dt.tzinfo).timestamp() * 1000) if dt.tzinfo else int(datetime.now().timestamp() * 1000)
    at_ms = int(dt.timestamp() * 1000)
    if at_ms <= now_ms:
        raise ValueError("at must be in the future")

    return at_ms, resolved_tz
