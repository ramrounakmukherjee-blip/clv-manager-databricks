# 📚 My Databricks Learning Notes

These are my notes from building **CLV Manager** — a customer lifetime value app — entirely on Databricks in a single day (2026-11-14), with a lot of help from **Genie**, Databricks' AI assistant. I'm keeping them here so future-me (or anyone else new to Databricks) can read them as a practical, project-driven introduction to what the platform can do.

## The one-day story

1. **Explored the Databricks workspace** — notebooks, compute, sample data, and how everything is organized. → [01](01-databricks-workspace.md)
2. **Generated a table of 50 sample customers** with PySpark (via a notebook Genie wrote for me), and learned how schemas and Unity Catalog work. → [02](02-schemas-and-unity-catalog.md)
3. **Built an AI/BI dashboard** ("Sample Customers Overview") on top of that table. → [03](03-ai-bi-dashboards.md)
4. **Built and deployed a Databricks App** — a Streamlit app (`clv-manager`) that computes customer lifetime value from Databricks sample data, with filters, KPI cards, charts, and a per-customer tracker. → [04](04-databricks-apps.md)
5. **Mirrored the CLV results into Lakebase Postgres** — Databricks' managed OLTP database. → [05](05-lakebase-postgres.md)
6. **Did all of the above with Genie**, the AI assistant, and pushed everything to GitHub. → [06](06-genie-the-ai-assistant.md)

## Reading order

| # | Note | What it covers |
| --- | --- | --- |
| 01 | [The Databricks Workspace](01-databricks-workspace.md) | What a workspace is, what lives inside it, compute types, Git integration |
| 02 | [Schemas & Unity Catalog](02-schemas-and-unity-catalog.md) | The catalog.schema.table namespace, creating tables, grants, deterministic sample data |
| 03 | [AI/BI Dashboards](03-ai-bi-dashboards.md) | Datasets, widgets, drafts vs published, the .lvdash.json format, deep links |
| 04 | [Databricks Apps](04-databricks-apps.md) | Hosting Streamlit apps, app.yaml, OAuth, the deploy lifecycle, external hosting lessons |
| 05 | [Lakebase Postgres](05-lakebase-postgres.md) | Managed Postgres inside Databricks: projects, branches, endpoints, OAuth credentials |
| 06 | [Genie, the AI Assistant](06-genie-the-ai-assistant.md) | What Genie did for this project and how to work with an AI assistant effectively |

Read them in order for a guided tour, or jump to whichever topic you need. Each note explains the concept first, then shows exactly what I did with it in this project.

## Quick glossary

* **Workspace** — your Databricks environment: notebooks, data, dashboards, apps, compute.
* **Unity Catalog (UC)** — the governance layer; organizes everything as `catalog.schema.table`.
* **SQL warehouse** — serverless compute for SQL queries and dashboards.
* **AI/BI dashboard** — dashboards built on datasets (SQL), stored as `.lvdash.json`.
* **Databricks App** — a web app (e.g. Streamlit) hosted inside the workspace with auth handled for you.
* **Lakebase** — managed Postgres (OLTP) databases that live next to your lakehouse (OLAP) data.
* **Genie** — Databricks' AI assistant; writes and runs code, creates assets, manages Git, explains things.
* **Service principal** — a machine identity (like a bot user) that apps and jobs authenticate as.
* **OAuth secret** — a credential for a service principal; write-only — you generate it, you can never view it again.
