# 01 · The Databricks Workspace

## What a workspace is

A **Databricks workspace** is your entire cloud environment for data work: a web UI where your notebooks, SQL queries, dashboards, apps, data catalogs, jobs, and Git repos all live together. Instead of stitching together a database + a BI tool + an app server + a Git host, you get all of them in one place with one login and one permission system.

The workspace URL looks like:

```
https://dbc-xxxxxxxx.cloud.databricks.com/?o=7474658865741961
```

The `o=` parameter is the **workspace ID** — it also shows up in app URLs and API calls. Everything I did in this project happened inside one workspace.

## What lives inside

* **Notebooks** — interactive code documents (`.ipynb`) mixing Python/SQL/Markdown, used for data prep and analysis. My *Sample Table Generation* notebook created the 50-customer demo table.
* **Queries** — saved SQL files (`.dbquery.ipynb` in your home folder) you can run against a SQL warehouse.
* **AI/BI dashboards** — visual analytics, stored as `.lvdash.json`. → [03](03-ai-bi-dashboards.md)
* **Apps** — hosted web apps (Streamlit etc.) with source files right in the workspace. → [04](04-databricks-apps.md)
* **Catalogs / schemas / tables** — your data, governed by Unity Catalog. → [02](02-schemas-and-unity-catalog.md)
* **Jobs & pipelines** — scheduled and automated data work.
* **Git folders (repos)** — clones of GitHub repos you can pull/push to straight from the workspace UI. This very repo lives at `/Users/<me>/clv-manager-repo` in my workspace, and everything in it was committed and pushed from there.

Your personal area is a home folder like `/Workspace/Users/<your-email>/` — notebooks, queries, files, and app source all default there.

## Compute: the part that runs your code

This was the biggest mental shift for me. Code doesn't run "in the browser" — it runs on **compute** attached to the workspace:

* **Serverless compute** — spins up automatically when you run a cell; no cluster to configure or wait for. This is what my notebooks used.
* **All-purpose clusters** — traditional shared Spark clusters; you pick the size and manage them.
* **SQL warehouses** — compute for SQL: queries, dashboards, and apps querying data. Mine is `/sql/1.0/warehouses/<warehouse-id>` — that path is what apps use to connect (`SQL_WAREHOUSE_HTTP_PATH`).

## What I actually did

* Navigated the sidebar (Workspace, Catalog, Dashboards, Apps, Compute) — everything is searchable from the top bar.
* Ran notebook cells on serverless compute without ever creating a cluster.
* Connected my GitHub account (workspace credential) and used a Git folder as the push target for the whole project.
* Opened the Apps page to manage and deploy the `clv-manager` app.

## Things that surprised me

* Workspaces are cheap to leave idle — serverless only bills while code runs.
* A `.lvdash.json` file isn't just a file — the workspace recognizes it as a dashboard asset, which matters when you try to copy it around (learned while exporting my dashboard for this repo).
* Almost every asset has a numeric ID behind the scenes, and the UI deep links are built on them.
