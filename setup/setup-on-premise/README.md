# Chest X-ray V3
## Setting up in on-premise server
Setup on-premise server for loading and transforming all data that were recorded in DocumentDB and correspoding images in S3. That loaded data is COCO format that is standard dataset format for object detection tasks in computer vision.

Follow instructions below to running batch loading from DW:
- Clone this repository with `on-premise` branch.
```bash
git clone -b on-premise --single-branch https://github.com/DatacollectorVN/Chest-Xray-Version3.git
```
- Install and setup Miniconda.
```bash
sudo wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

- Create virual environment.
```bash
cd Chest-Xray-Version3
pip install -r requirements_on_premise.txt
```
- Change the value in configuration with suitable values.
```bash
nano config/ETL.yaml
nano IAC/credential_aws_sample.ini
```
*Note:* in `credential_aws_sample.ini` file just change 2 sections - `[Credential-AWS-EC2]` and `[Credential-AWS-documentDB]`.

- Run batch loading
```bash
bash run.sh
```
The `run.sh` execute 3 tasks. Firstly, load the configuation in `IAC/credential_aws_sample.ini`. Secondly, run ssh tunnel in the background for fowarding the local port to remote port in DocumentDB. Finally, Run the python file `batch_loading_from_DW.py`.