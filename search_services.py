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
    # query_lower = query.lower().strip()
    
    # results = []
    
    # # 1. AWS Services discovery (your ~100 services)
    # if any(term in query_lower for term in ['service', 'ec2', 's3', 'lambda', 'aws']):
    #     df = con.execute("""
    #         SELECT 
    #             product_servicecode,
    #             COUNT(*) as usage_count,
    #             COUNT(DISTINCT line_item_usage_account_id) as accounts
    #         FROM cost_data 
    #         WHERE product_servicecode IS NOT NULL
    #         GROUP BY product_servicecode
    #         ORDER BY usage_count DESC
    #         LIMIT 15
    #     """).fetchdf()
        
    #     if not df.empty:
    #         results.append({
    #             "type": "aws_services",
    #             "answer": f"Top AWS services used in your data ({len(df)} total services found):",
    #             "data": df.to_dict(orient="records")
    #         })
    
    # # 2. Program Offices
    # if 'program' in query_lower or 'office' in query_lower:
    #     df = con.execute("""
    #         SELECT 
    #             program_office,
    #             COUNT(*) as row_count,
    #             SUM(total_unblended_cost) as total_cost
    #         FROM cost_data 
    #         WHERE program_office IS NOT NULL
    #         GROUP BY program_office
    #         ORDER BY total_cost DESC
    #         LIMIT 10
    #     """).fetchdf()
        
    #     if not df.empty:
    #         results.append({
    #             "type": "program_offices",
    #             "answer": f"Program Offices in your data (by spend):",
    #             "data": df.to_dict(orient="records")
    #         })
    
    # # 3. Applications
    # if 'application' in query_lower:
    #     df = con.execute("""
    #         SELECT 
    #             application,
    #             COUNT(*) as row_count,
    #             SUM(total_unblended_cost) as total_cost
    #         FROM cost_data 
    #         WHERE application IS NOT NULL
    #         GROUP BY application
    #         ORDER BY total_cost DESC
    #         LIMIT 10
    #     """).fetchdf()
        
    #     if not df.empty:
    #         results.append({
    #             "type": "applications",
    #             "answer": f"Applications in your data (by spend):",
    #             "data": df.to_dict(orient="records")
    #         })
    
    # # 4. Accounts
    # if 'account' in query_lower:
    #     df = con.execute("""
    #         SELECT 
    #             line_item_usage_account_name,
    #             COUNT(DISTINCT line_item_usage_account_id) as account_ids,
    #             SUM(total_unblended_cost) as total_cost
    #         FROM cost_data 
    #         WHERE line_item_usage_account_name IS NOT NULL
    #         GROUP BY line_item_usage_account_name
    #         ORDER BY total_cost DESC
    #         LIMIT 10
    #     """).fetchdf()
        
    #     if not df.empty:
    #         results.append({
    #             "type": "accounts",
    #             "answer": f"Top accounts by spend:",
    #             "data": df.to_dict(orient="records")
    #         })
    
    # # 5. Description search (for service-specific questions)
    # service_keywords = ['ec2', 's3', 'lambda', 'rds', 'ebs', 'vpc']
    # if any(kw in query_lower for kw in service_keywords) or 'description' in query_lower:
    #     search_term = query_lower.split()[:2]  # Use first 2 words
    #     df = con.execute(f"""
    #         SELECT 
    #             ,
    #             product_servicecode,
    #             product_usagetype,
    #             COUNT(*) as occurrences
    #         FROM cost_data
    #         WHERE line_item_line_item_description ILIKE '%{search_term[0]}%'
    #            OR product_servicecode ILIKE '%{search_term[0]}%'
    #         GROUP BY line_item_line_item_description, product_servicecode, product_usagetype
    #         ORDER BY occurrences DESC
    #         LIMIT 8
    #     """).fetchdf()
        
    #     if not df.empty:
    #         results.append({
    #             "type": "descriptions",
    #             "answer": "Sample line item descriptions matching your query:",
    #             "data": df.to_dict(orient="records")
    #         })
    
    # # 6. Specific value lookup (e.g. "DAAS program office")
    # for col in ['program_office', 'application', 'product_servicecode']:
    #     if col.replace('_', ' ') in query_lower or any(word in query_lower for word in query_lower.split()[:3]):
    #         df = con.execute(f"""
    #             SELECT DISTINCT {col},
    #                    COUNT(*) as occurrences,
    #                    SUM(total_unblended_cost) as total_spend
    #             FROM cost_data 
    #             WHERE {col} ILIKE '%{query_lower.split()[0]}%'
    #             GROUP BY {col}
    #             ORDER BY total_spend DESC
    #             LIMIT 5
    #         """).fetchdf()
            
    #         if not df.empty:
    #             results.append({
    #                 "type": f"{col}_lookup",
    #                 "answer": f"Matching {col.replace('_', ' ')} values from your data:",
    #                 "data": df.to_dict(orient="records")
    #             })
    
    # if results:
    #     return {
    #         "found": True,
    #         "query": query,
    #         "results": results[:3],  # Top 3 result types max
    #         "total_services": con.execute("SELECT COUNT(DISTINCT product_servicecode) FROM cost_data WHERE product_servicecode IS NOT NULL").fetchone()[0] or 0
    #     }
    
    # return {
    #     "found": False,
    #     "query": query,
    #     "answer": "No matching dimensions found. Try asking about AWS services, Program Offices, Applications, or accounts in your cost data.",
    #     "results": []
    # }


