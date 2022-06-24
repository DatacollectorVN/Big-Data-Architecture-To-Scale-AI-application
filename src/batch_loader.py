import os
from PIL import Image
from tqdm import tqdm
from src.utils import get_date_capture_img, down_load_file_s3_folder, extract_img_size, convert_bbox_xyxy_to_xywh, compute_area

class SettingConfig(object):
    def __init__(self, **args):
        for key in args:
            setattr(self, key, args[key])

class BatchLoader(SettingConfig):
    def __init__(self, **args):
        super(BatchLoader, self).__init__(**args)
    
    def batch_loading(self, s3_resource, mongocol):
        results = mongocol.find({}, {'_id':0})
        rows = list(results)
        meta_info = rows[0]
        imgs, annotations = self._transform_imgs_annots(s3_resource, rows)

        return imgs, annotations
    
    def _transform_imgs_annots(self, s3_resource, rows):
        imgs = []
        annotations = []
        rows = rows[1:] # skip the first rows cause it is the meta infomation
        for row in tqdm(rows, total = len(rows)):
            # img = _get_img(s3_resource, params, row)
            img = {}
            
            # get image information
            s3_bucket = s3_resource.Bucket(row['bucket'])
            date_capture = get_date_capture_img(row)
            down_load_file_s3_folder(s3_bucket, row['img_file'], row['folder'], os.path.join(self.SAVE_PATH, 'images'))
            img_w, img_h = extract_img_size(os.path.join(self.SAVE_PATH, 'images', row['img_file']))
            img_file_name = row['img_file']
            img_id = row['img_id']

            # update to image dictionary
            img['id'] = img_id
            img['license'] = self.LICENSE
            img['file_name'] = img_file_name
            img['coco_url'] = self.COCO_URL
            img['height'] = img_h
            img['width'] = img_w
            img['date_captured'] = date_capture
            img['flickr_url'] = self.FLICKR_URL

            trans = row['transactions']
            annotations = self._get_annots(annotations, trans, img_id)
            
            # update to images list
            imgs.append(img)
        
        return imgs, annotations
    
    def _get_annots(self, annotations, trans, img_id):
        for tran in trans:
            pred_bboxes = tran['pred_bbox']
            for pred_bbox in pred_bboxes:
                annotation = {}
                category_id = pred_bbox['pred_class']
                bbox_xyxy = pred_bbox['offset_value']
                bbox_xywh = convert_bbox_xyxy_to_xywh(bbox_xyxy)
                area = compute_area(bbox_xywh)
                
                # update to annotation dictionary
                annotation['id'] = pred_bbox['pred_bbox_id']
                annotation['image_id'] = img_id
                annotation['iscrowd'] = self.IS_CROWD
                annotation['category_id'] = category_id
                annotation['segmentation'] = self.SEGMENTATION
                annotation['bbox'] = bbox_xywh
                annotation['area'] = area
                annotation['bbox_mode'] = self.BBOX_MODE

                # update to annotatiosn list
                annotations.append(annotation)
        
        return annotations