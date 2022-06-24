from calendar import c
import os
import boto3
from src.batch_loader import BatchLoaderCOCO
from IAC.config import config
from pymongo import MongoClient
import ssl
import yaml

INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')
SECTION_S3 = 'Credential-AWS-S3'
SECTION_INFO_S3 = 'Info-AWS-S3'
SECTION_DOCMENTDB = 'Credential-AWS-documentDB'

FILE_ETL_CONFIG = os.path.join("config", "ETL.yaml")
with open(FILE_ETL_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

def main():
    # Connect to S3
    aws_s3_config = config(INI_FILE_PATH, SECTION_S3)
    session = boto3.Session(**aws_s3_config)
    s3_resource = session.resource('s3')
    
    # Connect to DocumentDB
    aws_documentdb_config = config(INI_FILE_PATH, SECTION_DOCMENTDB)
    dbUri = f"mongodb://{aws_documentdb_config['user']}:{aws_documentdb_config['password']}@{aws_documentdb_config['host']}:{aws_documentdb_config['port']}/?ssl=true&sslCAFile={aws_documentdb_config['ssl_ca_file']}&sslAllowInvalidHostnames={aws_documentdb_config['allow_invalid_host_name']}"
    client = MongoClient(dbUri, ssl_cert_reqs=ssl.CERT_NONE)
    mongodb = client[params['MONGODB']]
    mongocol = mongodb[f"{params['MONGOCOL_BASE']}{params['MONGOCOL_INDEX']}"]    
    loader = BatchLoaderCOCO(**params)
    loader.batch_loading(s3_resource, mongocol)
    print(f'Done save data into {params["SAVE_PATH"]}')

if __name__ == "__main__":
    isdir = os.path.isdir(params['SAVE_PATH']) 
    if not isdir:
        os.mkdir(params['SAVE_PATH'])
        os.mkdir(os.path.join(params['SAVE_PATH'], 'images'))
    
    main()