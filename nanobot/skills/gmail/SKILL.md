---
name: gmail
description: "Search, list, and read Gmail messages via the Praixy API proxy."
metadata: {"nanobot":{"emoji":"📧","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# Gmail

Access Gmail through the Praixy API proxy. All requests need the auth header.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## Recommended Workflow

1. **Search/list** message IDs with the raw API
2. **Fetch details** with the simple API (returns decoded, readable content)

## Search for Messages

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/gmail-raw/v1/users/me/messages?q=SEARCH_QUERY"
```

Gmail search syntax: `from:user@example.com`, `to:`, `subject:`, `is:unread`, `after:2025/01/01`, `has:attachment`, `label:LABEL_NAME`. Combine with spaces.

Returns `{"messages": [{"id": "...", "threadId": "..."}], "nextPageToken": "..."}`.

## Read a Message (Simple API - Recommended)

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/gmail-simple/messages/MESSAGE_ID"
```

Returns decoded JSON with `from`, `to`, `subject`, `date`, and `body_plaintext` or `body_markdown`.

## Batch Fetch Multiple Messages

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/gmail-simple/messages?ids=ID1,ID2,ID3"
```

Max 50 IDs per request.

## List Labels

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/gmail-simple/labels"
```

## List Threads

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/gmail-raw/v1/users/me/threads?q=SEARCH_QUERY"
```
