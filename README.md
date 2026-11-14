# clv-manager

A Databricks App (Streamlit) for managing customer lifetime value (CLV).

Users can view, filter, search, and track per-customer lifetime value metrics, and jump straight to the connected Databricks AI/BI dashboard.

## App details

| Field | Value |
| --- | --- |
| App name | clv-manager |
| App ID | 968d3779-6161-405e-b5d0-46ddebf185a9 |
| App URL | https://clv-manager-7474658865741961.aws.databricksapps.com |
| Compute size | MEDIUM |
| Command | streamlit run app.py |
| API scopes | sql |

## Connected resources

* **AI/BI dashboard**: Sample Customers Overview (UUID `01f1e00255a51ab68b084f6c014c9a40`) - the app deep-links to it and the app URL is embedded back into the dashboard.
* **Lakebase Postgres database**: `projects/clv-app-db/branches/production/databases/databricks-postgres` (resource name `postgres`, permission CAN_CONNECT_AND_CREATE). The app mirrors per-customer CLV metrics into the `clv.customer_clv` table using OAuth-generated database credentials.
* **SQL warehouse**: `/sql/1.0/warehouses/dcc76b7ee7627b72` (injected as `SQL_WAREHOUSE_HTTP_PATH`) for the CLV aggregation query.

## Data source

Per-customer CLV aggregation from the shared Databricks sample data in `samples.bakehouse` (`sales_customers` joined with `sales_transactions`), computing purchase count, lifetime value, average order value, and days since last purchase. Customers are segmented into High / Medium / Low CLV tiers by quartile.

## Environment variables

* `SQL_WAREHOUSE_HTTP_PATH` - set in `app.yaml` (the app's SQL warehouse).
* `LAKEBASE_ENDPOINT` - Lakebase Postgres endpoint, declared in `app.yaml` via `valueFrom: postgres`; `app.py` also honors `ENDPOINT_NAME` and falls back to `projects/clv-app-db/branches/production/endpoints/primary`.
* `PGDATABASE`, `PGUSER`, `PGHOST`, `PGPORT`, `PGSSLMODE` - injected Lakebase Postgres connection settings.

## Repository contents

Everything built in the Databricks workspace for the CLV Manager project:

* `app.py`, `app.yaml`, `requirements.txt` - the Databricks App source.
* `notebooks/Sample Table Generation` - notebook that creates the `workspace.default.sample_customers` Unity Catalog table and generates the 50 sample customer records (SQL DDL + PySpark).
* `data/sample_customers.csv` - export of all 50 generated records from that table (snapshot taken 2026-11-14).
* `data/lakebase_customer_clv.csv` - export of the 300 customer CLV records mirrored into the Lakebase `clv-app-db` database table `clv.customer_clv` (snapshot taken 2026-11-14).
* `dashboards/sample_customers_overview.json` - serialized config of the "Sample Customers Overview" AI/BI dashboard (UUID `01f1e00255a51ab68b084f6c014c9a40`), stored as plain JSON. To restore it in a Databricks workspace, rename to `.lvdash.json` and import.

## Running locally

Install dependencies and run the Streamlit server (requires Databricks workspace authentication):

```sh
pip install -r requirements.txt
streamlit run app.py
```
