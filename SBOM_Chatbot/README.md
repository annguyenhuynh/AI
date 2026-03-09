* This is an LLM project that use MCP tools to answer clients' questions regarding AWS cost data
* The chatbot uses AWS Bedrock Claude Sonnet 3.7
* The model read data in S3 directly using aws wrangler
* The source data is produced by a pipeline that runs on the 2nd day of everymonth. The data is written into csv format for data analytics purpose and parquet files for chatbot and dashboard purposes
