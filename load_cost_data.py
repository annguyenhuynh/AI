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

    # con = duckdb.connect()

    # # Reuse the SAME creds boto3 is using (no printing, no hard‑coding)
    # con.execute("SET s3_region='us-gov-west-1';")
    # con.execute("SET s3_endpoint='s3.us-gov-west-1.amazonaws.com';")
    # con.execute("SET s3_url_style='path';")
    # con.execute("SET s3_use_ssl=true;")
    # con.execute(f"SET s3_access_key_id='{creds.access_key}';")
    # con.execute(f"SET s3_secret_access_key='{creds.secret_key}';")
    # if creds.token:
    #     con.execute(f"SET s3_session_token='{creds.token}';")

    # path = f"{S3_PATH}/year={year}/month={month}/*.parquet"

    # query = f"""
    #     SELECT *
    #     FROM read_parquet(
    #         's3://{BUCKET}/{PREFIX}year={year}/month={month}/*.parquet',
    #         hive_partitioning=1
    #     )
    # """
    
    # df = con.execute(query).fetchdf()

    # return df