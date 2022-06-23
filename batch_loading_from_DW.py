import os
import boto3
from src.utils import _down_load_file_s3_folder
from IAC.config import config
from pymongo import MongoClient
import sys
INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')
SECTION_S3 = 'Credential-AWS-S3'
SECTION_INFO_S3 = 'Info-AWS-S3'
SECTION_DOCMENTDB = 'Credential-AWS-documentDB'

def main():
    aws_s3_info = config(INI_FILE_PATH, SECTION_INFO_S3)
    aws_s3_config = config(INI_FILE_PATH, SECTION_S3)
    session = boto3.Session(**aws_s3_config)
    s3_resource = session.resource('s3')
    s3_bucket = s3_resource.Bucket(aws_s3_info['root_bucket'])
    dbUri = f"mongodb://{aws_documentdb_config['user']}:{aws_documentdb_config['password']}@{aws_documentdb_config['host']}:{aws_documentdb_config['port']}/?ssl=true&sslCAFile={aws_documentdb_config['ssl_ca_file']}&sslAllowInvalidHostnames={aws_documentdb_config['allow_invalid_host_name']}"
    client = MongoClient(dbUri, ssl_cert_reqs=ssl.CERT_NONE)
    mongodb = client[params['MONGODB']]
    mongocol = mongodb[f"{params['MONGOCOL_BASE']}{params['MONGOCOL_INDEX']}"]    
    aws_documentdb_config = config(INI_FILE_PATH, SECTION_DOCMENTDB)
    

if __name__ == "__main__":
    if (s3_resource is None):
        ## S3 connection. Because must wait a couple of second for ssh tunnel connecting local port to documentdb port via EC2.
        aws_s3_info = config(INI_FILE_PATH, SECTION_INFO_S3)
        aws_s3_config = config(INI_FILE_PATH, SECTION_S3)
        session = boto3.Session(**aws_s3_config)
        s3_resource = session.resource('s3')
        s3_bucket = s3_resource.Bucket(aws_s3_info['root_bucket'])
        # bucket.download_file('xray-images/0e88612bd294e249382b9e64d222cdf4_hflip.jpg', './temp/img.jpg')
        #_down_load_file_s3_folder(s3_bucket, '0e88612bd294e249382b9e64d222cdf4_hflip.jpg', 'xray-images', 'temp')
        #download_s3_folder(s3_resource, aws_s3_info['root_bucket'], aws_s3_info['xray_images_bucket'])
    #main()