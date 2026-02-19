FROM apache/airflow:2.10.4-python3.12

USER root
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git libpq-dev && \
    rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    "astronomer-cosmos[dbt-postgres]" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt"

COPY --chown=airflow:root dbt/ /opt/airflow/dbt/
COPY --chown=airflow:root src/dags/ /opt/airflow/dags/
COPY --chown=airflow:root src/dags/common/ /opt/airflow/dags/common/
