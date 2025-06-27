from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
from scripts.sync_sqlite_to_datalake import (
    export_sqlite_to_csv,
    create_datalake_client,
    upload_files_to_datalake
)

# Parâmetros fixos (você pode externalizar via Variables ou Secrets do Airflow depois)
db_path = "/opt/airflow/data/db.sqlite"
export_dir = "/opt/airflow/data/exported_tables"

account_name = Variable.get("account_name")
sas_token = Variable.get("sas_token")
filesystem_name = Variable.get("filesystem_name")
landing_zone_path = Variable.get("landing_zone_path")
export_mode = Variable.get("export_mode")
upload_mode = Variable.get("upload_mode")

default_args = {
    "start_date": datetime(2024, 1, 1)
}

with DAG(
    dag_id="sqlite_to_datalake",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["sqlite", "azure", "datalake"]
) as dag:

    def export_task():
        export_sqlite_to_csv(db_path, export_dir, export_mode)

    def upload_task():
        client = create_datalake_client(account_name, sas_token, filesystem_name)
        upload_files_to_datalake(export_dir, landing_zone_path, client, upload_mode)

    t1 = PythonOperator(
        task_id="export_sqlite_to_csv",
        python_callable=export_task,
    )

    t2 = PythonOperator(
        task_id="upload_to_datalake",
        python_callable=upload_task,
    )

    t1 >> t2
