import os
import duckdb
import awswrangler as wr
from dotenv import load_dotenv
import boto3

load_dotenv()



s3 = boto3.client('s3')
session = boto3.Session()
creds = session.get_credentials().get_frozen_credentials()

BUCKET = os.getenv("BUCKET")
PREFIX = os.getenv("PREFIX")

S3_PATH = f"s3://{BUCKET}/{PREFIX}"

def load_cost_data(year: int, month: int):
    """Load data for specific partition"""
    df = wr.s3.read_parquet(
        path=S3_PATH,
        dataset=True,
        partition_filter=lambda x: (
            int(x["year"]) == year and int(x["month"]) == month
        )
    )

    return df
