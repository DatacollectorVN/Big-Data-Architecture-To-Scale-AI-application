# Chest X-ray V3

# Setting up Amazon Web Service (AWS)
In AWS, we setup Data Lake (DL) and Data Warehouse (DW) for back-end.

In the figure back-end architecture below, we setup AWS for running 4 processes (from stage 2 to stage 5). We explained detail each process in [here](https://github.com/DatacollectorVN/Chest-Xray-Version3/tree/master/back-end-detail)

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/introduction_fig2.png?raw=true)

## 1. Set up for Stage 2 - Extract and Load

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig3.png?raw=true)

In the Stage 2, we used 2 Amazon tools in DL (Amazon RDS with MySQL engine and Amazon S3). The data move from our web applcation in GCP and be transformed and loaded into DW with Amazon RDS for meta data such as image file name, location storage in S3, transaction and offset value of predicted bounding boxes, ... and Amazon S3 for X-ray images.

### 1.1. Setup Amazon S3
To load data from outside into Amazon S3. Following our instructions.
- Click `Bucket --> Create Bucket` then untick `Block all public access`.
- After created bucket, choose it and `Permissions` and click `Edit` in `Bucket policy` tag.
- Then add the Json script below. *Note:* Replace the text in `< >` corresponding your configuration. Read [here](https://cloudaffaire.com/bucket-policy-in-s3/) for more understanding **Bucket policy**  
```bash
{
    "Version": "2012-10-17",
    "Id": "<id_name>",
    "Statement": [
        {
            "Sid": "ExampleStatement01",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket_name>/*",
                "arn:aws:s3:::<bucket_name>"
            ]
        }
    ]
}
```
- Click `Save` and you can see your bucket have warning `Public` in `Access`.
- Create `Folder` in your bucket for storing x-ray images.

### 1.2. Setup Amazon RDS
The purpose of Amazon RDS is storage about meta data in relational data format. In database server, we design a database schema with third normal form to improve the query process. Following our instructions:
- Click `Create database` and choose MySQL in `Engine type`.
- Create `Master username` and `password`. *Note:* Please remember your password.
- In the `Connectivity` tag. Choose the VPC and subnet group, ticks `yes` in `public access` and the `security group` choose `choose existing` and select exist security group that allow to connect Amazon RDS to MySQL workbench from local. If you do not create it yet, we guide it in next steps.
- Then click `Create database`.

If you do not add `security group` after create database, follow our steps:
- Choose VPC service then click `Security Group --> Create security group`. 
- Then choose VPC that corressponding to the VPC when you created Amazon RDS. 
- Click `Add rule` in `Inbound rules` then configure: `Type` : `All trafic` and `Source`: `Anywhere IPv4`.
- Then click `Create security group`.
- In your database of Amazon RDS, click `Modify` and choose `security group` that was just created.

Connect Amazon RDS with MySQL Workbench:
- Click `Database --> Manage Connection`. 
- Click `new` and add the endpoint of Amazon RDS to `Hostname` and type `Username` and `password` correspoding the `Master username` and `password` in Amazon RDS.
- Then click `Test Connection` and pray for it sucess 🥹.

Setup database and table in Amazon RDS via MySQL Workbench, after the connection Amaozn RDS with MySQL Workbench is sucessful, please follow our instructions:
- Connect Amazon RDS via MySQL Workbench.
- Add SQL script in `src/create_table_rds.sql` for setting up database and create relationship for each table.
- Note: you can add some sample data into 3 tables by add script in `src/add_sample_in_table_rds.sql`.

## 2. Set up for Stage 3 - ETL for backup data

### 2.1. ETL for backup data
Because this stage, we run Airflow server in GCP. Therefore, you must setup Airflow and AWS CLI in your VM Instance of GCP - read [here] after following our instructions:
- Setup S3 and RDS for connection (follow our instruction in previous part `1.2.Setup Amazon RDS`)
- Then create the folder in S3 for data backup. 
- Create AWS Glue Job: `Create job --> Spark script editor` then copy the content in `aws_glue_job/3.aws_glue_job_data_backup.py`.
into AWS Glue Job. *Note:* You must replace the text in `< >` to connect data from RDS to S3.

## 2. Set up for Stage 4 - ETL for transforming data to data warehouse
As show in the section of `back-end-detail` in [here](https://github.com/DatacollectorVN/Chest-Xray-Version3/tree/master/back-end-detail#stage-4---etl-for-transforming-data-to-data-warehouse). 
we used a VM in EC2 with the same VPC of DocumentDB for executing the ETL job. We can trigger the Python scripts in EC2 by SSHClient and orchestrate by Airflow from VM Instance in GCP.

This instruction guides to setup in Instance in EC2 and DocumentDB:
### 2.1. Setup EC2 and DocumentDB for connection.
Because the DocumentDB places in the private VPC, that just can be connected with the service that the same VPC. Therefore, to manipulate with it, we must use instance in EC2 as a bridge to work with DocumentDB from local. 

Fortunately, we found the detail instruction [here](https://docs.aws.amazon.com/documentdb/latest/developerguide/connect-ec2.html). You can follow up with this.

*Note:* The configuration of instance of EC2 and database of DocumentDB can be edited.

### 2.2. Setup virtual enviroment in instance of EC2
After you connect successfully with DocumentDB via EC2. Then you must to setup Python environment for running the ETL script that be executed by Airflow from GCP.

- Install and setup Miniconda.
```bash
sudo wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

- Create new evironment.
```bash
conda create -n ec2 python=3.8 -y
conda activate ec2
```

- Clone this repository with `ec2` branch.
```bash
git clone -b ec2 --single-branch https://github.com/DatacollectorVN/Chest-Xray-Version3.git
```

- Install dependecies.
```bash
cd Chest-Xray-Version3
pip install -r requirment_ec2.txt
```

- Change the value in configuration with suitable values.
```bash
nano IAC/credential_aws_sample.ini
nano config/ETL.yaml
```
- Change credential path in `ETL_data_to_DocumentDB.py`. Cause during test process, we use other credential without commint on Github.
```bash
nano ETL_data_to_DocumentDB.py
```
Then replace line 12 `INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')` to `INI_FILE_PATH = os.path.join('IAC', 'credential_aws_sample.ini')`.

- Testing.
```bash
python ETL_data_to_DocumentDB.py
```

*Expected output:* After run python script, check DocumentDB server that have loaded new records like `MONGODB` database, `MONGOCOL_BASE` with `MONGOCOL_INDEX` collection like your configuration in `config/ETL.yaml`.

- Testing with Aiflow from GCP. Open Airflow server and try to run the Airflow dag to trigger `ETL_data_to_DocumentDB.py`.
