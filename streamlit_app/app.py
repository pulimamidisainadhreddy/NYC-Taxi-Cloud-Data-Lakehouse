"""NYC Taxi Cloud Data Lakehouse: public, read-only portfolio dashboard.

Launch locally: streamlit run streamlit_app/app.py
Hosted datasets are four *aggregated* CSV exports, not a live database.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import PAYMENT_NAMES, date_filter, summary, validate_frame, verify_consistency, weighted_average


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
NAVY = "#0c2149"
BLUE = "#1685ec"
CYAN = "#13c4d8"
GREEN = "#087f5b"
GRAY = "#64748b"

st.set_page_config(
    page_title="NYC Taxi | Cloud Data Lakehouse",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #f6f9fd; }
    [data-testid="stSidebar"] { background: #0b244c; }
    [data-testid="stSidebar"] * { color: #eef6ff; }
    [data-testid="stSidebar"] input { color: #172554 !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #172554; }
    h1, h2, h3 { color: #0c2149; letter-spacing: -0.015em; }
    .dash-header {
       padding: 24px 28px; border-radius: 14px; margin-bottom: 16px;
       background: linear-gradient(105deg,#0b2248,#103b74);
       color: white;
    }
    .dash-header h1 { margin:0; color:white; font-size:1.85rem; }
    .dash-header p { margin:7px 0 0; color:#d7e9ff; font-size:0.95rem; }
    [data-testid="stMetric"] {
       background: white; border:1px solid #e4eaf5; padding: 16px;
       border-radius: 12px; box-shadow: 0 3px 14px rgba(30,55,95,.06);
    }
    [data-testid="stMetricValue"] { color: #0b3474; }
    .section-note { font-size: .87rem; color:#526477; padding: 6px 0 12px; }
    .snapshot { background:#eef6ff; padding:12px 16px; border-radius:10px; color:#17365b; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading analytics exports...")
def load_marts() -> dict[str, pd.DataFrame]:
    """Load small static mart exports from repository; no network/database required."""
    files = (
        "mart_daily_trip_metrics.csv",
        "mart_hourly_trip_metrics.csv",
        "mart_payment_analysis.csv",
        "mart_zone_performance.csv",
    )
    frames = {}
    for filename in files:
        file = DATA / filename
        if not file.exists():
            raise FileNotFoundError(f"Missing {file.name} in streamlit_app/data/")
        frame = pd.read_csv(file)
        validate_frame(frame, filename)
        frames[filename] = frame
    frames["mart_daily_trip_metrics.csv"]["pickup_date"] = pd.to_datetime(
        frames["mart_daily_trip_metrics.csv"]["pickup_date"], errors="raise"
    )
    frames["mart_payment_analysis.csv"]["payment_name"] = frames[
        "mart_payment_analysis.csv"
    ]["payment_type"].map(PAYMENT_NAMES).fillna("Other")
    frames["mart_zone_performance.csv"]["location_label"] = frames[
        "mart_zone_performance.csv"
    ]["pickup_location_id"].astype(str)
    return frames


try:
    marts = load_marts()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.stop()

daily = marts["mart_daily_trip_metrics.csv"].sort_values("pickup_date")
hourly = marts["mart_hourly_trip_metrics.csv"].sort_values("pickup_hour")
payments = marts["mart_payment_analysis.csv"].copy()
zones = marts["mart_zone_performance.csv"].copy()
consistent, counts = verify_consistency(marts)


def plot_style(fig: go.Figure, *, height: int = 345) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=10, t=45, b=35),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", color=NAVY, size=12),
        legend_title_text="",
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=False, title_text=None)
    fig.update_yaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False, title_text=None)
    return fig


def chart(fig: go.Figure, *, key: str) -> None:
    st.plotly_chart(plot_style(fig), use_container_width=True, key=key)


def metrics_trip_revenue(frame: pd.DataFrame, *, key: str) -> None:
    s = summary(frame)
    cols = st.columns(4, gap="medium")
    cols[0].metric("Total Trips", f"{s['trips']:,}")
    cols[1].metric("Total Revenue", f"${s['revenue']/1_000_000:,.2f}M")
    cols[2].metric("Avg Fare", f"${s['fare']:,.2f}")
    cols[3].metric("Avg Trip Duration", f"{weighted_average(frame, 'average_trip_duration'):,.2f} min")


st.sidebar.markdown("## 🚕 NYC Taxi Analytics")
page = st.sidebar.radio(
    "Dashboard pages",
    ("Executive Overview", "Trip Analysis", "Payments & Locations"),
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
min_date = daily.pickup_date.min().date()
max_date = daily.pickup_date.max().date()
chosen = st.sidebar.date_input(
    "Daily metrics date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Changes date-grained daily KPIs and charts only; payment and zone exports do not include dates.",
)
if not isinstance(chosen, (tuple, list)) or len(chosen) != 2:
    st.sidebar.info("Select both a start date and an end date.")
    st.stop()
start_date, end_date = chosen
if start_date > end_date:
    st.sidebar.error("Start date must come before end date.")
    st.stop()
filtered_daily = date_filter(daily, start_date, end_date)

payment_options = ["All"] + [name for name in PAYMENT_NAMES.values() if name in payments.payment_name.values]
selected_payment = st.sidebar.selectbox("Payment type", payment_options)
zone_options = ["All"] + sorted(zones.pickup_location_id.astype(int).tolist())
selected_zone = st.sidebar.selectbox("Pickup location ID", zone_options)
chosen_payments = payments if selected_payment == "All" else payments.loc[payments.payment_name == selected_payment]
chosen_zones = zones if selected_zone == "All" else zones.loc[zones.pickup_location_id == selected_zone]

st.sidebar.caption("Portfolio preview • CSV snapshots • no database connection")
st.sidebar.caption("Each filter affects only data that contains that dimension.")

st.markdown(
    f'<div class="dash-header"><h1>🚕 NYC Taxi Cloud Data Lakehouse</h1>'
    f'<p>{page}  |  January 2025 Taxi Analytics  |  Interactive Portfolio</p></div>',
    unsafe_allow_html=True,
)

if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption("Daily KPIs and trends use the selected date range.")
    if filtered_daily.empty:
        st.warning("No daily trips found for the selected dates.")
    else:
        metrics_trip_revenue(filtered_daily, key="overall")
        a, b = st.columns(2)
        with a:
            fig = px.area(
                filtered_daily, x="pickup_date", y="total_revenue",
                title="Daily Revenue ($)", color_discrete_sequence=[BLUE],
            )
            fig.update_traces(line=dict(width=2.5), fillcolor="rgba(22,133,236,0.14)")
            chart(fig, key="overview-revenue")
        with b:
            fig = px.bar(
                filtered_daily, x="pickup_date", y="total_trips",
                title="Trips by Day", color_discrete_sequence=[BLUE],
            )
            chart(fig, key="overview-daily-trips")
        a, b = st.columns(2)
        with a:
            fig = px.line(
                filtered_daily, x="pickup_date", y="average_trip_distance",
                title="Average Trip Distance (miles)", markers=True,
                color_discrete_sequence=[CYAN],
            )
            chart(fig, key="overview-distance")
        with b:
            fig = px.line(
                filtered_daily, x="pickup_date", y="average_trip_duration",
                title="Average Trip Duration (min)", markers=True,
                color_discrete_sequence=[BLUE],
            )
            chart(fig, key="overview-duration")
    st.subheader("Data quality checks")
    if consistent:
        st.success(f"All four marts reconcile to {next(iter(counts.values())):,} trips (full exported dataset).")
    else:
        st.warning(f"Different total trip counts across marts: {counts}")
    st.info("Daily date filtering does not filter hourly, payment, or pickup-location marts because those exports have no date column.")

elif page == "Trip Analysis":
    st.subheader("Trip Analysis")
    peak = hourly.loc[hourly.total_trips.idxmax()]
    a, b, c = st.columns(3)
    a.metric("Peak Hour", f"{int(peak.pickup_hour):02d}:00")
    b.metric("Trips at Peak Hour", f"{int(peak.total_trips):,}")
    c.metric("Average Distance (all hours)", f"{weighted_average(hourly, 'average_distance'):.2f} mi")
    st.caption("Hourly breakdown represents the complete exported dataset; it cannot be filtered by day using these CSV files.")
    fig = px.bar(hourly, x="pickup_hour", y="total_trips", title="Trip Demand by Hour", color_discrete_sequence=[BLUE])
    fig.update_xaxes(dtick=1)
    chart(fig, key="trip-hourly-demand")
    a, b = st.columns(2)
    with a:
        fig = px.line(
            hourly, x="pickup_hour", y="average_distance", markers=True,
            title="Average Distance by Hour (miles)", color_discrete_sequence=[CYAN],
        )
        fig.update_xaxes(dtick=2)
        chart(fig, key="trip-hourly-distance")
    with b:
        fig = px.line(
            hourly, x="pickup_hour", y="average_duration", markers=True,
            title="Average Duration by Hour (min)", color_discrete_sequence=[BLUE],
        )
        fig.update_xaxes(dtick=2)
        chart(fig, key="trip-hourly-duration")
    st.subheader("Selected Date Range")
    if filtered_daily.empty:
        st.info("No daily data for the selected date range.")
    else:
        st.metric("Trips in Date Range", f"{int(filtered_daily.total_trips.sum()):,}")
        fig = px.line(
            filtered_daily, x="pickup_date", y="total_trips", markers=True,
            title="Daily Trips — Selected Dates", color_discrete_sequence=[BLUE],
        )
        chart(fig, key="trip-selected-dates")

else:
    st.subheader("Payments & Locations")
    st.caption("Payment and pickup-location filters work independently because these datasets are already aggregated.")
    pay_summary = summary(chosen_payments)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Payment Trips", f"{pay_summary['trips']:,}")
    m2.metric("Payment Revenue", f"${pay_summary['revenue']/1_000_000:,.2f}M")
    m3.metric("Payment Avg Fare", f"${pay_summary['fare']:,.2f}")
    m4.metric("Pickup Location Trips", f"{int(chosen_zones.total_trips.sum()):,}")

    a, b = st.columns(2)
    with a:
        fig = px.pie(
            chosen_payments, names="payment_name", values="total_trips", hole=.60,
            title="Trip Share by Payment Type", color_discrete_sequence=[BLUE, NAVY, CYAN, "#74a9fa", "#818cf8", GRAY],
        )
        fig.update_traces(textposition="outside", textinfo="percent")
        chart(fig, key="payment-share")
    with b:
        fig = px.bar(
            chosen_payments.sort_values("total_revenue", ascending=False),
            x="payment_name", y="total_revenue", title="Revenue by Payment Type ($)",
            color_discrete_sequence=[BLUE],
        )
        chart(fig, key="payment-revenue")

    a, b = st.columns(2)
    with a:
        fig = px.bar(
            chosen_payments.sort_values("average_fare", ascending=False),
            x="payment_name", y="average_fare", title="Average Fare by Payment Type ($)",
            color_discrete_sequence=[CYAN],
        )
        chart(fig, key="payment-fares")
    with b:
        st.markdown("#### Payment breakdown")
        st.dataframe(
            chosen_payments[["payment_name", "total_trips", "total_revenue", "average_fare"]].rename(
                columns={"payment_name": "Payment", "total_trips": "Trips", "total_revenue": "Revenue ($)", "average_fare": "Avg fare ($)"}
            ),
            use_container_width=True, hide_index=True,
        )

    st.subheader("Top Pickup Locations")
    a, b = st.columns(2)
    with a:
        top = chosen_zones.nlargest(10, "total_revenue").sort_values("total_revenue")
        fig = px.bar(
            top, x="total_revenue", y="location_label", orientation="h",
            title="Top 10 Pickup Locations by Revenue ($)", color_discrete_sequence=[BLUE],
        )
        chart(fig, key="zone-top-revenue")
    with b:
        top = chosen_zones.nlargest(10, "total_trips").sort_values("total_trips")
        fig = px.bar(
            top, x="total_trips", y="location_label", orientation="h",
            title="Top 10 Pickup Locations by Trips", color_discrete_sequence=[CYAN],
        )
        chart(fig, key="zone-top-trips")

    st.subheader("Data Quality & Pipeline Metrics")
    metrics_path = DATA / "latest_metrics.csv"
    runs_path = DATA / "pipeline_runs.csv"
    if metrics_path.exists() and runs_path.exists():
        try:
            metrics_df = pd.read_csv(metrics_path)
            runs_df = pd.read_csv(runs_path)
            needed = {"input_records", "output_records", "rejected_records", "duplicate_records", "processing_time_seconds"}
            if metrics_df.empty or runs_df.empty or not needed.issubset(metrics_df.columns) or "pipeline_status" not in runs_df:
                st.warning("Pipeline CSVs exist but are empty or missing expected columns.")
            else:
                if "recorded_at" in metrics_df:
                    metrics_df = metrics_df.sort_values("recorded_at")
                if "start_date" in runs_df:
                    runs_df = runs_df.sort_values("start_date")
                m = metrics_df.iloc[-1]
                r = runs_df.iloc[-1]
                cols = st.columns(3)
                cols[0].metric("Input Records", f"{int(m.input_records):,}")
                cols[1].metric("Output Records", f"{int(m.output_records):,}")
                cols[2].metric("Rejected Records", f"{int(m.rejected_records):,}")
                cols = st.columns(3)
                cols[0].metric("Duplicate Records", f"{int(m.duplicate_records):,}")
                cols[1].metric("Pipeline Status", str(r.pipeline_status).upper())
                cols[2].metric("Processing Time", f"{float(m.processing_time_seconds):,.2f} sec")
                st.caption("Snapshot loaded from optional pipeline CSV exports; not a live database query.")
        except (ValueError, KeyError, pd.errors.ParserError) as exc:
            st.warning(f"Unable to render optional pipeline metrics: {exc}")
    else:
        st.markdown(
            '<div class="snapshot">📋 <b>Last recorded Power BI snapshot</b> '
            '(manual reference, not live): <b>3,475,226</b> input records • '
            '<b>3,330,663</b> output records • <b>144,563</b> rejected records • '
            '<b>0</b> duplicates • <b>SUCCESS</b> status. '
            'Upload latest_metrics.csv and pipeline_runs.csv later for data-backed pipeline cards.</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    "Data: aggregated exports from the NYC Taxi Cloud Data Lakehouse project. "
    "Static portfolio snapshot; filters only affect the dimensions present in each export. "
    "Original Power BI and pipeline remain unchanged."
)
