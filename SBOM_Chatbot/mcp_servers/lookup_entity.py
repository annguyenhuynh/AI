import boto3
import os
import awswrangler as wr
import duckdb
from dotenv import load_dotenv
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


s3 = boto3.client('s3')
session = boto3.Session()
creds = session.get_credentials().get_frozen_credentials()

BUCKET = os.getenv("BUCKET")
PREFIX = os.getenv("PREFIX")
S3_PATH = f"s3://{BUCKET}/{PREFIX}"

def lookup_entity(name: str) -> Dict[str, Optional[str]]:
    """
    Identify whether a name belongs to:
    - program_office
    - application
    - line_item_usage_account_name
    """
    df = wr.s3.read_parquet(
        path=S3_PATH,
        dataset=True,
        columns=[
            "program_office",
            "application",
            "line_item_usage_account_name"
        ]
    )

    name_lower = name.lower()

    for col in df.columns:

        values = df[col].dropna().astype(str).unique()

        for v in values:
            if name_lower in v.lower():
                return {
                    "entity": col,
                    "value": v
                }

    return {"entity": None}
