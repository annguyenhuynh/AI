# aggregate_cost.py - 100% DuckDB-FREE
import os
import pandas as pd
import awswrangler as wr
from typing import Any, List, Dict, Literal, Optional
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.getenv("BUCKET")
PREFIX = os.getenv("PREFIX")
S3_PATH = f"s3://{BUCKET}/{PREFIX}"

NUMERIC_COLS = {
    "line_item_unblended_rate", "total_usage_amount", "sp_covered_cost",
    "edp_discount", "spp_discount", "credit_amount", 
    "total_unblended_cost", "total_cost_before_discount", "year", "month"
}

CATEGORICAL_COLS = {
    "line_item_usage_account_id", "program_office", "application",
    "product_product_family", "product_servicecode", "product_usagetype",
    "line_item_line_item_description"
}

def map_metric(user_input: str) -> str:

    text = user_input.lower()

    if "edp" in text or "enterprise discount" in text:
        return "edp_discount"

    if "savings plan discount" in text or "spp" in text:
        return "spp_discount"

    if "savings plan covered" in text or "covered cost" in text:
        return "sp_covered_cost"

    if "credit" in text:
        return "credit_amount"

    if "usage" in text:
        return "total_usage_amount"

    if "rate" in text:
        return "line_item_unblended_rate"

    if "cost" in text or "spend" in text or "spending" in text:
        return "total_unblended_cost"

    return "total_unblended_cost"

def map_agg(user_input: str) -> Literal["sum","avg","min","max","count"]:

    agg_map = {
        "total": "sum",
        "sum": "sum",
        "average": "avg",
        "avg": "avg",
        "maximum": "max",
        "max": "max",
        "minimum": "min",
        "min": "min",
        "count": "count"
    }

    user_input = user_input.lower()

    for key, val in agg_map.items():
        if key in user_input:
            return val

    return "sum"
def query_cost_data(
        metric: str, 
        agg: Literal["sum", "avg", "min", "max", "count"], 
        group_by: Optional[List[str]] = None, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100):
    """Query data on S3 bucket"""
    print("---- COST QUERY DEBUG ----")
    print("Metric:", metric)
    print("Aggregation:", agg)
    print("Filters:", filters)
    print("Group_by:", group_by)

    filters = filters or {}
    
    try:
        df = wr.s3.read_parquet(path=S3_PATH, dataset=True)
        print(f"✅ Loaded {len(df)} rows")
    except Exception as e:
        print(f"❌ S3 Error: {e}")
        # Return empty DataFrame with expected columns
        cols = (group_by or []) + [metric]
        return pd.DataFrame(columns=cols)

    # Apply filters
    for col, val in filters.items():
        if col in df.columns:
            if isinstance(val, list):
                df = df[df[col].isin(val)]
            else:
                df = df[df[col] == val]

    # If DataFrame is empty after filtering, return empty DataFrame
    if df.empty:
        cols = (group_by or []) + [metric]
        return pd.DataFrame(columns=cols)
    
    #----Ensure correct year/month paritions-----#
    if 'year' in filters and 'month' in filters:
        available = df.groupby(['year', 'month']).size().reset_index(name='count')
        print(f"Available partitions: {available.to_dict('records')}")
        if not df[(df['year'] == filters['year']) & (df['month'] == filters['month'])].empty:
            print(f"✅ Found data for {filters['year']}-{filters['month']:02d}")
        else:
            print(f"❌ NO DATA for {filters['year']}-{filters['month']:02d}")
            return pd.DataFrame({"value": [0.0]})  # Return zero instead of 

# Group + aggregate
    if group_by:
        # Avoid aggregating on a column that is also in group_by
        if metric in group_by:
            # use row count instead
            result = df.groupby(group_by).size().reset_index(name="value")
        else:
            result = df.groupby(group_by)[metric].agg(agg).reset_index()
            result = result.rename(columns={metric: "value"})
    else:
        result = pd.DataFrame({"value": [df[metric].agg(agg)]})

    # if group_by:
    #     result = df.groupby(group_by)[metric].agg(agg).reset_index()
    #     result = result.rename(columns={metric: "value"})
    # else:
    #     result = pd.DataFrame({"value": [df[metric].agg(agg)]})

    # Sort + limit
    result = result.sort_values("value", ascending=False).head(limit)

    return result