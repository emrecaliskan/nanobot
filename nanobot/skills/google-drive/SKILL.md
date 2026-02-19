---
name: google-drive
description: "Search and list files in Google Drive via the Praixy API proxy."
metadata: {"nanobot":{"emoji":"📁","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# Google Drive

Access Google Drive through the Praixy API proxy.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## List Recent Files

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/drive-raw/v3/files?fields=files(id,name,mimeType,modifiedTime)"
```

## Search Files

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/drive-raw/v3/files?q=name%20contains%20%27report%27"
```

**Query syntax** (URL-encode the `q` param):
- `name contains 'report'` - name search
- `mimeType = 'application/pdf'` - PDFs
- `mimeType = 'application/vnd.google-apps.document'` - Google Docs
- `mimeType = 'application/vnd.google-apps.spreadsheet'` - Google Sheets
- `mimeType = 'application/vnd.google-apps.folder'` - folders
- `modifiedTime > '2025-01-01T00:00:00'` - modified after date
- `'FOLDER_ID' in parents` - files in a folder
- `trashed = false` - exclude trash
- Combine with `and`: `name contains 'budget' and mimeType = 'application/vnd.google-apps.spreadsheet'`

## Get File Metadata

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/drive-raw/v3/files/FILE_ID?fields=*"
```

## List Shared Drives

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/drive-raw/v3/drives"
```

## Files from Shared Drives

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/drive-raw/v3/files?includeItemsFromAllDrives=true&supportsAllDrives=true"
```

**Parameters:** `pageSize` (1-1000), `pageToken`, `orderBy` (e.g. `modifiedTime desc`), `fields`.
