# 05 · Lakebase Postgres (OLTP inside Databricks)

## Why this exists

The lakehouse (Delta tables, Spark, SQL warehouses) is built for **OLAP** — analytics over large scans. But lots of apps need **OLTP** — transactional row-level reads/writes: a Postgres database. **Lakebase** gives you that inside Databricks: a managed Postgres server next to your lakehouse, under the same governance, reachable by your apps. My app's whole "mirror the analytics results into a database" feature runs on it.

## The hierarchy

Lakebase organizes things like this:

```
projects/ clv-app-db
└── branches/ production
    ├── databases/ databricks-postgres
    │   └── schemas/ clv → tables/ customer_clv
    └── endpoints/ primary
```

* **Project** — the database's container (mine: `clv-app-db`).
* **Branch** — like a Git branch for your database; `production` is the live one.
* **Database** — the actual Postgres database (named `databricks-postgres` by default).
* **Endpoint** — the connection point; the `primary` endpoint's host is what you connect to.

My table: `clv.customer_clv` — 300 rows, one per customer, keyed by `customer_id` with a `synced_at` timestamp; the app upserts on every page load.

## Connecting from an app

The neat trick: **no static passwords**. The app asks Databricks to generate short-lived database credentials over OAuth (`generate_database_credential` on the endpoint), then connects with `psycopg`:

* host — from the endpoint's status
* database — `databricks_postgres`, port 5432, `sslmode=require`
* user — the service principal's client ID (or workspace user), password — the generated token

Because the credential is minted per session, nothing secret is ever stored in the app source. In `app.yaml` this shows up as `LAKEBASE_ENDPOINT: valueFrom: postgres` — the connected-resource injection.

## Gotchas I hit

* **Grants again** — Postgres roles mirror Databricks identities. The app's service principal needed `USAGE` on schema `clv` and `SELECT, INSERT, UPDATE` on `customer_clv` before it could write. Same lesson as Unity Catalog: check the service principal's grants first.
* **The `psycopg` driver must be installed** in the app environment (`requirements.txt`) — it isn't part of the default image.
* **Connection info is discoverable** — when env vars aren't injected, the app can look up its endpoint and current user via the Databricks SDK and build the connection from that. Good defensive pattern for external hosting.

## When to use what

| Need | Use |
| --- | --- |
| Analytics over millions of rows, BI, ML | Lakehouse tables (Delta) |
| Transactional app backend, row-level upserts | Lakebase Postgres |
| Both, sharing the same governance | Both — that's the point of the platform |
