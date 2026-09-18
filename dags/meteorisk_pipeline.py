from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from script.extract_bronze import extraction
from script.clean_silver import transformation
from script.feature_gold import create_gold
from db.load import load_postgres

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="meteorisk_pipeline",
    default_args=default_args,
    description="Pipeline météo MétéoRisk",
    schedule="@daily",
    start_date=datetime(2026, 9, 17),
    catchup=False,
    max_active_runs=1,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_bronze",
        python_callable=extraction,
    )

    silver_task = PythonOperator(
        task_id="clean_silver",
        python_callable=transformation,
    )

    gold_task = PythonOperator(
        task_id="create_gold",
        python_callable=create_gold,
    )

    load_task = PythonOperator(
        task_id="load_postgres",
        python_callable=load_postgres,
    )

    extract_task >> silver_task >> gold_task >> load_task