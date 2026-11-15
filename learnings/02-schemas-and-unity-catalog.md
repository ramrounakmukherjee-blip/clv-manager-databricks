# 02 · Schemas, Unity Catalog & Making a Table

## The three-level namespace

In Databricks, every data object is addressed as

```
catalog.schema.table
```

* **Catalog** — the top level (think "database" in the traditional sense). A workspace has one default catalog (mine is `workspace`) plus shared ones with sample data (`samples`).
* **Schema** — a grouping inside a catalog. The default schema is literally called `default` — fine for demos, but real projects create their own (I also got a `clv` schema in Lakebase Postgres).
* **Table** — the actual data. A **managed table** means Databricks stores both the data and the metadata; you just write rows.

Tables in this project:

* `workspace.default.sample_customers` — the 50-customer table I generated for the dashboard demo.
* `samples.bakehouse.sales_customers` and `samples.bakehouse.sales_transactions` — Databricks' shared sample data, the real input for the CLV app.
* `clv.customer_clv` — the Lakebase Postgres table the app mirrors its results into. → [05](05-lakebase-postgres.md)

## Generating deterministic sample data (the fun part)

I needed a small demo table, so I asked Genie to write a notebook (*Sample Table Generation*) that fabricates **50 customer records with PySpark** — reproducibly. The tricks that make it deterministic:

* `spark.range(50)` — 50 rows, numbered `0..49`.
* Hard-coded pools of first names, last names, and cities (Austin, Boston, Chicago, Denver, Miami, Seattle, Toronto, Pune).
* Index arithmetic instead of randomness: `F.element_at` + modulo math (`id % 20`, `id * 7 % 20`, `id * 3 % 8`, `id % 3`) picks names, cities, and a status of `active` / `inactive` / `pending`.
* `lifetime_value = ((id * 137) % 940) + 60` — every customer gets a different but stable LTV.
* `signup_date` offsets 0–90 days from a fixed base date; emails are `first.last@example.com`.

Because there's no RNG involved, **every re-run produces identical data** — great for demos and tests. It also uses native Spark expressions instead of Python UDFs, which keeps it fast.

The notebook ends by writing with overwrite mode, so re-running replaces the table instead of duplicating rows.

## Unity Catalog: why it exists

**Unity Catalog (UC)** is Databricks' governance layer. It's not just naming — it's where permissions, lineage, and data discovery live:

* **Permissions are on the objects** — users and service principals get `SELECT`, `INSERT`, `USAGE` etc. on catalogs, schemas, tables.
* **Discovery** — you can search all tables, see their columns, and query `information_schema` to find things.
* **Everything is one system** — the dashboard, the app, and even Lakebase Postgres all talk to the same catalog.

## Grants: the lesson I learned the hard way

Apps authenticate as their own **service principal** — a machine identity. That identity needs explicit grants on anything it touches. My app could *read* the sample data fine, but its writes to `clv.customer_clv` needed:

```sql
GRANT USAGE ON SCHEMA clv TO "<service-principal-client-id>";
GRANT SELECT, INSERT, UPDATE ON clv.customer_clv TO "<service-principal-client-id>";
```

Rule of thumb: **if a service principal can't do something, check its grants first** — identity is not enough, and "it works in my notebook" doesn't count because your notebook runs as *you*, not as the app.
