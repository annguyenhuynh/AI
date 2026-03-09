import os
import boto3
import awswrangler as wr
from dotenv import load_dotenv

load_dotenv()


s3 = boto3.client('s3')

BUCKET = os.getenv("BUCKET")
PREFIX = os.getenv("PREFIX")
S3_PATH = f"s3://{BUCKET}/{PREFIX}"

def list_partitions():
    """Return list of year/month partitions"""

    partitions = wr.s3.read_parquet_metadata(
        path=S3_PATH,
        dataset=True
    )["partitions"]

    return partitions
