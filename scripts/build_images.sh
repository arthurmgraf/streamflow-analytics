#!/usr/bin/env bash
# Build all StreamFlow Docker images
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG="${1:-latest}"

echo "=== Building streamflow/pyflink:${TAG} ==="
docker build -t "streamflow/pyflink:${TAG}" -f "$PROJECT_DIR/docker/flink/Dockerfile" "$PROJECT_DIR"

echo "=== Building streamflow/generator:${TAG} ==="
docker build -t "streamflow/generator:${TAG}" -f "$PROJECT_DIR/docker/generator/Dockerfile" "$PROJECT_DIR"

echo "=== Building streamflow/airflow-dbt:${TAG} ==="
docker build -t "streamflow/airflow-dbt:${TAG}" -f "$PROJECT_DIR/docker/airflow/Dockerfile" "$PROJECT_DIR"

echo ""
echo "All images built. To import to K3s: ./scripts/import_images.sh ${TAG}"
