import numpy as np
import pandas as pd
from detectron2.config import get_cfg
from detectron2 import model_zoo
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from collections import Counter
import sys
import json
from datetime import datetime
import boto3
import io
import os
from IAC.config import config
import pymysql
'''Hide command below cause we use Apple M1 therefore can't install ensemble_boxes'''
# from ensemble_boxes import nms, weighted_boxes_fusion 
from detectron2.structures import BoxMode

def plot_multi_imgs(imgs, # 1 batchs contain multiple images
                    cols=2, size=10, # size of figure
                    is_rgb=True, title=None, cmap="gray", save=False,
                    img_size=None): # set img_size if you want (width, height)
    rows = (len(imgs) // cols) + 1
    fig = plt.figure(figsize = (size *  cols, size * rows))
    for i , img in enumerate(imgs):
        if img_size is not None:
            img = cv2.resize(img, img_size)
        fig.add_subplot(rows, cols, i + 1) # add subplot int the the figure
        plt.imshow(img, cmap = cmap) # plot individual image
    plt.suptitle(title)
    if save:
        os.makedirs("outputs", exist_ok = True)
        plt.savefig(os.path.join("outputs", save))

def draw_bbox(img, img_bboxes, img_classes_name, classes_name, color, thickness=5):
    img_draw = img.copy()
    for i, img_bbox in enumerate(img_bboxes):
        img_draw = cv2.rectangle(img_draw, pt1 = (int(img_bbox[0]), int(img_bbox[1])), 
                                 pt2 = (int(img_bbox[2]), int(img_bbox[3])), 
                                 color = color[classes_name.index(img_classes_name[i])],
                                 thickness = thickness) 
        cv2.putText(img_draw,
                    text = img_classes_name[i].upper(),
                    org = (int(img_bbox[0]), int(img_bbox[1]) - 5),
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.6,
                    color = (255, 255, 255),
                    thickness = 1, lineType = cv2.LINE_AA)    
    
    return img_draw

def xray_NMS(df, img_id, params):
    img = cv2.imread(os.path.join(params["IMG_DIR"], img_id))
    height, width = img.shape[:2]
    img_annotations = df[df["image_file"] == img_id]
    classes_name_full = img_annotations["class_name"].tolist()
    classes_id_full = [params["CLASSES_NAME"].index(i) for i in classes_name_full]
    classes_id_count = Counter(classes_id_full)
    classes_id_unique = [params["CLASSES_NAME"].index(i) for i in img_annotations["class_name"].unique().tolist()] 
    norm_scale = np.hstack([width, height, width, height])

    # prepare input data of nms function
    bboxes_lst = []
    scores_lst = [] # all scores is 1, cause all of bounding boxes is labeled by doctor
    classes_id_lst = []
    weights = [] # all weigths is 1, cause all of bounding boxes is ground truth 

    # have a list to save a single boxes cause the NMS function do not allow this case
    classes_id_single_lst = []
    bboxes_single_lst = []
    for class_id in classes_id_unique:
        if classes_id_count[class_id] == 1:
            classes_id_single_lst.append(class_id)
            bboxes_single_lst.append(img_annotations[img_annotations["class_name"] == params["CLASSES_NAME"][class_id]][["x_min", "y_min", "x_max", "y_max"]].to_numpy().squeeze().tolist())
        else:
            cls_id_lst = [class_id for _ in range(classes_id_count[class_id])]
            scores_ = np.ones(shape = classes_id_count[class_id]).tolist()
            bboxes = img_annotations[img_annotations["class_name"] == params["CLASSES_NAME"][class_id]][["x_min", "y_min", "x_max", "y_max"]].to_numpy()
            bboxes = bboxes / norm_scale
            bboxes = np.clip(bboxes, 0, 1).tolist()
            classes_id_lst.append(cls_id_lst)
            bboxes_lst.append(bboxes)
            scores_lst.append(scores_)
            weights.append(1)
    if classes_id_lst == []:
        boxes_nms = []
        classes_ids_nms = []
    else:
        boxes_nms, scores, classes_ids_nms = nms(boxes = bboxes_lst, scores = scores_lst, labels = classes_id_lst,
                                                 iou_thr = params["IOU_THR_NMS"], weights = weights)
        boxes_nms = boxes_nms * norm_scale
        boxes_nms = boxes_nms.astype(int).tolist()
        classes_ids_nms = classes_ids_nms.astype(int).tolist()

    # add with single class
    boxes_nms.extend(bboxes_single_lst)
    classes_ids_nms.extend(classes_id_single_lst)
    classes_name_nms = [params["CLASSES_NAME"][j] for j in classes_ids_nms]
    
    return boxes_nms, classes_name_nms

def xray_WBF(df, img_id, params):
    img = cv2.imread(os.path.join(params["IMG_DIR"], img_id))
    height, width = img.shape[:2]
    img_annotations = df[df["image_file"] == img_id]
    classes_name_full = img_annotations["class_name"].tolist()
    classes_id_full = [params["CLASSES_NAME"].index(i) for i in classes_name_full]
    classes_id_count = Counter(classes_id_full)
    classes_id_unique = [params["CLASSES_NAME"].index(i) for i in img_annotations["class_name"].unique().tolist()] 
    norm_scale = np.hstack([width, height, width, height])

    # prepare input data of nms function
    bboxes_lst = []
    scores_lst = [] # all scores is 1, cause all of bounding boxes is labeled by doctor
    classes_id_lst = []
    weights = [] # all weigths is 1, cause all of bounding boxes is ground truth 

    # have a list to save a single boxes cause the NMS function do not allow this case
    classes_id_single_lst = []
    bboxes_single_lst = []
    for class_id in classes_id_unique:
        if classes_id_count[class_id] == 1:
            classes_id_single_lst.append(class_id)
            bboxes_single_lst.append(img_annotations[img_annotations["class_name"] == params["CLASSES_NAME"][class_id]][["x_min", "y_min", "x_max", "y_max"]].to_numpy().squeeze().tolist())
        else:
            cls_id_lst = [class_id for _ in range(classes_id_count[class_id])]
            scores_ = np.ones(shape = classes_id_count[class_id]).tolist()
            bboxes = img_annotations[img_annotations["class_name"] == params["CLASSES_NAME"][class_id]][["x_min", "y_min", "x_max", "y_max"]].to_numpy()
            bboxes = bboxes / norm_scale
            bboxes = np.clip(bboxes, 0, 1).tolist()
            classes_id_lst.append(cls_id_lst)
            bboxes_lst.append(bboxes)
            scores_lst.append(scores_)
            weights.append(1)
    if classes_id_lst == []:
        boxes_nms = []
        classes_ids_nms = []
    else:
        boxes_nms, scores, classes_ids_nms = weighted_boxes_fusion(boxes_list = bboxes_lst, scores_list = scores_lst, labels_list = classes_id_lst,
                                                                   iou_thr = params["IOU_THR_WBF"], weights = weights, skip_box_thr = params["SKIP_BOX_THR_WBF"])
        boxes_nms = boxes_nms * norm_scale
        boxes_nms = boxes_nms.astype(int).tolist()
        classes_ids_nms = classes_ids_nms.astype(int).tolist()

    # add with single class
    boxes_nms.extend(bboxes_single_lst)
    classes_ids_nms.extend(classes_id_single_lst)
    classes_name_nms = [params["CLASSES_NAME"][j] for j in classes_ids_nms]
    
    return boxes_nms, classes_name_nms

def x_ray_train_val_split(df, val_ratio):
    # problem 2 in standard data
    train_standard = ["ec513a0af055499f1b188cc6a9175ee1.jpg", 
                      "f9f7feefb4bac748ff7ad313e4a78906.jpg"]
    val_standard = ["43e11813c6d7bcef779a1a287edc02c4.jpg"]

def get_chestxray_dicts(df, class_name, img_dir):
    COCO_detectron2_list = [] # list(dict())
    img_paths = []
    img_ids = df["image_file"].unique().tolist()
    for i, img_id in enumerate(img_ids):
        img_path = os.path.join(img_dir, img_id)
        img_paths.append(img_paths)
        img = Image.open(img_path)
        width, height = img.size
        id_ = i + 1
        img_classes_name = df[df["image_file"] == img_id]["class_name"].values.tolist()
        img_bboxes = df[df["image_file"] == img_id][["x_min", "y_min", "x_max", "y_max"]].values
        x_min = img_bboxes[:, 0]
        y_min = img_bboxes[:, 1]
        x_max = img_bboxes[:, 2]
        y_max = img_bboxes[:, 3]
        annotaions = [] # list(dict())
        for j, img_class_name in enumerate(img_classes_name):
            annotaions_dct = {"bbox" : [x_min[j], y_min[j], x_max[j], y_max[j]],
                              "bbox_mode" : BoxMode.XYXY_ABS,
                              "category_id" : class_name.index(img_class_name)
                             }
            annotaions.append(annotaions_dct)
        COCO_detectron2_dct = {"image_id" : id_,
                               "file_name" : img_path,
                               "height" : height,
                               "width" : width,
                               "annotations" : annotaions
                              }
        COCO_detectron2_list.append(COCO_detectron2_dct)
    
    return COCO_detectron2_list

def detectron2_prediction(model, img):
    '''
        Args:
            + model: Detectron2 model file.
            + img: Image file with RGB channel
        Return:
            + outputs: Ouput of detetron2's predictions
    '''
    
    img_copy = img.copy()
    img_copy = cv2.cvtColor(img_copy, cv2.COLOR_RGB2BGR)
    
    return model(img_copy)

def get_outputs_detectron2(outputs, to_cpu=True):
    if to_cpu:
        instances = outputs["instances"].to("cpu")
    else:
        instances = outputs["instances"]

    pred_bboxes = instances.get("pred_boxes").tensor
    pred_confidence_scores = instances.get("scores")
    pred_classes = instances.get("pred_classes")
    
    return pred_bboxes, pred_confidence_scores, pred_classes

def draw_bbox_infer(img, pred_bboxes, pred_classes_id, pred_scores, classes_name, color, thickness=5):
    img_draw = img.copy()
    for i, img_bbox in enumerate(pred_bboxes):
        img_draw = cv2.rectangle(img_draw, pt1 = (int(img_bbox[0]), int(img_bbox[1])), 
                                 pt2 = (int(img_bbox[2]), int(img_bbox[3])), 
                                 color = color[classes_name.index(classes_name[pred_classes_id[i]])],
                                 thickness = thickness)         
        cv2.putText(img_draw,
                    text = classes_name[pred_classes_id[i]].upper() + " (" + str(round(pred_scores[i] * 100, 2)) + "%)",
                    org = (int(img_bbox[0]), int(img_bbox[1]) - 5),
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.6,
                    color = (255, 0, 0),
                    thickness = 1, lineType = cv2.LINE_AA)     
    
    return img_draw

def write_metadata_experiment(params):
    with open(os.path.join(params["OUTPUT_DIR"], "metadata.txt"), 'w') as f:
        f.write("TRANSFER,TRANSFER_LEARNING,RESIZE,MODEL,IMS_PER_BATCH,BATCH_SIZE_PER_IMAGE,WARMUP_ITERS,BASE_LR,MAX_ITER,STEPS_MIN,STEPS_MAX,GAMMA,LR_SCHEDULER_NAME,RANDOM_FLIP,EVAL_PERIOD")
        f.write("\n")
        f.write(str(params["TRANSFER"]) + "," + params["TRANSFER_LEARNING"] + "," + str(params["RESIZE"]) + "," + params["MODEL"] + "," + str(params["IMS_PER_BATCH"]) + "," + str(params["BATCH_SIZE_PER_IMAGE"]) + "," + str(params["WARMUP_ITERS"]) + "," + str(params["BASE_LR"]) + "," + str(params["MAX_ITER"]) +  "," + str(params["STEPS_MIN"]) + "," + str(params["STEPS_MAX"]) + "," + str(params["GAMMA"]) + "," + params["LR_SCHEDULER_NAME"] + "," + params["RANDOM_FLIP"] + "," + str(params["EVAL_PERIOD"]))

def check_connect_rds(INI_FILE_PATH_RDS, SECTION_RDS):
    conn = None
    try:
        # read connection parameters
        params = config(INI_FILE_PATH_RDS, SECTION_RDS)

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = pymysql.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        print('MySQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, pymysql.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def update_data_to_data_lake(rds_client, s3_resource,  aws_s3_info, pred_confidence_scores, pred_classes, pred_bboxes, 
                             image_file, image_file_name, cs_thr, nms_thr):
    cur = rds_client.cursor()
    cur.execute('USE x_ray;')
    cur.execute('SET FOREIGN_KEY_CHECKS=0;')
    image_file_exist = []
    for i in s3_resource.Bucket(aws_s3_info['root_bucket']).objects.filter(Prefix=aws_s3_info['xray_images_bucket']):
        if i.key.split('/')[1] != '':
            image_file_exist.append(i.key.split('/')[1])
    
    if len(image_file_exist) == 0: # empty folder in s3
        upload_image_to_s3(s3_resource, image_file, image_file_name, 
                           aws_s3_info['root_bucket'], aws_s3_info['xray_images_bucket'])
        print(f"Uploaded {image_file_name} to {aws_s3_info['root_bucket']} s3 bucket in folder {aws_s3_info['xray_images_bucket']}")
        update_image_entity_rds(cur, aws_s3_info['root_bucket'], aws_s3_info['xray_images_bucket'], 
                                image_file_name)
        rds_client.commit()
        print('Updated image entities')
        current_trans_id = update_transaction_entity_rds(cur, image_file_name, cs_thr, nms_thr)
        
        rds_client.commit()
        print('Updated trasaction entities with new image id')
        update_pred_bounding_box_entity_rd(cur, current_trans_id, pred_confidence_scores, pred_classes, pred_bboxes)
        rds_client.commit()
        print('Update pred_bounding_box entities with new trasaction id')
    else:
        if image_file_name not in image_file_exist:
            print(f'{image_file_name} not exist in s3 butcket')
            upload_image_to_s3(s3_resource, image_file, image_file_name, 
                                    aws_s3_info['root_bucket'], aws_s3_info['xray_images_bucket'])
            print(f"Uploaded {image_file_name} to {aws_s3_info['root_bucket']} s3 bucket in folder {aws_s3_info['xray_images_bucket']}")
            update_image_entity_rds(cur, aws_s3_info['root_bucket'], aws_s3_info['xray_images_bucket'], 
                                    image_file_name)
            rds_client.commit()
            print(f'Updated image table')
            current_trans_id = update_transaction_entity_rds(cur, image_file_name, cs_thr, nms_thr)
            rds_client.commit()
            print(f'Updated transaction table')
            update_pred_bounding_box_entity_rd(cur, current_trans_id, pred_confidence_scores, pred_classes, pred_bboxes)
            rds_client.commit()
            print(f'Updated pred_bounding_box table')
        else:
            print(f'{image_file_name} exist in s3 butcket')
            current_trans_id = update_transaction_entity_rds(cur, image_file_name, cs_thr, nms_thr)
            rds_client.commit()
            print(f'Updated transaction table')
            update_pred_bounding_box_entity_rd(cur, current_trans_id, pred_confidence_scores, pred_classes, pred_bboxes)
            rds_client.commit()
            print(f'Updated pred_bounding_box table')

def update_image_entity_rds(cur, bucket, folder, image_file_in_s3):
    cur.execute('SELECT MAX(image_id) from image;')
    max_image_id = cur.fetchone()[0]
    if max_image_id is None:
        max_image_id = 0
    cur.execute(f'INSERT INTO image VALUES({max_image_id+1}, "{bucket}", "{folder}", "{image_file_in_s3}")')

def update_transaction_entity_rds(cur, image_file_name, cs_thr, nms_thr):
    cur.execute(f'SELECT image_id FROM image WHERE image_file = "{image_file_name}";')
    image_id = cur.fetchone()[0]
    cur.execute(f'SELECT MAX(transaction_id) FROM transaction;')
    max_transaction_id = cur.fetchone()[0]
    if max_transaction_id is None:
        max_transaction_id = 0
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(f'INSERT INTO transaction VALUES({max_transaction_id+1}, {image_id}, "{time}", {cs_thr}, {nms_thr})')
    
    return max_transaction_id + 1

def update_pred_bounding_box_entity_rd(cur, current_trans_id, pred_confidence_scores, pred_classes, pred_bboxes):
    cur.execute('SELECT MAX(pred_bbox_id) from pred_bounding_box;')
    max_pred_bbox_id = cur.fetchone()[0]
    if max_pred_bbox_id is None:
        max_pred_bbox_id = 0
    pred_bbox_id = max_pred_bbox_id + 1
    pred_x_mins = pred_bboxes[:, 0]
    pred_y_mins = pred_bboxes[:, 1]
    pred_x_maxs = pred_bboxes[:, 2]
    pred_y_maxs = pred_bboxes[:, 3]

    for i in range(len(pred_classes)):
        pred_class = pred_classes[i]
        pred_confidence_score = pred_confidence_scores[i]
        pred_x_min = pred_x_mins[i]
        pred_y_min = pred_y_mins[i]
        pred_x_max = pred_x_maxs[i]
        pred_y_max = pred_y_maxs[i]
        cur.execute(f'INSERT INTO pred_bounding_box VALUES({pred_bbox_id}, {current_trans_id}, {pred_class}, ROUND({pred_confidence_score}, 3), {pred_x_min}, {pred_y_min}, {pred_x_max}, {pred_y_max})')
        pred_bbox_id += 1

def parse_sql_scripts(scripts):
    DELIMITER = ';'
    stmts = []
    for i in [content + DELIMITER for content in scripts.split(DELIMITER)[:-1]]:
        if i.startswith('\n'):
            i = i[i.find('\n') + len('\n'):]
        stmts.append(i)
    
    return stmts

def check_connect_s3(INI_FILE_PATH_S3, SECTION_S3):
    try:
        params = config(INI_FILE_PATH_S3, SECTION_S3)
        s3_client = boto3.client('s3', **params)
        print('Connect successfully')
    except Exception as error:
        print(error)

def parse_sql_scripts(scripts):
    DELIMITER = ';'
    stmts = []
    for i in [content + DELIMITER for content in scripts.split(DELIMITER)[:-1]]:
        if i.startswith('\n'):
            i = i[i.find('\n') + len('\n'):]
        stmts.append(i)
    
    return stmts

def upload_image_to_s3(s3_resource, image_file, image_file_name, s3_bucket, s3_image_folder):
    in_mem_file = io.BytesIO()
    image_file.save(in_mem_file, format=image_file.format)
    in_mem_file.seek(0)
    s3_resource.meta.client.upload_fileobj(in_mem_file, s3_bucket, s3_image_folder + '/' + image_file_name)

def download_image_from_s3(s3_resouce, image_file_name, s3_bucket, s3_image_folder):
    pass

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        return super(NpEncoder, self).default(obj)

def extract_data(rds_client, full_loading_flag=False):
    cur = rds_client.cursor()
    cur.execute('USE x_ray;')
    df_image = _load_table(cur, 'image', ['image_id', 'bucket', 'folder', 'image_file'])
    df_pred_bbox = _load_table(cur, 'pred_bounding_box', ['pred_bbox_id', 'transaction_id', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max'])
    df_transaction = _load_table(cur, 'transaction', ['transaction_id', 'image_id', 'time', 'cs_thr', 'nms_thr'])
    df_join = _group_three_table(df_image, df_pred_bbox, df_transaction)
    
    return df_join

def transform_to_document(df_join, full_loading_flag=False):
    row = {}
    meta_info = {"month": "June - 2022", 
                 "duration_months": 1, 
                 "source": "AWS_RDS"}
    dataset = []
    dataset = _transform_to_document(df_join, dataset)      
    
    row = {"meta_info": meta_info,
           "dataset": dataset}
    
    return row

def _transform_to_document(df_join, dataset):
    images_id = df_join['image_id'].unique()
    for image_id in images_id:
        dict_image = {}
        df_image = df_join[df_join['image_id'] == image_id]
        
        bucket = df_image['bucket'].unique()
        if len(bucket) !=1:
            print('Error')
        else:
            bucket = bucket[0]
        
        folder = df_image['folder'].unique()
        if len(folder) !=1:
            print('Error')
        else:
            folder = folder[0]
        
        image_file = df_image['image_file'].unique()
        if len(image_file) !=1:
            print('Error')
        else:
            image_file = image_file[0]
        
        # update to dictionary
        dict_image['img_id'] = int(image_id)
        dict_image['bucket'] = bucket
        dict_image['folder'] = folder
        dict_image['img_file'] = image_file
        dict_image['transactions'] = []
        dict_image = _get_transaction(df_image, dict_image)
        dataset.append(dict_image)
    
    return dataset

def _get_transaction(df_image, dict_image):
    trans_id =  df_image['transaction_id'].unique()
    for tran_id in trans_id:
        dict_trans = {}
        df_tran = df_image[df_image['transaction_id'] == tran_id]
        
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
        dict_trans['tran_id'] = int(tran_id)
        dict_trans['time'] = time
        dict_trans['cs_thr'] = cs_thr
        dict_trans['nms_thr'] = nms_thr
        dict_trans['mode'] = 'Object Detection'
        dict_trans['pred_bbox'] = []
        dict_trans = _get_pred_bbox(df_tran, dict_trans)
        dict_image['transactions'].append(dict_trans)    
    
    return dict_image
        
        
def _get_pred_bbox(df_tran, dict_trans):
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
        dict_trans['pred_bbox'].append(dict_pred_box)
    
    return dict_trans
        
def full_loading(mongocol, df_join):
    '''
        Clear exist data in collection of documentDB server then loading all new data into it.
    '''
    # delete all rows in collection
    mongocol.delete_many({})
    pass

def _group_three_table(df_image, df_pred_bbox, df_transaction):
    df_join = df_transaction.merge(df_image, how='inner').merge(df_pred_bbox, how='inner')
    df_join = df_join.sort_values(by=['image_id', 'transaction_id', 'pred_bbox_id'], ascending = True)
    cols = ['image_id', 'transaction_id', 'pred_bbox_id', 'time', 'bucket', 'folder', 'image_file', 'cs_thr', 'nms_thr', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max']
    df_join = df_join[cols]
    
    # convert data type
    df_join[['time', 'bucket', 'folder', 'image_file']] = df_join[['time', 'bucket', 'folder', 'image_file']].astype(str)
    df_join[['cs_thr', 'nms_thr', 'pred_cs']] = df_join[['cs_thr', 'nms_thr', 'pred_cs']].astype(float)
    df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']] = df_join[['image_id', 'transaction_id', 'pred_bbox_id', 'pred_class', 'x_min', 'y_min', 'x_max', 'y_max']].astype(int)
    
    return df_join

def _load_table(cur, table_name, columns=None):
    cur.execute(f'SELECT * from {table_name};')
    rows = cur.fetchall()
    
    return(pd.DataFrame(rows, columns=columns))