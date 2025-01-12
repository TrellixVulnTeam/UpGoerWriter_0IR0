import os
import tarfile

import boto3

import dotenv
from pathlib import Path

dotenv.load_dotenv(Path(__file__).parent / ".env")

LOCAL_MODEL_DIR = os.environ["LOCAL_MODEL_DIR"]
S3_BUCKET = os.environ["S3_BUCKET"]


def download_model_from_s3(model_name: str, local_path: str) -> str:
    if not os.path.exists(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    local_compressed = f"{local_path}.tar.gz"

    # download model is the archive doesn't exist
    if not os.path.exists(local_compressed):
        print("Downloading model...")
        s3_prefix = f"models/{model_name}.tar.gz"
        s3 = boto3.client("s3")
        s3.download_file(S3_BUCKET, s3_prefix, local_compressed)

    with tarfile.open(local_compressed) as f:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f, path=local_path)

    return local_path


def get_model_path(model_name):
    local_path = os.path.join(LOCAL_MODEL_DIR, model_name)
    if os.path.exists(local_path):
        return local_path
    return download_model_from_s3(model_name, local_path)
