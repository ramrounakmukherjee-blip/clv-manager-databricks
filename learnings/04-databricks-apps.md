# 04 · Databricks Apps

## What they are

**Databricks Apps** let you host a real web app — Streamlit, Dash, Flask, Gradio — **inside your workspace**. Why that's better than it sounds:

* **Auth is handled for you.** The app runs as its own **service principal** (a machine identity) with OAuth credentials injected at runtime — no API keys baked into your code. Mine is `app-1xaduo clv-manager` with OAuth scope `sql`.
* **It can reach everything in your workspace** — query tables via a SQL warehouse, connect to Lakebase Postgres, deep-link to dashboards — all under Unity Catalog permissions.
* **Source lives in the workspace** (or a Git repo) — `app.py` + `app.yaml` + `requirements.txt` is the whole scaffold.

## The three source files

```yaml
# app.yaml — how to run the app and what env it gets
command: ['streamlit', 'run', 'app.py']
env:
  - name: 'SQL_WAREHOUSE_HTTP_PATH'
    value: '/sql/1.0/warehouses/<warehouse-id>'
  - name: 'LAKEBASE_ENDPOINT'
    valueFrom: postgres        # injected from a connected Lakebase resource
```

* `app.py` — the app itself. Mine: a Streamlit CLV explorer.
* `app.yaml` — run command, environment variables, resources. `valueFrom: postgres` pulls connection info from a connected resource instead of hardcoding secrets.
* `requirements.txt` — pip dependencies (streamlit, pandas, databricks-sdk, databricks-sql-connector, psycopg).

## What my app does (clv-manager)

1. **Queries** `samples.bakehouse` (customers ⋈ transactions) through a SQL warehouse and aggregates per-customer CLV: purchase count, lifetime value, average order value, days since last purchase.
2. **Tiers customers** by LTV quartiles — High (≥75th pct), Medium (≥25th), Low. Across the 300 customers: 77 High / 150 Medium / 73 Low; total LTV $66,471, average $222, 11.1 orders per customer.
3. **Renders the UI** — KPI cards, three charts (LTV by continent, tier distribution, top-10 customers — led by Lorraine James at ~$672), and a "track a customer" profile view.
4. **Filters everything reactively** — continent, country, gender, tier, LTV range slider, minimum purchases, name/email search.
5. **Mirrors results to Lakebase Postgres** on page load (→ [05](05-lakebase-postgres.md)) and **deep-links to the AI/BI dashboard** (→ [03](03-ai-bi-dashboards.md)).

## Deploy lifecycle (the part that bit me)

Apps have real state, and the order of operations matters:

1. `apps get <name>` — **always check status first**.
2. If `STOPPED` → `apps start <name> --timeout 20m`, wait for `RUNNING`.
3. Only when `RUNNING` → `apps deploy <name>` — deploying a stopped/new app fails.
4. Apps auto-stop when idle — that's normal, not a crash.

Deployed apps get a URL like `https://<app-name>-<workspace-id>.<region>.databricksapps.com`.

## Trying to host it elsewhere (Render) — lessons

I tried moving the same app to Render and learned the boundary:

* **Streamlit needs a long-running server**, which serverless platforms like Vercel don't offer; Render works, but you manage everything yourself.
* On Databricks Apps, `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET` are injected automatically. Elsewhere you must set them yourself — and generate an **OAuth secret** for the service principal (secrets are write-only: shown once at creation, never retrievable after).
* The start command must bind to the host's port: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true` — a wrong start command on Render literally tried to execute the word `PORT`.
* Grants still apply: the service principal needs permissions no matter where the app runs.

**Conclusion:** the platform-hosted version wins for anything already tied to your workspace. External hosting is worth it only when you need to escape the Databricks perimeter.
