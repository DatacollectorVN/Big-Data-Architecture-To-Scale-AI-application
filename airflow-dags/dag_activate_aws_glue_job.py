from asyncio import tasks
from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
from airflow.models.baseoperator import chain
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.subdag import SubDagOperator
from airflow.operators.python_operator import PythonOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago
import yaml
import os

FILE_INFER_CONFIG = os.path.join("airflow", "dags", "config_airflow.yaml")
with open(FILE_INFER_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

JOBS = params['AWS_GLUE_JOBS_NAME']
DEFAULT_ARGS = {
    'owner': 'Nathan Ngo',
    'start_date': days_ago(0),
    'email': ['datacollectoriu@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
def run_ETL():
    print(os.getcwd())

with DAG(
    dag_id='activate-job',
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(minutes=15),
    schedule_interval='*/5 * * * *',
    #schedule_interval = timedelta(days=1)
) as dag:
    begin = DummyOperator(task_id="begin")

    end = DummyOperator(task_id="end")

    load_to_s3 = BashOperator(
            task_id = JOBS[0],
            bash_command=f'aws glue start-job-run --job-name {JOBS[0]}'
        )
        
chain(
    begin, 
    load_to_s3,
    end
)