# 06 · Genie — the AI Assistant

(Full disclosure, written by Genie itself at the author's request. The opinions are still accurate.)

## What Genie is

**Genie** is the AI assistant woven through Databricks. The flavors that mattered to me:

* **Genie Code** — the developer assistant in notebooks, queries, dashboards, and Apps pages. It reads and writes your assets, runs code, executes SQL, manages Git, and inspects live state (app status, logs, service principals) — not just a chat window that suggests code.
* **Genie agents (AI/BI data rooms)** — natural-language Q&A over governed tables for business users.
* **AI-assisted authoring** — e.g. building dashboard widgets from a description.

The difference from a generic chatbot: Genie is *grounded in your workspace*. It can see your tables, run your queries, and change your files — with permission gates on anything risky.

## What Genie did in this project

In one day, from plain-English requests:

1. Wrote and ran the **Sample Table Generation** notebook — 50 deterministic PySpark customers.
2. Created the Unity Catalog table and exported it to CSV.
3. Built the **Sample Customers Overview** AI/BI dashboard.
4. Scaffolded and deployed the **clv-manager** Streamlit app — including wiring it to the SQL warehouse, Lakebase Postgres, and the dashboard.
5. Populated `clv.customer_clv` with the app's exact CLV logic (300 rows).
6. Cloned my GitHub repo into the workspace, resolved the Git credential/app-installation issues, and pushed every asset — plus wrote this repo's README.
7. On request: edited the README (renamed "Screenshots" to "Views"), diagnosed a failed Render deployment, looked up the app's service principal and OAuth endpoints, and wrote the very notes you're reading.

## What I learned about working with an AI assistant

* **Describe outcomes, not steps.** "Make a dashboard over this table showing X" beat giving instructions.
* **It reads before it writes.** Genie inspected the app, logs, and diffs before changing things — I could trust the edits more because of that.
* **Ask for the reasoning.** When grants or OAuth secrets confused me, the explanation was more durable than the fix.
* **Confirm dangerous things explicitly.** Generating credentials and pushing to Git always asked first. That's correct behavior, mildly annoying, still correct.
* **Some things are invisible by design.** OAuth secrets are write-only; Genie can't (and shouldn't) read them out — you generate new ones instead.
* **Memory is real.** Next-day sessions remembered the repo, the app, and the pending grants — no re-explaining.

## The honest verdict

I came in knowing roughly zero Databricks and ended the day with a working app, a dashboard, a mirrored database, and a public repo documenting all of it. Genie handled the boilerplate, the syntax, and the platform trivia; I handled the intent and the judgment calls. That division of labor is exactly what an AI assistant should be — and yes, I liked it a lot.
