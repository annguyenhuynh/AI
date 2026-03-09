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

    # partitions = []

    # paginator = s3.get_paginator("list_objects_v2")

    # pages = paginator.paginate(
    #     Bucket=os.getenv("BUCKET"),
    #     Prefix=os.getenv("PREFIX"),
    #     Delimiter='/'
    # )

    # print(os.getenv("BUCKET"))
    # print(os.getenv("PREFIX"))

    # for page in pages:
    #     for year_prefix in page.get("CommonPrefixes", []):
    #         year_path = year_prefix["Prefix"]
    #         year = year_path.split("year=")[1].strip("/")

    #         month_pages = s3.list_objects_v2(
    #             Bucket=os.getenv("BUCKET"),
    #             Prefix=year_path,
    #             Delimiter="/"
    #         )

    #         for month_prefix in month_pages.get("CommonPrefixes", []):
    #             month_path = month_prefix["Prefix"]
    #             month = month_path.split("month=")[1].strip("/")

    #         partitions.append({
    #                 "year": int(year),
    #                 "month": int(month)
    #             })

    # return sorted(partitions)