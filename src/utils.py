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

def get_img_id(df_join, img_id):
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
    trans_id =  df_img['transaction_id'].unique()
    for tran_id in trans_id:
        dict_tran = get_transaction(df_img, tran_id)
        dict_img['transactions'].append(dict_tran) 
    
    return dict_img
    
def get_transaction(df_img, tran_id):
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
    pred_bboxes_id = df_tran['pred_bbox_id'].unique()    
    for pred_bbox_id in pred_bboxes_id:
        dict_pred_box = get_pred_bbox(df_tran, pred_bbox_id)
        dict_tran['pred_bbox'].append(dict_pred_box)
       
    return dict_tran
    
def get_pred_bbox(df_tran, pred_bbox_id):
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
    
    return dict_pred_box    

def filter_tran_id(trans_id_col, trans_id_df):
    temp_1 = set(trans_id_df) ^ set(trans_id_col)
    temp_2 = temp_1 & set(trans_id_df)
    
    return list(temp_2)