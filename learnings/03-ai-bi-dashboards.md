# 03 · AI/BI Dashboards

## What they are

**AI/BI dashboards** are Databricks' native BI layer — analytics/visualization built straight into the workspace, no external tool needed. "AI" in the name is real: you can build and refine widgets with AI assistance, and dashboards can be embedded with Genie-powered Q&A over your data.

The model that clicked for me:

* A dashboard is a **canvas of widgets** (tables, bar charts, donut charts, KPI cards…).
* Each widget is powered by a **dataset — a SQL query** you author. Change the SQL, the widget re-renders.
* Widgets can be wired to **filters**, including dashboard-wide **global filters** that cross-filter every widget at once.
* You edit a **draft**, then **publish** — viewers see the published snapshot, you keep iterating on the draft.

## The one I built: "Sample Customers Overview"

Built over `workspace.default.sample_customers` (the 50-customer table from [02](02-schemas-and-unity-catalog.md)):

* **Paginated data table** of all 50 records — id, name, email, city, status, signup date, lifetime value (5 rows per page).
* **Record Count by City** — bar chart, roughly 6–7 records per city across the 8 cities.
* **Status Breakdown** — donut of the `active` / `inactive` / `pending` split.
* **Lifetime Value by City** — bar chart of total LTV per city (~$2,900–$3,900 each).

Genie built the widgets; I mostly reviewed what the data showed and adjusted. The whole thing took minutes, which is the point.

## Dashboards are files (mostly)

A dashboard is stored as a `.lvdash.json` file — a JSON serialization of its datasets, widgets, encodings, and layout. Two practical consequences I hit directly:

1. **You can export/import them.** This repo contains my dashboard as `dashboards/sample_customers_overview.json` — rename it to `.lvdash.json` and import it into any workspace to restore the dashboard.
2. **The workspace recognizes `.lvdash.json` as a live dashboard asset**, not a plain file — so copying one around as a file can be awkward (I stored the repo copy with a `.json` extension for exactly this reason).

## Wiring a dashboard to an app

Dashboards and Apps can deep-link to each other: my app has a button that opens the dashboard, and the dashboard carries a link back to the app. Each lives in the same workspace under the same governance (Unity Catalog permissions apply to the dashboard's datasets), so sharing is just a permission grant away.

## When to reach for one

* Fast, governed visual analytics over tables you already have — the 80% case.
* Genie-assisted authoring when you'd rather describe the chart than configure it.
* Embedding/BI-at-scale when paired with queries and alerts.
