from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.models.baseoperator import chain
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import yaml

# get airflow variable
tmpl_search_path = Variable.get("BASE_PATH")

# read configure file. Based on `BASE_PATH` airflow variable.
FILE_INFER_CONFIG = "config_airflow.yaml"
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
with DAG(
    dag_id='activate-job',
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(minutes=7),
    schedule_interval='*/5 * * * *',
    template_searchpath=tmpl_search_path
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