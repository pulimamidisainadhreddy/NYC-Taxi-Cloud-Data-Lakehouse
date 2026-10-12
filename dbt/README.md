# dbt

The local target uses DuckDB and reads the locally produced Silver Parquet files.
The `athena` target is for AWS deployment with `dbt-athena-community`.

Run locally:
```bash
dbt deps --profiles-dir .
dbt build --profiles-dir .
```

Run in AWS:
```bash
dbt build --target athena --profiles-dir .
```

Provide Athena/S3 settings through environment variables.
