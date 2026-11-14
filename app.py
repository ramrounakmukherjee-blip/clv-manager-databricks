"""
CLV Manager - a customer lifetime value management app for the team.

Users can view, filter, search, and track per-customer lifetime value
metrics, and jump straight to the connected Databricks dashboard.
"""

import os

import pandas as pd
import psycopg
import streamlit as st
from databricks.sdk import WorkspaceClient

from databricks.sdk.core import Config
from databricks.sql import connect

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# The AI/BI dashboard this app is connected to.
DASHBOARD_UUID = "01f1e00255a51ab68b084f6c014c9a40"

# Per-customer CLV aggregation from the shared bakehouse sample data.
CLV_QUERY = """
SELECT
    c.customerID,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email_address,
    c.country,
    c.continent,
    c.gender,
    COUNT(t.transactionID)            AS purchase_count,
    SUM(t.totalPrice)                AS lifetime_value,
    ROUND(AVG(t.totalPrice), 2)      AS avg_order_value,
    DATEDIFF(CURRENT_DATE(), MAX(t.dateTime)) AS days_since_last_purchase
FROM samples.bakehouse.sales_customers c
JOIN samples.bakehouse.sales_transactions t
    ON c.customerID = t.customerID
GROUP BY 1, 2, 3, 4, 5, 6
"""

# The Lakebase Postgres endpoint backing this app. LAKEBASE_ENDPOINT is
# injected from the app's `postgres` resource (declared in app.yaml);
# older env name and a literal fallback kept for robustness.
ENDPOINT_NAME = os.environ.get("LAKEBASE_ENDPOINT") or os.environ.get(
    "ENDPOINT_NAME", "projects/clv-app-db/branches/production/endpoints/primary"
)


# -----------------------------------------------------------------------------
# Data access
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner="Fetching customer data from Databricks...")
def load_clv_data() -> pd.DataFrame:
    """Run the CLV aggregation query against the app's SQL warehouse."""
    cfg = Config()
    host = cfg.host.replace("https://", "").replace("http://", "")
    with connect(
        server_hostname=host,
        http_path=os.environ["SQL_WAREHOUSE_HTTP_PATH"],
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    ) as connection, connection.cursor() as cursor:
        cursor.execute(CLV_QUERY)
        return cursor.fetchall_arrow().to_pandas()


# -----------------------------------------------------------------------------
# Lakebase (Postgres) bridge
# -----------------------------------------------------------------------------

_lakebase_client = None


def _get_workspace_client():
    """Lazily create a workspace client for OAuth token generation."""
    global _lakebase_client
    if _lakebase_client is None:
        _lakebase_client = WorkspaceClient()
    return _lakebase_client


class OAuthConnection(psycopg.Connection):
    """Postgres connection that generates a fresh OAuth token per connection."""

    @classmethod
    def connect(cls, conninfo="", **kwargs):
        credential = _get_workspace_client().postgres.generate_database_credential(
            endpoint=ENDPOINT_NAME
        )
        kwargs["password"] = credential.token
        return super().connect(conninfo, **kwargs)


def _lakebase_host() -> str:
    """Endpoint host, preferring the injected PGHOST."""
    host = os.environ.get("PGHOST")
    if not host:
        host = (
            _get_workspace_client()
            .postgres.get_endpoint(ENDPOINT_NAME)
            .status.hosts.host
        )
    return host


def _pg_conninfo() -> str:
    """Connection info with fallbacks when PG* env vars aren't injected."""
    user = (
        os.environ.get("PGUSER")
        or os.environ.get("DATABRICKS_CLIENT_ID")
        or _get_workspace_client().current_user.me().user_name
    )
    return (
        f"dbname={os.environ.get('PGDATABASE', 'databricks_postgres')} "
        f"user={user} host={_lakebase_host()} "
        f"port={os.environ.get('PGPORT', '5432')} "
        f"sslmode={os.environ.get('PGSSLMODE', 'require')}"
    )


UPSERT_CLV_SQL = """
INSERT INTO clv.customer_clv (
    customer_id, customer_name, email_address, country, continent, gender,
    clv_tier, purchase_count, lifetime_value, avg_order_value,
    days_since_last_purchase, synced_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (customer_id) DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    email_address = EXCLUDED.email_address,
    country = EXCLUDED.country,
    continent = EXCLUDED.continent,
    gender = EXCLUDED.gender,
    clv_tier = EXCLUDED.clv_tier,
    purchase_count = EXCLUDED.purchase_count,
    lifetime_value = EXCLUDED.lifetime_value,
    avg_order_value = EXCLUDED.avg_order_value,
    days_since_last_purchase = EXCLUDED.days_since_last_purchase,
    synced_at = now()
"""


