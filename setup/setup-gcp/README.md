# Chest-Xray-Version3


# Setting up Google Cloud Platform (GCP)
In GCP, we setup a virtual machine (VM) for running our web application.

## Setup and configure VM Instance
### Step 1: Create VM Instance
- Choose `Virtual machine --> VM instances` then click `CREATE INSTANCE`. 
- When setup new instance for this project, please select at least `Machine type` is `e2 - medium (2 vCPU, 4GB memory)`.
- Click `CHANGE` button in `Boot disk` and choose `Container Optimized OS` of `Operating system` for running Docker and `50GB` of `Size` cause our Docker image and container have approaximate 7GB.
- Tick `Allow HTTP traffic` and `Allow HTTPS traffic` in `FireWall`.
- Then create VM Instance..

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

## Run Docker in VM Instance
- Click `SSH` to connect VM Instance via CLI in website.
- Clone this repository and configure 3 sections (`Credential-AWS-RDS-MySQL`, `Credential-AWS-S3`, `Info-AWS-S3`) in `IAC/credential_aws_sample.ini` 
```bash
git clone https://github.com/DatacollectorVN/Chest-Xray-Version3.git
cd Chest-Xray-Version3
nano AC/credential_aws_sample.ini
```

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
