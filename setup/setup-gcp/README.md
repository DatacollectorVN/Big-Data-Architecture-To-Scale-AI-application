# Chest-Xray-Version3


# Setting up Google Cloud Platform (GCP)
In GCP, we setup a virtual machine (VM) for running our web application.

## 1. Setup and configure VM Instance for running web application (Docker)
### Step 1: Create VM Instance
- Choose `Virtual machine --> VM instances` then click `CREATE INSTANCE`. 
- When setup new instance for this project, please select at least `Machine type` is `e2 - medium (2 vCPU, 4GB memory)`.
- Click `CHANGE` button in `Boot disk` and choose `Container Optimized OS` of `Operating system` for running Docker and `50GB` of `Size` cause our Docker image and container have approaximate 7GB.
- Tick `Allow HTTP traffic` and `Allow HTTPS traffic` in `FireWall`.
- Then create VM Instance.

### Step 2: Create Firewall
Create firewall for access the VM Instance from outside VPC.
- Choose `VPC network --> Firewall` then click `CREATE FIREWALL RULE`. 
- Configure FIREWALL RULE for allowing all trafic. Choose `IPv4 ranges` of `Source Filter` and `0.0.0.0/0` of `Source IPv4 ranges`.
- Tick `Allow all` of `Protocols and ports`.

*Note:* Read [here](https://www.quora.com/What-does-0-0-0-0-0-mean-in-context-of-networking-IP-addressing-If-it-is-a-default-route-to-the-rest-where-exactly-does-this-%E2%80%9Crest%E2%80%9D-lie) for more understanding **IPv4 ranges** is **0.0.0.0/0**.

### Step 3: Add Firewall in VM Instance
- Choose the VM Instance that was created and click `EDIT`.
- In `Network tags`, type and select the Firewall name that jus have created. 
- Then click `SAVE`.

### Step 4: Run Docker in VM Instance
- Click `SSH` to connect VM Instance via CLI in website.
- Clone this repository wiht `master` branch and configure 3 sections (`Credential-AWS-RDS-MySQL`, `Credential-AWS-S3`, `Info-AWS-S3`) in `IAC/credential_aws_sample.ini` 
```bash
git clone -b master --single-branch https://github.com/DatacollectorVN/Chest-Xray-Version3.git
cd Chest-Xray-Version3
nano IAC/credential_aws_sample.ini
```
- Change credential path in `streamlit_inference.py`. Cause during test process, we use other credential without commint on Github.
```bash
nano streamlit_inference.py
```
Then replace line 22 `INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')` to `INI_FILE_PATH = os.path.join('IAC', 'credential_aws_sample.ini')`.

*Notes:* You must setup your AWS before running Docker. You also do not configure the `IAC/credential_aws_sample.ini`. It just connect and load data into your AWS. To prevent the error if don't connect AWS, you should comment the line `86-87` and `90-96` before running Docker.

- Create Docker image
```bash
docker build -f Dockerfile -t chestxrayv3 
```
- Then create and access Docker image 
```bash
docker run -p 8501:8501 chestxrayv3
```

*Expected output:*

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/setup_gcp_fig1.png?raw=true)

Then when you access website application via `http://34.168.110.196:8501`, you can interact directly with our application.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/setup_gcp_fig2.png?raw=true)

## 2. Setup and configure VM Instance for running workflow management (Apache Airflow)
### Step 1: Create VM Instance
Like the `Step 1` of part 1 above, but instead of creating `Container Optimized OS`, select `Ubuntu`

- Choose `Virtual machine --> VM instances` then click `CREATE INSTANCE`. 
- When setup new instance for this project, please select at least `Machine type` is `e2 - medium (2 vCPU, 4GB memory)`.
- Click `CHANGE` button in `Boot disk` and choose `Ubuntu` of `Operating system` and `10GB` of `Size`.
- Tick `Allow HTTP traffic`, `Allow HTTPS traffic` in `FireWall` and add the Firewall that was created in part 1 in the `Network tags`.
- Then create VM Instance.


### Step 2: Installing Miniconda
- Click `SSH` to connect VM Instance via CLI in website.
- Install and setup Miniconda.
```bash
sudo wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```
### Step 3: Create virtual environment and downloading Airflow
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

### Step 4: Setup Airflow
- Get Airflow Home (Optional). You can skip this step and use default Airflow Home `~/airflow`.
```bash
mkdir airflow
export AIRFLOW_HOME=~/<path_of_project>/airflow
echo $AIRFLOW_HOME
```
- Create user
```bash
airflow users create --username admin --password admin --firstname <first_name> --lastname <last_name> --role Admin --email <email>
```
*Expected output:* in airflow/ directory have `logs` folder and `airflow.cfg`, `airflow.db` and `webserver_config.py` files.

- Create dags folder in Airflow Home.
```bash
mkdir airflow/dags
```

### Step 5: Set Airflow Variable
Cause in the dag files, we setup to read the configuration and read the aws ec key pair file. Therefore, we must setup Airflow Variable and pass it into `template_searchpath` in dag setup. 

*Note:* If you do not really understand about Airflow, just follow our instruction with default value.

- Open Airflow Webserver
```bash
airflow webserver -p 8080
```
- Create Airflow Variable in `Airflow UI`
`Admin --> Variable` and create new vairable wih `key` is `BASE_PATH` and `value` is `/home/<user_name>/airflow/dags`. Cause later, we move the configuration file and key pair file into `~/airflow/dags`. 

*Note:* You can move it into other place.

### Step 5: Setbup and move materials into Airflow server
- Clone this repository with `master` branch.
```bash
git clone -b master --single-branch https://github.com/DatacollectorVN/Chest-Xray-Version3.git
```

- Install dependecies of airflow dags.
```bash
pip install -r Chest-Xray-Version3/requirements_airflow_dags.txt
```

- Move dag files and configuration into airflow server
```bash
mkidr ./airflow/dags
mkidr ./airflow/dags/IAC
cp Chest-Xray-Version3/airflow-dags/* ./airflow/dags/
```

- Change the value in configuration with suitable value
```bash
nano ./airflow/dags/config_airflow.yaml
```
*Note:* in `AWS_EC2_KEY_PAIR` add the value `./airflow/dags/IAC/<key_pair_file_name>`. And the other depends on your setting up in AWS.

- Upload your key pair file into VM Instances by clikc `Upload file` and move it to `~/airflow/dags/IAC/`.
```bash
chmod 400 ~/<key_pair_file_name>
mv ~/<key_pair_file_name> ./airflow/dags/IAC
```

### Step 6: Running Airlfow
We can running airflow with one command `airflow standalone` but when shutting down this service can get some troubles. Therefore we use other ways with open 2 terminal.

*Note:* If you do not use default value of Airflow Home, in the other terminal you must the set it again.
- First terminal, running Airflow webserver with port 8080.
```bash
airflow webserver -p 8080
```

- Second terminal, running Airflow scheduler
```bash
airflow scheduler
```

After all this step, now you can enjoy 😝.
