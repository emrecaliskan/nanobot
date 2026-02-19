---
name: crm
description: "Query companies, people, investments, and health checks via the CRM GraphQL API."
metadata: {"nanobot":{"emoji":"🏢","requires":{"bins":["curl"],"env":["MARSHAL_API_KEY"]}}}
---

# CRM

Query the CRM via GraphQL through the Praixy API proxy.

**Auth header (include on every request):**
```
-H "Authorization: Bearer $MARSHAL_API_KEY"
```

## GraphQL Endpoint

```bash
curl -s -X POST \
  -H "Authorization: Bearer $MARSHAL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://dev-ken.tail945f.ts.net:8443/api/crm/graphql" \
  -d '{"query": "YOUR_GRAPHQL_QUERY"}'
```

## Search Companies

```bash
curl -s -X POST -H "Authorization: Bearer $MARSHAL_API_KEY" \
  -H "Content-Type: application/json" \
  "https://dev-ken.tail945f.ts.net:8443/api/crm/graphql" \
  -d '{"query": "{ allCompanies(nameContains: \"acme\", limit: 10) { id name description permalink } }"}'
```

## Get a Company

```bash
-d '{"query": "{ company(id: 123) { id name description permalink } }"}'
```

## Search People

```bash
-d '{"query": "{ allPersons(nameContains: \"john\", limit: 10) { id firstName lastName permalink } }"}'
```

## Get Contacts for a Company

```bash
-d '{"query": "{ allContacts(companyId: 123, leftCompany: false) { id email roles person { firstName lastName } } }"}'
```

## Investments

```bash
-d '{"query": "{ allInvestments(status: \"INVESTED\", limit: 50) { id company { name } fund { name } statusDisplay roundDisplay dateFunded permalink } }"}'
```

**Investment status values:** `INVESTED`, `IN_PROCESS`, `NEEDS_DECISION`, `CLOSING`, `PASSING`, `EXITED`, `PASSED`, `LOST_BID`, `ON_HOLD`.

## Health Checks

```bash
-d '{"query": "{ allHealthChecks(years: [2024], quarters: [1, 2]) { id company { name } year quarter status runway notes } }"}'
```

**Health check status:** `green` (healthy), `yellow` (caution), `red` (needs attention).

## Available Queries

| Query | Key Arguments |
|-------|---------------|
| `company(id)` | single company by ID |
| `person(id)` | single person by ID |
| `investment(id)` | single investment by ID |
| `allCompanies` | `nameContains`, `primaryElectricContactId`, `limit` |
| `allPersons` | `nameContains`, `limit` |
| `allContacts` | `companyId`, `emailContains`, `leftCompany`, `limit` |
| `allInvestments` | `status`, `dateFundedAfter`, `dateFundedBefore`, `limit` |
| `allHealthChecks` | `companyIds`, `years`, `quarters`, `status`, `limit` |

All entities have a `permalink` field for the web UI link. Default `limit` is 50. Dates are ISO 8601.

## Schema Introspection

```bash
curl -s -H "Authorization: Bearer $MARSHAL_API_KEY" \
  "https://dev-ken.tail945f.ts.net:8443/api/crm/schema"
```
