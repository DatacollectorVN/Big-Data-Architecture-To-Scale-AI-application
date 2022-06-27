# Chest-Xray-Version3

The figure below illustrates our back-end architecture that contains 5 processes.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/introduction_fig2.png?raw=true)


## Stage 1 - Docker Container
The Figure illustrates the process for building container in GCP from Docker file in Github. 


![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig1.png?raw=true)

The container consists the GUI that is website application and AI model that is RetinaNet model with [Detectron2](https://github.com/facebookresearch/detectron2). In the future, we will split 2 containers with one is GUI and the other is AI model.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig2.png?raw=true)
## Stage 2 - Extract and Load
This stage extract the data from application (x-ray image and meta data) and load it into Data lake with x-ray image is loaded to Amazon S3 and meta data are loaded to Amazon RDS.

In the Figure displays how data from application is transformed and loaded to data lake (Amazon
RDS and Amazon S3). Amazon RDS is a web service that makes it easier to set up, operate, and scale a relational database in the AWS Cloud. It provides
cost-efficient, resizable capacity for an industry-standard relational database and manages common
database administration tasks. Amazon S3 is an object storage service that offers industry-leading scalability, data availability, security, and performance. Customers
of all sizes and industries can use Amazon S3 to store and protect any amount of data for a range
of use cases, such as data lakes, websites, mobile applications, backup and restore, archive, enterprise
applications, IoT devices, and big data analytics. Amazon S3 provides management features so that you
can optimize, organize, and configure access to your data to meet your specific business, organizational,
and compliance requirements. To make the application and data lake in AWS interoperable, Amazon
provided tool called Amazon SDK and Boto3 is Amazon SDK for python.
In Amazon RDS, we used MySQL engine and created x ray database with 3 relational tables - image, transaction and pred bounding box. We setup these relational tables in third normal form cfor improving the performance of query and scalability of database.


![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig3.png?raw=true)

In Amazon RDS, we used MySQL engine and created x ray database with 3 relational tables -
image, transaction and pred bounding box. We setup these relational tables in third normal form
for improving the performance of query and scalability of database.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig4.png?raw=true)


## Stage 3 - ETL for backup data
Because the price for using Amazon RDS depend on the amount of data storage in server. Therefore,
we must clean the historical data in server and backup that to Amazon S3.

In Figure shows how we backup data to S3. We used AWS Glue for create a job to ETL data
from Amazon RDS to Amazon S3. AWS Glue is a fully managed ETL (extract, transform, and load)
service that makes it simple and cost-effective to categorize your data, clean it, enrich it, and move
it reliably between various data stores and data streams. AWS Glue consists of a central metadata
repository known as the AWS Glue Data Catalog, an ETL engine that automatically generates Python
or Scala code, and a flexible scheduler that handles dependency resolution, job monitoring, and retries.
AWS Glue is serverless, so there’s no infrastructure to set up or manage. In the AWS Glue Job
used PySpark for processing the Big Data. Let imagine that our project is used for many
used and receive many request from application so that enlarge our database and complex processing.
Therefore, we deploy AWS Glue Job by PySpark for processing. During ETL process the data must
to convert to DynamicFrame type, so when load it into Amazon S3 we must to save it into parquet
format with partion key is image id (that is the primary key in image relational table). And
we want this stage is automation and trigger after interval time (weekly), we used Apache Airflow to
schedule this stage. Airflow is a platform to programmatically author, schedule and monitor workflows.
Use Airflow to author workflows as Directed Acyclic Graphs (DAGs) of tasks. The Airflow scheduler
executes your tasks on an array of workers while following the specified dependencies.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig5.png?raw=true)

## Stage 4 - ETL for transforming data to data warehouse
In Figure below illustrates how we transform data from data lake to data warehouse. Although we can use Amazon Glue for ETL job. However, the Amazon Glue Job does not support efficiently the other packages of Python except PySpark, so it harms our transforming from SQL data format to No-SQL data foramt. To resolve this, we used a VM in EC2 with the same VPC of DocumentDB for executing the ETL job. We can trigger the Python scripts in EC2 by SSHClient and orchestrate by Airflow from local machine.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig6.png?raw=true)

And to connect with DocumentDB from local machine, we use SSH to connect with VM in EC2 and connect DocumentDB by mongoshell.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig7.png?raw=true)

## Stage 5 - Batch loading to data mart
Figure shows the ETL process from Amazon DocumentDB to save it in on-premise server. This process is batch loading mean that process a complex and large data, we used bash script file to run several python files. However, this stage occurs when the AI engineer run bash script file from local. To run bash script file from local, we apply SSH tunnel to connect local
port 27017 and remote local port 27017 in cluster in EC2. SSH tunneling, or SSH port forwarding,
is a method of transporting arbitrary data over an encrypted SSH connection. SSH tunnels allow
connections made to a local port (that is, to a port on your own desktop) to be forwarded to a remote
machine via a secure channel.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/back_end_detail_fig8.png?raw=true)
