# Troubleshooting

### S3 AccessDenied
Check the runtime IAM role and bucket policy.

### Athena table not found
Check the Glue database/table and S3 location.

### dbt authentication error
Check the Athena target and runtime AWS credentials.

### Spark input not found
Check the source path and file permissions.

### Airflow task failure
Read the task log before rerunning. Do not hide exceptions with broad error handling.

### Local Docker problem
```bash
docker compose ps
docker compose logs <service>
docker compose down
docker compose up -d --build
```
