from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="fetch_stock_hourly",
    default_args=default_args,
    description="Fetch and store stock data hourly",
    schedule_interval="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    def run_fetch():
        import sys
        import os

        # Make sure /opt/airflow/scripts is importable
        scripts_path = "/opt/airflow/scripts"
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)

        try:
            from fetch_and_store import main as fetch_main

            logging.info("Running fetch_main from DAG")
            fetch_main()
        except Exception as e:
            logging.error(f"Error in fetch_and_store: {e}")
            raise

    fetch_task = PythonOperator(
        task_id="fetch_and_store_task",
        python_callable=run_fetch,
    )
