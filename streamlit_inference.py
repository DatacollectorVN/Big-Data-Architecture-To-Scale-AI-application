import os
import yaml
from PIL import Image
import torch
import numpy as np
from src.utils import detectron2_prediction, get_outputs_detectron2, draw_bbox_infer, config, update_data_to_data_lake
from detectron2.engine import  DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
import streamlit as st
import time
import boto3
import pymysql
from detectron2.utils.logger import setup_logger
setup_logger()
import logging
logger = logging.getLogger("detectron2")
import sys

s3_resource = None
rds_client = None
INI_FILE_PATH = os.path.join('IAC', 'credential_aws_sample.ini')
SECTION_RDS = 'Credential-AWS-RDS-MySQL'
SECTION_S3 = 'Credential-AWS-S3'
SECTION_INFO_S3 = 'Info-AWS-S3'

FILE_INFER_CONFIG = os.path.join("config", "inference.yaml")
with open(FILE_INFER_CONFIG) as file:
    params = yaml.load(file, Loader = yaml.FullLoader)

@st.cache(hash_funcs = {torch.nn.parameter.Parameter: lambda _: None}, ttl = 300)
def load_model(cfg):
    return DefaultPredictor(cfg)

def setup_config_infer(params):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(params["MODEL"]))
    cfg.OUTPUT_DIR = params["OUTPUT_DIR"]
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, params["TRANSFER_LEARNING"])
    cfg.DATALOADER.NUM_WORKERS = 0
    cfg.MODEL.DEVICE = params["DEVICE"]
    if "retina" in params["MODEL"]:
        cfg.MODEL.RETINANET.SCORE_THRESH_TEST = params["SCORE_THR"]
        cfg.MODEL.RETINANET.NUM_CLASSES = params["NUM_CLASSES"]
        cfg.MODEL.RETINANET.NMS_THRESH_TEST = params["NMS_THR"]
    else:
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = params["SCORE_THR"]
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = params["NUM_CLASSES"]
        cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = params["NMS_THR"]

    return cfg

def main():
    # UI of website
    st.header("**CHEST X-RAY VERSION3**")
    st.write("by Nathan Ngo")
    st.write("Read carefully the [instructions](https://github.com/DatacollectorVN/Chest-Xray-Version2/tree/master/website-streamlit) of that model")
    st.write("If you don't have the X-ray image, click [here](https://drive.google.com/drive/folders/1HnTG2LXkltJOFPdVNYx8JplI8phUqpSK?usp=sharing) to download")
    file = st.sidebar.file_uploader('Upload img file (JPG/PNG format)')
    params["SCORE_THR"] = st.sidebar.number_input("Confidence Score Threshold", min_value = 0.0, max_value = 11.0, format = "%f", value = 0.5)
    params["NMS_THR"] = st.sidebar.number_input("IOU NMS Threshold", min_value = 0.0, max_value = 1.0, format = "%f", value = 0.5, )
    if not file:
        st.write("Please upload your image (JPG/PNG format)")
        return
    
    cfg = setup_config_infer(params)
    model = load_model(cfg)
    image_file = Image.open(file)
    image = np.array(image_file.convert("RGB"))
    col_1, col_2 = st.columns([1, 1])
    col_1.write("Orginal image")
    col_1.image(image)
    start = time.time()
    outputs = detectron2_prediction(model, image)
    duration = time.time() - start
    pred_bboxes, pred_confidence_scores, pred_classes = get_outputs_detectron2(outputs)
    pred_bboxes = pred_bboxes.detach().numpy().astype(int)
    pred_confidence_scores = pred_confidence_scores.detach().numpy()
    pred_confidence_scores = np.round(pred_confidence_scores, 2)
    pred_classes = pred_classes.detach().numpy().astype(int)
    img_after = draw_bbox_infer(image, pred_bboxes, 
                                pred_classes, pred_confidence_scores,
                                params["CLASSES_NAME"], params["COLOR"], 5)
    col_2.write(f"Image after (duration: {duration:.3f})")
    col_2.image(img_after)
    update_data_to_data_lake(rds_client, s3_resource, aws_s3_info, pred_confidence_scores, pred_classes, pred_bboxes,
                             image_file, file.name, params["SCORE_THR"], params["NMS_THR"])

if __name__ == "__main__":
    if (s3_resource is None) & (rds_client is None):
        aws_s3_info = config(INI_FILE_PATH, SECTION_INFO_S3)
        aws_s3_config = config(INI_FILE_PATH, SECTION_S3)
        session = boto3.Session(**aws_s3_config)
        s3_resource = session.resource('s3')
        aws_rds_config = config(INI_FILE_PATH, SECTION_RDS)
        rds_client = pymysql.connect(**aws_rds_config)
    
    if os.path.isdir(params["OUTPUT_DIR"]):
        main()