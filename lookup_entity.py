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

    # sql = """
    # SELECT
    #     program_office,
    #     application,
    #     line_item_usage_account_name
    # FROM cost_data
    # WHERE
    #     LOWER(program_office) = LOWER(?)
    #     OR LOWER(application) = LOWER(?)
    #     OR LOWER(line_item_usage_account_name) = LOWER(?)
    # LIMIT 20
    # """

    # df = con.execute(sql, [name, name, name]).fetchdf()

    # if df.empty:
    #     return {"entity": None, "value": None}

    # name_lower = name.lower()

    # if name_lower in df["program_office"].str.lower().values:
    #     return {"entity": "program_office", "value": name}

    # if name_lower in df["application"].str.lower().values:
    #     return {"entity": "application", "value": name}

    # if name_lower in df["line_item_usage_account_name"].str.lower().values:
    #     return {"entity": "line_item_usage_account_name", "value": name}

    # return {"entity": None, "value": None}