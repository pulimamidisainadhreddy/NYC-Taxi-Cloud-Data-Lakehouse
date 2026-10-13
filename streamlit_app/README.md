# NYC Taxi Streamlit dashboard

This folder provides a **standalone, read-only, public portfolio dashboard** using four small CSV exports from the NYC Taxi Cloud Data Lakehouse. It does not require Spark, Airflow, a PostgreSQL gateway, or AWS services to stay online.

## How to run locally

From the **root of the GitHub repository**:

```powershell
python -m pip install -r streamlit_app/requirements.txt
python -m streamlit run streamlit_app/app.py
```

## Streamlit Community Cloud deployment

1. Upload the whole `streamlit_app/` directory to the existing GitHub repository on its `main` branch.
2. Visit <https://share.streamlit.io> and select **Create app** (or **New app**).
3. Select repository `pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse` and branch `main`.
4. Set the **Main file path** to `streamlit_app/app.py`.
5. If there is a Python version selector, choose Python 3.11.
6. Deploy. Confirm all three dashboard pages and sidebar filters load.

## CSVs included

- `data/mart_daily_trip_metrics.csv` — dates and daily KPIs.
- `data/mart_hourly_trip_metrics.csv` — hourly KPIs (whole dataset, not date-aware).
- `data/mart_payment_analysis.csv` — payment totals (whole dataset, not date-aware).
- `data/mart_zone_performance.csv` — pickup-location totals (whole dataset, not date-aware).

**Aggregated exports do not allow payment-by-date, zone-by-date, or payment-by-zone interactions.** The Streamlit application does not pretend to make those cross-filtered aggregations. For exact cross-filtering, export lower-grain data with the needed combinations of dimensions.

## Adding pipeline metrics later (optional)

Save these CSV exports in the same data directory:

- `latest_metrics.csv`: `input_records,output_records,rejected_records,duplicate_records,processing_time_seconds,recorded_at`
- `pipeline_runs.csv`: `pipeline_status,start_date` (more fields are fine)

When both files exist, the app will display their last rows as snapshot KPI cards. Otherwise, it clearly labels the existing Power BI snapshot as a manual reference, not live data.

## Privacy and publishing

The GitHub repository is public. Review all CSVs for data you are allowed to share; never commit credentials, passwords, or private customer records. This demonstration uses aggregated public-transport data. Do not publish raw large datasets or database secrets.
