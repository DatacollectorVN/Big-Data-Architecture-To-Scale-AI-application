# Chest-Xray-Version3
Complete building Docker for AI application on Google Cloud Platform (GCP) and data architecture on Amazon Web Service (AWS)

This repository has 3 branch:
- `master` branch for running Web application with Docker and management workflow with Airflow. That is used for setting Instance VM in GCP.
- `ec2` branch for setting up and running python script in Amazon EC2.
- `on-premise` branch for setting up and running bash script to batch loading data from on-premise server.

Please read the `setup` part for detail.

## 1. Introduction
### 1.1. Scope of project
Deep learning (DL) applications are growing and being widely applied in many industries. One of the most important tasks in DL application is deploying DL models to productions besides the algorithm research. This project aims to building back-end system on cloud and deploy DL model to production that the users can use directly. In this project use the DL model for Chest X-ray abnormalities detection and the users can interact via website application.

### 1.2. Background
The DL model are developed from May-2021 to Jan-2022 about researching and developing models for abnormalities detection in chest X-ray image. You can read 2 reports below for more understanding our methodologies so far:
- Deep learning model development by using Tensorflow-Keras - July-2021. Report [here](https://drive.google.com/file/d/1whMHzAWsTgvnt-X1aKH__u1ozSUBHV-k/view?usp=sharing) and public source code [here](https://github.com/DatacollectorVN/Chest-Xray-Version1).
- Deep learning model development by using Detectron2-Pytorch - Jan-2022. Report [here](https://drive.google.com/file/d/1E14d8vY4Fh3Nw_oVIaJAnfZ15fpj7vF7/view?usp=sharing) and public source code [here](https://github.com/DatacollectorVN/Chest-Xray-Version2)

### 1.3. Project ardchitecture
This our project have 2 main components:
- **Back-end** : Backend is the server-side of the website. It stores and arranges data, and also makes sure everything on the client-side of the website works fine. In our project, the backend must have the special part that is Deep learning model operation. So our backend has 2 parts, “DL model on cloud” and “Database system”. With backend operation, we used Python language and Django framework for building.
- **Front-end** : The part of a website that the user interacts with directly is termed the front end. It is also referred to as the ‘client side’ of the application. With frontend operation, we used Python with Streamlit. In the future, we will use 3 languages: HTML, CSS, JavaScript and ReactJS framework for building.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/introduction_fig1.png?raw=true)

*Note:* In this repository, we mainly focus on building **Back-end** architecture. 

## 2. Back-end architecture
The figure below shows the back-end architecture of project where we built data pipeline for data lake, data warehouse and data mart. In the backend architecture, it consist 4 components and 5 processes.

![plot](https://github.com/DatacollectorVN/Chest-Xray-Version3/blob/master/public-imgs/introduction_fig2.png?raw=true)

The components:
- **Application**: It is the web application of project that end-user can interact directly.
- **Data lake:** A data lake is a centralized repository designed to store, process, and secure large amounts of structured, semistructured, and unstructured data. It can store data in its native format and process any variety of it, ignoring size limits. In this project built data lake in AWS and used 2 services (Amazon RDS and Amazon S3).
- **Data warehouse**: A data warehouse is a type of data management system that is designed to enable and support business intelligence (BI) activities, especially analytics. Data warehouses are solely intended to perform queries and analysis and often contain large amounts of historical data. The data warehouse of project used Amazon DocumentDB
- **Data mart**: A data mart is a simple form of data warehouse focused on a single subject or line of business. With a data mart, teams can access data and gain insights faster, because they don’t have to spend time searching within a more complex data warehouse or manually aggregating data from different sources. The data mart of project that is built on on-premise server.

The processes:
- **Stage 1: Docker container**. The container include the graphic user interface (GUI), AI models and the developed environment. Total size of this container is approximate 7GB.
- **Stage 2: Extract and load**. This stage use for extract the data from application (x-ray images and meta data) and load it into data lake.
- **Stage 3: ETL for backup data**. ETL refers to Extract, Transform, and Load commonly used in the field of data engineering. This stage is used to load data from Amazon RDS to Amazon S3 for future backup because storage and management are more expensive than storage in Amazon S3 and the price depends on the total amount of data storage , so it's sometimes recommended to delete the data in Amazon RDS and back it up to Amazon S3.
- **Stage 4: ETL for transforming data to data warehouse**. The data in Amazon RDS is relational data and data in Amazon DocumentDB is non-relational data with document format. Therefore, we must transform data to correct format after loading into Amazon DocumentDB.
- **Stage 5: Batch loading to data mart**. The data is stored in cloud. To use that data, we must transform the organized data to the data format for specific requirement. In this case, we transform and loading the annotations with COCO format and xray images in data mart.

Read [here](https://github.com/DatacollectorVN/Chest-Xray-Version3/tree/master/back-end-detail) for more detail each stage.