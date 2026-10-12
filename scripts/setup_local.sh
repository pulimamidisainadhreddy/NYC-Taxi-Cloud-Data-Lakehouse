#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
mkdir -p data/sample logs local-lake
docker compose up -d --build
echo "Airflow: http://localhost:8080"
echo "MinIO:   http://localhost:9001"
echo "Spark:   http://localhost:8081"