@st.cache_data(ttl=600, show_spinner="Mirroring CLV metrics into Lakebase...")
def sync_clv_to_lakebase(df: pd.DataFrame) -> dict:
    """Mirror the computed CLV metrics into the Lakebase Postgres database."""
    try:
        rows = list(
            zip(
                df["customerID"].tolist(),
                df["customer_name"].tolist(),
                df["email_address"].tolist(),
                df["country"].tolist(),
                df["continent"].tolist(),
                df["gender"].tolist(),
                df["clv_tier"].tolist(),
                df["purchase_count"].tolist(),
                [float(v) for v in df["lifetime_value"].tolist()],
                [float(v) for v in df["avg_order_value"].tolist()],
                df["days_since_last_purchase"].tolist(),
            )
        )
        with OAuthConnection.connect(_pg_conninfo()) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE SCHEMA IF NOT EXISTS clv")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS clv.customer_clv (
                        customer_id BIGINT PRIMARY KEY,
                        customer_name TEXT,
                        email_address TEXT,
                        country TEXT,
                        continent TEXT,
                        gender TEXT,
                        clv_tier TEXT,
                        purchase_count BIGINT,
                        lifetime_value DOUBLE PRECISION,
                        avg_order_value DOUBLE PRECISION,
                        days_since_last_purchase INT,
                        synced_at TIMESTAMPTZ
                    )
                    """
                )
                cur.executemany(UPSERT_CLV_SQL, rows)
                cur.execute(
                    "SELECT count(*), max(synced_at) FROM clv.customer_clv"
                )
                count, last_sync = cur.fetchone()
            conn.commit()
        return {"ok": True, "rows": count, "last_sync": str(last_sync)}
    except Exception as exc:  # keep the app usable if the bridge is down
        return {"ok": False, "error": str(exc)}


def read_lakebase_preview(limit: int = 10) -> pd.DataFrame:
    """Read back a sample of the mirrored CLV data from Lakebase Postgres."""
    with OAuthConnection.connect(_pg_conninfo()) as conn:
        return pd.read_sql(
            f"SELECT customer_name, clv_tier, lifetime_value, "
            f"purchase_count, synced_at FROM clv.customer_clv "
            f"ORDER BY lifetime_value DESC LIMIT {int(limit)}",
            conn,
        )


def assign_clv_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Segment customers into High / Medium / Low value tiers by quartile."""
    df = df.copy()
    q25 = df["lifetime_value"].quantile(0.25)
    q75 = df["lifetime_value"].quantile(0.75)

    def tier(value: float) -> str:
        if value >= q75:
            return "High"
        if value >= q25:
            return "Medium"
        return "Low"

    df["clv_tier"] = df["lifetime_value"].apply(tier)
    return df


def dashboard_url() -> str:
    """Deep link to the connected AI/BI dashboard."""
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    return f"{host}/dashboardsv3/{DASHBOARD_UUID}"


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

st.set_page_config(page_title="CLV Manager", page_icon="💰", layout="wide")

st.title("💰 Customer Lifetime Value Manager")
st.caption(
    "View, filter, and track customer lifetime value across the team. "
    "Data source: samples.bakehouse (customers + transactions)."
)

url = dashboard_url()
st.link_button(
    "📊 Open connected dashboard: Sample Customers Overview",
    url,
    help="Opens the AI/BI dashboard this app is connected to.",
    type="primary",
)

# Load and segment the data.
full_df = assign_clv_tier(load_clv_data())

# Mirror the computed CLV metrics into the connected Lakebase Postgres
# database, completing the table -> dashboard -> app -> Lakebase bridge.
lakebase_status = sync_clv_to_lakebase(full_df)

