---
name: google-calendar
description: "List calendars and query events via the Praixy API proxy."
metadata: {"nanobot":{"emoji":"📅","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# Google Calendar

Access Google Calendar through the Praixy API proxy.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## List Calendars

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/calendar-raw/v3/users/me/calendarList"
```

## List Upcoming Events

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/calendar-raw/v3/calendars/primary/events?timeMin=2025-01-28T00:00:00Z&singleEvents=true&orderBy=startTime&maxResults=10"
```

Use `primary` for the user's main calendar. Timestamps must be RFC3339 (e.g. `2025-02-19T00:00:00Z`).

## Events in a Date Range

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/calendar-raw/v3/calendars/primary/events?timeMin=2025-02-01T00:00:00Z&timeMax=2025-03-01T00:00:00Z&singleEvents=true"
```

## Search Events

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/calendar-raw/v3/calendars/primary/events?q=meeting&singleEvents=true"
```

## Get a Specific Event

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/calendar-raw/v3/calendars/primary/events/EVENT_ID"
```

**Key parameters:** `timeMin`, `timeMax` (RFC3339), `q` (text search), `singleEvents=true` (expand recurring), `orderBy=startTime` (requires singleEvents=true), `maxResults`.
