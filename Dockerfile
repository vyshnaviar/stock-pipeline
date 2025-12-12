# Base Airflow image
FROM apache/airflow:2.7.1-python3.11

# Install PostgreSQL client (needed for pg_isready)
USER root
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python dependencies used by your DAG/script
RUN pip install --no-cache-dir \
    yfinance \
    pandas \
    psycopg2-binary

# (Optional) If you ever decide not to use volumes:
# COPY ./airflow/dags /opt/airflow/dags
# COPY ./scripts /opt/airflow/scripts
