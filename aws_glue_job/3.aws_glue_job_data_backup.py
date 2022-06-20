# Stage 3: ETL data from RDS to S3 for backup
'''
    Upload this file into your Amazon Glue Job.
    
'''
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pyspark.sql.functions as F
from awsglue.dynamicframe import DynamicFrame

RDS_HOST = '<RDS_endpoint>'
PORT = 3306
RDS_DB = '<Database_name>'
USER = '<RDS_USER>'
PASSWORD = '<RDS_PASSWORD_USER>'
S3_BUCKET = '<S3_BUCKNET_NAME>'
BACKUP_FOLDER_S3_BUCKET = '<BACKUP_FOLDER_NAME>'

# Setup glueContext and SparkSession
glueContext = GlueContext(SparkContext.getOrCreate())
gluejob = Job(glueContext)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
gluejob.init(args['JOB_NAME'], args)
spark = glueContext.sparkSession

# Extract data from RDS
spark_df_image = spark.read.format('jdbc') \
    .option('url', f'jdbc:mysql://{RDS_HOST}:{PORT}/{RDS_DB}') \
    .option('dbtable', 'image') \
    .option('user', USER) \
    .option('password', PASSWORD) \
    .load()
    
spark_df_tran = spark.read.format('jdbc') \
    .option('url', f'jdbc:mysql://{RDS_HOST}:{PORT}/{RDS_DB}') \
    .option('dbtable', 'transaction') \
    .option('user', USER) \
    .option('password', PASSWORD) \
    .load()

spark_df_pred_bbox = spark.read.format('jdbc') \
    .option('url', f'jdbc:mysql://{RDS_HOST}:{PORT}/{RDS_DB}') \
    .option('dbtable', 'pred_bounding_box') \
    .option('user', USER) \
    .option('password', PASSWORD) \
    .load()

# Transform data
spark_df_join = spark_df_tran.join(spark_df_image, on= 'image_id', how = 'inner') \
    .join(spark_df_pred_bbox, on= 'transaction_id', how = 'inner')
spark_df_join = spark_df_join.sort(F.col('image_id').asc(), F.col('transaction_id').asc(), F.col('pred_bbox_id').asc())
cols = ['image_id', 'transaction_id', 'pred_bbox_id', 'time', 'bucket', 'folder', 'image_file', 'cs_thr', 'nms_thr', 'pred_bbox_id', 'pred_class', 'pred_cs', 'x_min', 'y_min', 'x_max', 'y_max']
spark_df_join = spark_df_join.select(*cols)

# Load data into S3 for backup
dynamic_join = DynamicFrame.fromDF(spark_df_join, glueContext, 'dynamic_frame')
S3bucket_node = glueContext.getSink(
    path=f's3://{S3_BUCKET}/{BACKUP_FOLDER_S3_BUCKET}/',
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=['image_id'])
S3bucket_node.setFormat("csv")
S3bucket_node.writeFrame(dynamic_join)
print('Saved to S3')

# commit job
gluejob.commit()