---
name: google-docs
description: "Read Google Docs and Sheets via the Praixy API proxy."
metadata: {"nanobot":{"emoji":"📄","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# Google Docs & Sheets

Access Google Docs and Sheets through the Praixy API proxy.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## Google Docs

### List Documents

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/docs-raw/v1/documents?orderBy=modifiedTime%20desc&pageSize=10"
```

### Read a Document

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/docs-raw/v1/documents/DOCUMENT_ID"
```

With all tabs: append `?includeTabsContent=true`.

### Search Documents

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/docs-raw/v1/documents?q=name%20contains%20%27report%27"
```

## Google Sheets

### List Spreadsheets

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/sheets-raw/v4/spreadsheets?orderBy=modifiedTime%20desc&pageSize=10"
```

### Get Spreadsheet Metadata

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/sheets-raw/v4/spreadsheets/SPREADSHEET_ID"
```

### Read Cell Values

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/sheets-raw/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:D10"
```

Range uses A1 notation: `Sheet1!A1:D10`, `A1:B5`, `Sheet1`.

### Batch Read Multiple Ranges

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/sheets-raw/v4/spreadsheets/SPREADSHEET_ID/values:batchGet?ranges=Sheet1!A1:B5&ranges=Sheet1!C1:D5"
```

**Value parameters:** `valueRenderOption` (`FORMATTED_VALUE`, `UNFORMATTED_VALUE`, `FORMULA`), `majorDimension` (`ROWS`, `COLUMNS`).

**IDs:** Find document/spreadsheet IDs in their URLs: `docs.google.com/document/d/DOCUMENT_ID/edit` or `docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`.