# ---- Sidebar filters --------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    continent = st.multiselect(
        "Continent",
        options=sorted(full_df["continent"].dropna().unique()),
        default=[],
    )
    countries = sorted(full_df["country"].dropna().unique())
    country = st.multiselect("Country", options=countries, default=[])
    gender = st.multiselect(
        "Gender", options=sorted(full_df["gender"].dropna().unique()), default=[]
    )
    tier = st.multiselect(
        "CLV tier", options=["High", "Medium", "Low"], default=[]
    )
    min_value, max_value = int(full_df["lifetime_value"].min()), int(
        full_df["lifetime_value"].max()
    )
    clv_range = st.slider(
        "Lifetime value range", min_value=min_value, max_value=max_value,
        value=(min_value, max_value),
    )
    min_purchases = st.number_input(
        "Minimum purchases", min_value=0, max_value=100, value=0, step=1
    )
    search = st.text_input(
        "Search customer name or email", "", placeholder="e.g. Kayla"
    )


# ---- Apply filters ----------------------------------------------------------
df = full_df.copy()
if continent:
    df = df[df["continent"].isin(continent)]
if country:
    df = df[df["country"].isin(country)]
if gender:
    df = df[df["gender"].isin(gender)]
if tier:
    df = df[df["clv_tier"].isin(tier)]
df = df[
    df["lifetime_value"].between(clv_range[0], clv_range[1])
    & (df["purchase_count"] >= min_purchases)
]
if search.strip():
    needle = search.strip().lower()
    df = df[
        df["customer_name"].str.lower().str.contains(needle, na=False)
        | df["email_address"].str.lower().str.contains(needle, na=False)
    ]
df = df.sort_values("lifetime_value", ascending=False)

# ---- KPIs -------------------------------------------------------------------
if df.empty:
    st.warning("No customers match the current filters. Try widening them.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customers", f"{len(df):,}")
    col2.metric("Total lifetime value", f"${df['lifetime_value'].sum():,.0f}")
    col3.metric("Average lifetime value", f"${df['lifetime_value'].mean():,.0f}")
    col4.metric("Avg. orders per customer", f"{df['purchase_count'].mean():.1f}")

    # ---- Charts --------------------------------------------------------------
    st.subheader("Lifetime value by continent")
    by_continent = (
        df.groupby("continent", as_index=False)["lifetime_value"].sum()
        .sort_values("lifetime_value", ascending=False)
    )
    st.bar_chart(by_continent, x="continent", y="lifetime_value")

    left, right = st.columns(2)
    with left:
        st.subheader("Customers by CLV tier")
        tier_counts = df["clv_tier"].value_counts().rename_axis("tier").reset_index(name="customers")
        st.bar_chart(tier_counts, x="tier", y="customers")
    with right:
        st.subheader("Top 10 customers by lifetime value")
        st.bar_chart(df.head(10), x="customer_name", y="lifetime_value")

    # ---- Customer tracker ----------------------------------------------------
    st.subheader("Track a customer")
    customer_names = df["customer_name"].tolist()
    if customer_names:
        selected = st.selectbox("Select a customer", customer_names)
        row = df[df["customer_name"] == selected].iloc[0]
        t1, t2, t3, t4, t5 = st.columns(5)
        t1.metric("CLV tier", row["clv_tier"])
        t2.metric("Lifetime value", f"${row['lifetime_value']:,.0f}")
        t3.metric("Purchases", int(row["purchase_count"]))
        t4.metric("Avg. order value", f"${row['avg_order_value']:,.0f}")
        t5.metric("Days since last purchase", int(row["days_since_last_purchase"]))
        st.caption(f"✉️ {row['email_address']} · 🌍 {row['country']} ({row['continent']})")

    # ---- Detail table --------------------------------------------------------
    st.subheader("Customer lifetime value table")
    st.dataframe(
        df[
            [
                "customerID",
                "customer_name",
                "email_address",
                "country",
                "continent",
                "gender",
                "clv_tier",
                "purchase_count",
                "lifetime_value",
                "avg_order_value",
                "days_since_last_purchase",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered view (CSV)", csv, "clv_export.csv", "text/csv"
    )

st.subheader("Lakebase bridge")
if lakebase_status["ok"]:
    st.success(
        f"{lakebase_status['rows']:,} customer CLV records mirrored into the "
        f"**clv-app-db** Postgres database (`clv.customer_clv`) - "
        f"last sync {lakebase_status['last_sync']}"
    )
    with st.expander("Preview mirrored data in Lakebase Postgres"):
        st.dataframe(
            read_lakebase_preview(10),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.warning(f"Lakebase sync skipped: {lakebase_status['error']}")

st.divider()
st.markdown(
    f"ℹ️ This app is connected to the **Sample Customers Overview** "
    f"[dashboard]({url}). Build it out with CLV widgets to share deeper "
    "visualizations with the team."
)
