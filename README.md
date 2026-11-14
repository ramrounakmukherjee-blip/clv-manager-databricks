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
* `ENDPOINT_NAME` - Lakebase Postgres endpoint (injected; falls back to `projects/clv-app-db/branches/production/endpoints/primary`).
* `PGDATABASE`, `PGUSER`, `PGHOST`, `PGPORT`, `PGSSLMODE` - injected Lakebase Postgres connection settings.

## Running locally

Install dependencies and run the Streamlit server (requires Databricks workspace authentication):

```sh
pip install -r requirements.txt
streamlit run app.py
```
