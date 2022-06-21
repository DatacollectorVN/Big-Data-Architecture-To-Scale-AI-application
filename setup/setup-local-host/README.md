# Chest X-ray V3
## Setting up in local host
In your local host, we use Airflow for management workflow.

### 1. Create virtual environment and downloading Airflow
- Create new evironment.
```bash
conda create -n chestxrayv3-airflow python=3.8 -y
conda activate chestxrayv3-airflow
```

- Install Airflow. In this example, we install airflow with version 2.2.3.
```bash
pip install apache-airflow==2.2.3 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-3.8.txt"
```

*Note:* the constraint of Airflow with syntx `https://raw.githubusercontent.com/apache/airflow/constraints-<Airflow_version>/constraints-<Python_version>.txt`
### Setup Airflow (MacOS)
We setup the local host in MacOS (M1), might be it can be correct with Linux OS.

- Get Airflow Home
```bash
mkdir airflow
export AIRFLOW_HOME=~/<path_of_project>/airflow
echo $AIRFLOW_HOME
```

*Note:* If you use other termial the path variable is not saved.

- Create user
```bash
airflow users create --username admin --password admin --firstname <first_name> --lastname <last_name> --role Admin --email <email>
```

*Expected output:* in airflow/ directory have `logs` folder and `airflow.cfg`, `airflow.db` and `webserver_config.py` files.

- Add dags file into Airflow server
```bash
mkdir airflow/dags
cp airflow-dags/activate_aws_glue_job.py airflow/dags
```

- Run Airflow server
```
airflow standalone
```
*Note:* To running dag file successfully, you must setup AWS CLI in the next part. And after setup AWS CLI check the Amazon Glue Job in your account that must the same with the `<AWS_Glue_job_name>` in `airflow/dags/activate_aws_glue_job.py`

### Setup AWS CLI (MacOS)
- Installation:
Follow instruction [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for install for all user (using `sudo` command) or current user.

- Setup AWS CLI for AWS account:
```bash
aws configure
```
Then pass the key and region of your AWS account.

*Expected output:*
```bash
AWS Access Key ID [None]: <Your_access_key_id>
AWS Secret Access Key [None]: <your_seret_access_key>
Default region name [None]: <region>
Default output format [None]: json
```
*Note:* Choose the region that includes your Amazon services.

- If you use Amazon Glue Job, you can test the connection by show all jobs in your region:
```bash
aws glue list-jobs  
```
