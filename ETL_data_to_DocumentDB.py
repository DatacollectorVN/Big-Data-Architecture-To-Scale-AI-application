import os
import pymysql
import pandas as pd
from pymongo import MongoClient
import ssl
from IAC.config import config
import json
import sys
import yaml
from src.utils import extract_data, batch_loading, query_img_id_from_collection, updated_loading, incremental_loading

INI_FILE_PATH = os.path.join('IAC', 'credential_aws.ini')
SECTION_DOCMENTDB = 'Credential-AWS-documentDB'
SECTION_RDS = 'Credential-AWS-RDS-MySQL'

FILE_ETL_CONFIG = os.path.join("config", "ETL.yaml")
with open(FILE_ETL_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

def main():
    aws_rds_config = config(INI_FILE_PATH, SECTION_RDS)
    aws_documentdb_config = config(INI_FILE_PATH, SECTION_DOCMENTDB)
    rds_client = pymysql.connect(**aws_rds_config)
    df_join = extract_data(rds_client, params['INTERVAL_DAY_LOADING'])
    dbUri = f"mongodb://{aws_documentdb_config['user']}:{aws_documentdb_config['password']}@{aws_documentdb_config['host']}:{aws_documentdb_config['port']}/?ssl=true&sslCAFile={aws_documentdb_config['ssl_ca_file']}&sslAllowInvalidHostnames={aws_documentdb_config['allow_invalid_host_name']}"
    client = MongoClient(dbUri, ssl_cert_reqs=ssl.CERT_NONE)
    mongodb = client[params['MONGODB']]
    mongocol = mongodb[f"{params['MONGOCOL_BASE']}{params['MONGOCOL_INDEX']}"]

    imgs_id_col = query_img_id_from_collection(mongocol)   
    if len(imgs_id_col) == 0:
        batch_loading(df_join, mongocol)
        print(f'Done batch loading to collection {mongocol.name}')
    else:
        imgs_id_df = df_join['image_id'].unique()
        for img_id_df in imgs_id_df:
            if img_id_df in imgs_id_col:
                updated_loading(img_id_df, mongocol, df_join)
                print(f'Done updated loading image id {img_id_df}')
            else:
                incremental_loading(img_id_df, mongocol, df_join)
                print(f'Done incremental loading image id {img_id_df}')

if __name__ == '__main__':
    main()