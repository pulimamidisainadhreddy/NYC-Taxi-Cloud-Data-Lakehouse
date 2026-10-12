# Pipeline

1. Detect a new TLC month.
2. Ingest source Parquet into S3 Bronze.
3. Record run metadata.
4. Spark reads only the new month.
5. Validate schema and business rules.
6. Write invalid rows to rejected storage.
7. Write partitioned Silver Parquet.
8. Expose Silver through Glue/Athena.
9. Run dbt staging, intermediate and mart models.
10. Run dbt tests.
11. Run Athena/Gold validation.
12. Publish Power BI-ready Gold tables.
13. Record pipeline metrics and status.

Incremental unit: one TLC source month. Successful months should not be silently reprocessed. Add an explicit backfill/reprocess path for corrections.
