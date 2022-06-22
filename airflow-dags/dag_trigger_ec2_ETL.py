import paramiko
from airflow import DAG
from datetime import timedelta
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
from airflow.models.baseoperator import chain
from airflow.operators.dummy import DummyOperator
# This makes scheduling easy
from airflow.models import Variable
from airflow.utils.dates import days_ago
import yaml
import os
from airflow.operators.python_operator import PythonOperator

FILE_INFER_CONFIG = os.path.join("airflow", "dags", "config_airflow.yaml")
with open(FILE_INFER_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

def run_ETL():
    key = paramiko.RSAKey.from_private_key_file(params['AWS_EC2_KEY_PAIR'])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect/ssh to an instance
    try:
        # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
        client.connect(hostname=params['AWS_EC2_HOSE_NAME'], username=params['AWS_EC2_USER'], pkey=key)

        # Execute a command(cmd) after connecting/ssh to an instance
        cmd = f'conda activate ec2 \n  cd {params["AWS_EC2_BASE_DIR"]} \n python {params["AWS_EC2_ETL_FILES"][0]}'
        stdin, stdout, stderr = client.exec_command(cmd)
        

    except Exception as e:
        print (e)

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
    dag_id='activate-ec2',
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(minutes=15),
    schedule_interval='*/5 * * * *',
    #schedule_interval = timedelta(days=1)
) as dag:
    begin = DummyOperator(task_id="begin")

    end = DummyOperator(task_id="end")

    activate_ETL_ec2 = PythonOperator(
            task_id = 'activate-ETL',
            python_callable=run_ETL
        )
        
chain(
    begin, 
    activate_ETL_ec2,
    end
)