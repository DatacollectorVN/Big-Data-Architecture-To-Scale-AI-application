import pandas as pd
import sys
import numpy as np
import json 
import datetime

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def extract_data(rds_client, interval_day=1, full_loading_flag=False):
    cur = rds_client.cursor()
    cur.execute('USE x_ray;')
    df_image = _load_table(cur, 'image', ['image_id', 'bucket', 'folder', 'image_file'])
    df_pred_bbox = _load_table(cur, 'pred_bounding_box', ['pred_bbox_id', 'transaction_id', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max'])
    df_transaction = _load_table(cur, 'transaction', ['transaction_id', 'image_id', 'time', 'cs_thr', 'nms_thr'])

    df_join = _group_three_table(df_image, df_pred_bbox, df_transaction, interval_day)
    return df_join

def _transform_to_document(df_join, full_loading_flag=False):
    row = {}
    meta_info = {"month": "June - 2022", 
                 "duration_months": 1, 
                 "source": "AWS_RDS"}
    dataset = []
    dataset = _transform_to_dataset(df_join, dataset)      
    
    row = {"meta_info": meta_info,
           "dataset": dataset}
    return row

def _transform_to_dataset(df_join, dataset):
    imgs_id = df_join['image_id'].unique()
    for img_id in imgs_id:
        dict_img = {}
        df_img = df_join[df_join['image_id'] == img_id]
        
        bucket = df_img['bucket'].unique()
        if len(bucket) !=1:
            print('Error')
        else:
            bucket = bucket[0]
        
        folder = df_img['folder'].unique()
        if len(folder) !=1:
            print('Error')
        else:
            folder = folder[0]
        
        img_file = df_img['image_file'].unique()
        if len(img_file) !=1:
            print('Error')
        else:
            img_file = img_file[0]
        
        # update to dictionary
        dict_img['img_id'] = int(img_id)
        dict_img['bucket'] = bucket
        dict_img['folder'] = folder
        dict_img['img_file'] = img_file
        dict_img['transactions'] = []
        dict_img = _get_transaction(df_img, dict_img)
        dataset.append(dict_img)
    
    return dataset

def _get_transaction(df_img, dict_img):
    trans_id =  df_img['transaction_id'].unique()
    for tran_id in trans_id:
        dict_tran = {}
        df_tran = df_img[df_img['transaction_id'] == tran_id]
        
        time = df_tran['time'].unique()
        if len(time) !=1:
            print('Error')
        else:
            time = time[0]
        
        cs_thr = df_tran['cs_thr'].unique()
        if len(cs_thr) !=1:
            print('Error')
        else:
            cs_thr = cs_thr[0]
        
        nms_thr = df_tran['nms_thr'].unique()
        if len(nms_thr) !=1:
            print('Error')
        else:
            nms_thr = nms_thr[0]
        
        # update to dictionary
        dict_tran['tran_id'] = int(tran_id)
        dict_tran['time'] = time
        dict_tran['cs_thr'] = cs_thr
        dict_tran['nms_thr'] = nms_thr
        dict_tran['mode'] = 'Object Detection'
        dict_tran['pred_bbox'] = []
        dict_tran = _get_pred_bbox(df_tran, dict_tran)
        dict_img['transactions'].append(dict_tran)    
    
    return dict_img
        
def _get_pred_bbox(df_tran, dict_tran):
    pred_bboxes_id = df_tran['pred_bbox_id'].unique()    
    for pred_bbox_id in pred_bboxes_id:
        dict_pred_box = {}
        df_pred_bboxes = df_tran[df_tran['pred_bbox_id'] == pred_bbox_id]
        pred_class = df_pred_bboxes['pred_class'].values
        if len(pred_class) !=1:
            print('Error')
        else:
            pred_class = pred_class[0] 
        
        pred_cs = df_pred_bboxes['pred_cs'].values
        if len(pred_cs) !=1:
            print('Error')
        else:
            pred_cs = pred_cs[0]

        offset_value =  df_pred_bboxes[['x_min', 'y_min', 'x_max', 'y_max']].values
        if len(offset_value) !=1:
            print('Error')
        else:
            offset_value = [int(offset_value[0][0]), int(offset_value[0][1]), int(offset_value[0][2]), int(offset_value[0][3])]
        # update to dictionary
        dict_pred_box['pred_bbox_id'] = int(pred_bbox_id)
        dict_pred_box['pred_class'] = int(pred_class)
        dict_pred_box['pred_cs'] = pred_cs
        dict_pred_box['offset_value'] = offset_value
        dict_tran['pred_bbox'].append(dict_pred_box)
    
    return dict_tran
        
def full_loading(mongocol, df_join):
    '''
        Clear exist data in collection of documentDB server then loading all new data into it.
    '''
    # delete all rows in collection
    mongocol.delete_many({})

def _remove_reduant_trans(df_transaction, interval_day=1):
    '''Base on time column in df_transaction, remove transtractions that were recorded before `interal_day` days.'''
    date_now = datetime.datetime.now().date()
    days = datetime.timedelta(interval_day)
    flags = date_now - pd.to_datetime(df_transaction['time'].values).date <= days
    df_transaction = df_transaction[flags]
    
    return df_transaction

def _group_three_table(df_image, df_pred_bbox, df_transaction, interval_day=1):
    df_transaction = _remove_reduant_trans(df_transaction,interval_day )
    df_join = df_transaction.merge(df_image, how='inner').merge(df_pred_bbox, how='inner')
    df_join = df_join.sort_values(by=['image_id', 'transaction_id', 'pred_bbox_id'], ascending = True)
    cols = ['image_id', 'transaction_id', 'pred_bbox_id', 'time', 'bucket', 'folder', 'image_file', 'cs_thr', 'nms_thr', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max']
    df_join = df_join[cols]
    df_join[['time', 'bucket', 'folder', 'image_file']] = df_join[['time', 'bucket', 'folder', 'image_file']].astype(str)
    df_join[['cs_thr', 'nms_thr', 'pred_cs']] = df_join[['cs_thr', 'nms_thr', 'pred_cs']].astype(float)
    df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']] = df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']].astype(int)
    
    return df_join

def _load_table(cur, table_name, columns=None):
    cur.execute(f'SELECT * from {table_name};')
    rows = cur.fetchall()
    return(pd.DataFrame(rows, columns=columns))

#### 
def query_img_id_from_collection(mongocol):
    results = mongocol.find({}, {'img_id':1, '_id':0})
    imgs_id = []
    for i in list(results):
        if len(i) == 0: # advoid the meta info at the first row in collection
            continue
        else:
            imgs_id.append(i['img_id'])

    return imgs_id

def _query_tran_id_accord_img_id(mongocol, img_id):
    results = mongocol.find({'img_id':{'$eq':int(img_id)}}, {'transactions.tran_id':1,'_id':0})
    trans_id = [i['tran_id'] for i in list(results)[0]['transactions']]

    return trans_id

def _query_tran_accord_img_id(mongocol, img_id):
    results = mongocol.find({'img_id':{'$eq':int(img_id)}}, {'transactions':1,'_id':0})
    tran = list(results)[0]['transactions']
    
    return tran

def _filter_tran_id(trans_id_col, trans_id_df):
    temp_1 = set(trans_id_df) ^ set(trans_id_col)
    temp_2 = temp_1 & set(trans_id_df)
    
    return list(temp_2)

def batch_loading(df_join, mongocol):
    batch_dataset = _transform_to_document(df_join)
    
    # firstly, insert meta_info
    mongocol.insert_one(batch_dataset['meta_info'])

    # secondly, insert image as row
    for row in batch_dataset['dataset']:
        mongocol.insert_one(row)


def incremental_loading(img_id_df, mongocol, df_join):
    print(f'Loading new image with id {img_id_df} ...')
    dict_img = {}
    df_img_incre = df_join[df_join['image_id'] == img_id_df]
    bucket = df_img_incre['bucket'].unique()
    if len(bucket) !=1:
        print('Error')
    else:
        bucket = bucket[0]
    
    folder = df_img_incre['folder'].unique()
    if len(folder) !=1:
        print('Error')
    else:
        folder = folder[0]
    
    img_file = df_img_incre['image_file'].unique()
    if len(img_file) !=1:
        print('Error')
    else:
        img_file = img_file[0]
    
    # update to dictionary
    dict_img['img_id'] = int(img_id_df)
    dict_img['bucket'] = bucket
    dict_img['folder'] = folder
    dict_img['img_file'] = img_file
    dict_img['transactions'] = []
    dict_img = _get_transaction(df_img_incre, dict_img)
    mongocol.insert_one(dict_img)
    
def updated_loading(img_id_df, mongocol, df_join):
    trans_id_col = _query_tran_id_accord_img_id(mongocol, img_id_df)
    trans_id_df = df_join[df_join['image_id'] == img_id_df]['transaction_id'].unique()
    trans_id_update = _filter_tran_id(trans_id_col, trans_id_df)
    tran = _query_tran_accord_img_id(mongocol, img_id_df)
    print(f'Number of updated transaction in image id {img_id_df}: {len(trans_id_update)}')
    
    for tran_id_update in trans_id_update:
        dict_tran = {}
        df_tran = df_join[df_join['transaction_id'] == tran_id_update]
        time = df_tran['time'].unique()
        if len(time) !=1:
            print('Error')
        else:
            time = time[0]
        
        cs_thr = df_tran['cs_thr'].unique()
        if len(cs_thr) !=1:
            print('Error')
        else:
            cs_thr = cs_thr[0]
        
        nms_thr = df_tran['nms_thr'].unique()
        if len(nms_thr) !=1:
            print('Error')
        else:
            nms_thr = nms_thr[0]
        
        # update to dictionary
        dict_tran['tran_id'] = int(tran_id_update)
        dict_tran['time'] = time
        dict_tran['cs_thr'] = cs_thr
        dict_tran['nms_thr'] = nms_thr
        dict_tran['mode'] = 'Object Detection'
        dict_tran['pred_bbox'] = []
        dict_tran = _get_pred_bbox(df_tran, dict_tran)
        tran.append(dict_tran)
    
    mongocol.update({'img_id':{'$eq':int(img_id_df)}}, {'$set':{'transactions':tran}})