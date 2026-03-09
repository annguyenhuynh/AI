"""
Service Search Tool - Dynamically discovers services, Program Offices, Applications, 
etc. directly from your cost data (no hardcoding needed).
"""

import os
import duckdb
from typing import Dict, List, Any, Optional
import boto3
from dotenv import load_dotenv
load_dotenv()
import awswrangler as wr
s3 = boto3.client('s3')
session = boto3.Session()
creds = session.get_credentials().get_frozen_credentials()

# con = duckdb.connect()
# # Install/load S3 support once
# con.execute("INSTALL httpfs;")
# con.execute("LOAD httpfs;")

# # Reuse the SAME creds boto3 is using (no printing, no hard‑coding)
# con.execute("SET s3_region='us-gov-west-1';")
# con.execute("SET s3_endpoint='s3.us-gov-west-1.amazonaws.com';")
# con.execute("SET s3_url_style='path';")
# con.execute("SET s3_use_ssl=true;")
# con.execute(f"SET s3_access_key_id='{creds.access_key}';")
# con.execute(f"SET s3_secret_access_key='{creds.secret_key}';")
# if creds.token:
#     con.execute(f"SET s3_session_token='{creds.token}';")
BUCKET = os.getenv("BUCKET")
PREFIX = os.getenv("PREFIX")
S3_PATH = f"s3://{BUCKET}/{PREFIX}"

def search_service(query: str) -> Dict[str, Any]:
    """
    Answers non-math questions by querying your actual cost data.
    Discovers all ~100 AWS services dynamically from product_servicecode.
    
    Args:
        query: "What AWS services do we use?", "Show EC2 costs", "DAAS program office", etc.
    """

    df = wr.s3.read_parquet(
        path=S3_PATH,
        dataset=True,
        columns=["product_servicecode", "product_usagetype"]
    )

    query = query.lower()

    results = []

    for col in df.columns:
        matches = df[col].dropna().astype(str)

        matches = matches[matches.str.lower().str.contains(query)]

        results.extend(matches.unique().tolist())

    return {
        "found": len(results) > 0,
        "results": results[:20],
        "answer": "No matches found"
    }
