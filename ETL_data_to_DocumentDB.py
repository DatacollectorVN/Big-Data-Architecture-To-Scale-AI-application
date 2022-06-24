import os
import pymysql
import pandas as pd
from pymongo import MongoClient
import ssl
from src.etler import ETLer
from IAC.config import config
import json
import sys
import yaml

INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')
SECTION_DOCMENTDB = 'Credential-AWS-documentDB'
SECTION_RDS = 'Credential-AWS-RDS-MySQL'

FILE_ETL_CONFIG = os.path.join("config", "ETL.yaml")
with open(FILE_ETL_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

def main():
    # Connection
    aws_rds_config = config(INI_FILE_PATH, SECTION_RDS)
    aws_documentdb_config = config(INI_FILE_PATH, SECTION_DOCMENTDB)
    rds_client = pymysql.connect(**aws_rds_config)
    dbUri = f"mongodb://{aws_documentdb_config['user']}:{aws_documentdb_config['password']}@{aws_documentdb_config['host']}:{aws_documentdb_config['port']}/?ssl=true&sslCAFile={aws_documentdb_config['ssl_ca_file']}&sslAllowInvalidHostnames={aws_documentdb_config['allow_invalid_host_name']}"
    client = MongoClient(dbUri, ssl_cert_reqs=ssl.CERT_NONE)
    mongodb = client[params['MONGODB']]
    mongocol = mongodb[f"{params['MONGOCOL_BASE']}{params['MONGOCOL_INDEX']}"]
    
    etler = ETLer(rds_client, mongocol, **params)
    # extract
    df_join = etler.extract_data_rds()
    imgs_id_col = etler.extract_img_id_documentdb()   
    
    # transform and loading
    if len(imgs_id_col) == 0:
        etler.batch_loading(df_join)
        print(f'Done batch loading to collection {mongocol.name}')
    else:
        imgs_id_df = df_join['image_id'].unique()
        for img_id_df in imgs_id_df:
            if img_id_df in imgs_id_col:
                etler.updated_loading(img_id_df, df_join)
                print(f'Done updated loading image id {img_id_df}')
            else:
                etler.incremental_loading(img_id_df, df_join)
                print(f'Done incremental loading image id {img_id_df}')

if __name__ == '__main__':
    main()