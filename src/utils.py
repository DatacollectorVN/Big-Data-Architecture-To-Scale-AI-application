import os
from PIL import Image
from tqdm import tqdm

def transform_coco_format(imgs, annotations, params):
    info = {
        'description': 'Dataset with image from user uploaded and annotations from model prediction'
    }
    licenses = [
        {
            'url': 'https://github.com/DatacollectorVN/Chest-Xray-Version3',
            'id': params['LICENSE']
        }
    ]
    categories = []
    for i, class_name in enumerate(params['CLASSES_NAME']):
        category_ = {
            'supercategory': class_name,
            'id': i,
            'name': class_name
        }
        categories.append(category_)
    
    coco_data = {
        'info': info,
        'licenses': licenses,
        'categories': categories,
        'images': imgs,
        'annotations': annotations
    }

    return coco_data
    
def _download_s3_folder(s3_resource, bucket_name, s3_folder, local_dir=None):
    """
    Download the all contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """

    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

def down_load_file_s3_folder(s3_bucket, file_name, s3_folder_name, local_dir=None):
    if local_dir != None:
        s3_bucket.download_file(os.path.join(s3_folder_name, file_name), os.path.join(local_dir, file_name))
    else:
        local_dir = s3_folder_name
        s3_bucket.download_file(os.path.join(s3_folder_name, file_name), os.path.join(local_dir, file_name))

def extract_img_size(img_file_path):
    img = Image.open(img_file_path)
    img_w, img_h = img.size
    
    return (img_w, img_h)

def _get_index_minvalue(inputlist):
 
    #get the minimum value in the list
    min_value = min(inputlist)
 
    #return the index of minimum value 
    min_index=inputlist.index(min_value)
    
    return min_index

def get_date_capture_img(row):
    trans = row['transactions']
    trans_id = [tran['tran_id'] for tran in trans]
    min_index = _get_index_minvalue(trans_id)
    
    # 2022-06-22 02:12:38, so split it to get year-month-date 2022-06-22
    date_capture = trans[min_index]['time'].split(' ')[0]
    
    return date_capture

def convert_bbox_xyxy_to_xywh(bbox_xyxy):
    x_min, y_min, x_max, y_max = bbox_xyxy
    width = x_max - x_min
    height = y_max - y_min
    x_center = round((x_min + x_max) / 2)
    y_center = round((y_min + y_max) / 2)
    return [x_center, y_center, width, height]

def compute_area(bbox_xywh):
    return bbox_xywh[2] * bbox_xywh[3]