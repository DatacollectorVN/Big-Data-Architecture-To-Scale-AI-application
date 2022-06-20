# Chest X-ray V3
## Setting up in local host
In your local host, we use Airflow for management workflow.

### Downloading and setup Airflow
- Create new evironment.
```bash
conda create -n chestxrayv3-airflow python=3.8 -y
conda activate chestxrayv3-airflow
```

- Install Airflow. In this example, we install airflow with version 2.2.3.
```bash
pip install apache-airflow==2.2.3 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-3.8.txt"
```

### Setup Airflow Home

### Setup AWS CLI
#### In MacOS M1
