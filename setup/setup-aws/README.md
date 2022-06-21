# Chest X-ray V3

# Setting up Amazon Web Service (AWS)
In AWS, we setup Data Lake (DL) and Data Warehouse (DW) for back-end.

In the figure back-end architecture below, we setup AWS for running 4 processes (from stage 2 to stage 5). We explained detail each process in [here](https://github.com/DatacollectorVN/Chest-Xray-Version3/tree/master/back-end-detail)

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/introduction_fig1.png?raw=true)

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

### 1.3. ETL for backup data
Because this stage, we run Airflow server in local machine. Therefore, you must setup Airflow and AWS CLI in your local machine - read [here] before following our instructions:
- Setup S3 and RDS for connection (follow our instruction in previous part `1.2.Setup Amazon RDS`)
- Then create the folder in S3 for data backup. 
- Create AWS Glue Job: `Create job --> Spark script editor` then copy the content in `aws_glue_job/3.aws_glue_job_data_backup.py`.
into AWS Glue Job. *Note:* You must replace the text in `< >`.