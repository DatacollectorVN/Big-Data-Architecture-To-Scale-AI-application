from src.utils import get_img_id, get_transaction, filter_tran_id, get_pred_bbox
import pandas as pd
import datetime
import sys

class SettingConfig(object):
    def __init__(self, **args):
        for key in args:
            setattr(self, key, args[key])

class ETLer(SettingConfig):
    def __init__(self, rds_client, mongocol, **args):
        super(ETLer, self).__init__(**args)
        self.mongocol = mongocol
        self.rds_client = rds_client
    
    def extract_data_rds(self):
        cur = self.rds_client.cursor()
        cur.execute(f'USE {self.RDS_DATABASE};')
        df_image = self._extract_table(cur, 'image', ['image_id', 'bucket', 'folder', 'image_file'])
        df_pred_bbox = self._extract_table(cur, 'pred_bounding_box', ['pred_bbox_id', 'transaction_id', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max'])
        df_transaction = self._extract_table(cur, 'transaction', ['transaction_id', 'image_id', 'time', 'cs_thr', 'nms_thr'])

        df_join = self._group_three_table(df_image, df_pred_bbox, df_transaction)

        return df_join
    
    def extract_img_id_documentdb(self):
        results = self.mongocol.find({}, {'img_id':1, '_id':0})
        imgs_id = []
        for i in list(results):
            if len(i) == 0: # advoid the meta info at the first row in collection
                continue
            else:
                imgs_id.append(i['img_id'])

        return imgs_id
    
    def batch_loading(self, df_join):
        batch_dataset = self._transform_to_document(df_join)
        # firstly, insert meta_info
        self.mongocol.insert_one(batch_dataset['meta_info'])

        # secondly, insert image as row
        for row in batch_dataset['dataset']:
            self.mongocol.insert_one(row)
    
    def incremental_loading(self, img_id_df, df_join):
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
        trans_id =  df_img_incre['transaction_id'].unique()
        for tran_id in trans_id:
            dict_tran = get_transaction(df_img_incre, tran_id)
            dict_img['transactions'].append(dict_tran) 
        self.mongocol.insert_one(dict_img)

    def updated_loading(self, img_id_df, df_join):
        trans_id_col = self._extract_tran_id_accord_img_id(img_id_df)
        trans_id_df = df_join[df_join['image_id'] == img_id_df]['transaction_id'].unique()
        trans_id_update = filter_tran_id(trans_id_col, trans_id_df)
        tran = self._extract_tran_accord_img_id(img_id_df)
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
            pred_bboxes_id = df_tran['pred_bbox_id'].unique()    
            for pred_bbox_id in pred_bboxes_id:
                dict_pred_box = get_pred_bbox(df_tran, pred_bbox_id)
                dict_tran['pred_bbox'].append(dict_pred_box)
            tran.append(dict_tran)
        
        self.mongocol.update({'img_id':{'$eq':int(img_id_df)}}, {'$set':{'transactions':tran}}) 
        
    def _extract_table(self, cur, table_name, columns=None):
        cur.execute(f'SELECT * from {table_name};')
        rows = cur.fetchall()

        return(pd.DataFrame(rows, columns=columns)) 

    def _extract_tran_id_accord_img_id(self, img_id):
        results = self.mongocol.find({'img_id':{'$eq':int(img_id)}}, {'transactions.tran_id':1,'_id':0})
        trans_id = [i['tran_id'] for i in list(results)[0]['transactions']]

        return trans_id

    def _extract_tran_accord_img_id(self, img_id):
        results = self.mongocol.find({'img_id':{'$eq':int(img_id)}}, {'transactions':1,'_id':0})
        tran = list(results)[0]['transactions']
        
        return tran
    
    def _group_three_table(self, df_image, df_pred_bbox, df_transaction, interval_day=1):
        df_transaction = self._remove_reduant_trans(df_transaction)
        df_join = df_transaction.merge(df_image, how='inner').merge(df_pred_bbox, how='inner')
        df_join = df_join.sort_values(by=['image_id', 'transaction_id', 'pred_bbox_id'], ascending = True)
        cols = ['image_id', 'transaction_id', 'pred_bbox_id', 'time', 'bucket', 'folder', 'image_file', 'cs_thr', 'nms_thr', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max']
        df_join = df_join[cols]
        df_join[['time', 'bucket', 'folder', 'image_file']] = df_join[['time', 'bucket', 'folder', 'image_file']].astype(str)
        df_join[['cs_thr', 'nms_thr', 'pred_cs']] = df_join[['cs_thr', 'nms_thr', 'pred_cs']].astype(float)
        df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']] = df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']].astype(int)

        return df_join

    def _remove_reduant_trans(self, df_transaction):
        '''Base on time column in df_transaction, remove transtractions that were 
        recorded before `interal_day` days.'''
        
        date_now = datetime.datetime.now().date()
        days = datetime.timedelta(self.INTERVAL_DAY_LOADING)
        flags = date_now - pd.to_datetime(df_transaction['time'].values).date <= days
        df_transaction = df_transaction[flags]
        
        return df_transaction
    
    def _transform_to_document(self, df_join):
        row = {}
        meta_info = {"month": "June - 2022", 
                    "duration_months": 1, 
                    "source": "AWS_RDS"}
        dataset = []
        dataset = self._transform_to_dataset(df_join, dataset)      
        
        row = {"meta_info": meta_info,
            "dataset": dataset}
        
        return row
    
    def _transform_to_dataset(self, df_join, dataset):
        imgs_id = df_join['image_id'].unique()
        for img_id in imgs_id:
            dict_img = get_img_id(df_join, img_id)
            dataset.append(dict_img)
        return dataset