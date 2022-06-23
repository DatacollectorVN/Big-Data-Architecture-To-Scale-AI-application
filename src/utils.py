import os
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

def _down_load_file_s3_folder(s3_bucket, file_name, s3_folder_name, local_dir=None):
    if local_dir != None:
        s3_bucket.download_file(os.path.join(s3_folder_name, file_name), os.path.join(local_dir, file_name))
    else:
        local_dir = s3_folder_name
        s3_bucket.download_file(os.path.join(s3_folder_name, file_name), os.path.join(local_dir, file_name))
