---
name: slack-search
description: "Search Slack messages, list channels, and read conversation history via the Praixy API proxy."
metadata: {"nanobot":{"emoji":"💬","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# Slack Search & History

Access Slack through the Praixy API proxy. Read-only: search messages, list channels, read history.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## Search Messages

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/search.messages?query=project+update"
```

Supports [Slack search syntax](https://slack.com/help/articles/202528808): `from:@user`, `in:#channel`, `before:2025-02-01`, `after:2025-01-01`, `has:link`.

**Parameters:** `count` (max 100, default 20), `page`, `sort` (`score` or `timestamp`), `sort_dir` (`asc`/`desc`).

## List Channels

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/conversations.list"
```

Include DMs: `?types=public_channel,private_channel,im,mpim`

**Parameters:** `limit` (1-1000), `cursor`, `exclude_archived` (default true).

## Channel History

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/conversations.history?channel=CHANNEL_ID"
```

**Parameters:** `limit` (1-1000), `oldest`/`latest` (Unix timestamps), `cursor`.

## Thread Replies

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/conversations.replies?channel=CHANNEL_ID&ts=1234567890.123456"
```

## User Info

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/users.info?user_id=U1234567890"
```

## List Users

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack/users.list"
```

## Send DM to Yourself

```bash
curl -s -X POST -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/slack-simple/dm-self?text=Hello%20from%20nanobot!"
```

Sends from the Praixy bot. Useful for notifications and reminders.

**IDs:** Channel IDs start with `C`, user IDs with `U`. Timestamps include microseconds (e.g. `1234567890.123456`).
