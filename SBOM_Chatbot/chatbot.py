from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Dict, Annotated, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.messages import SystemMessage
from langchain_aws import ChatBedrock
from pydantic import BaseModel, Field
from typing import Optional, Literal, TypedDict
import os
import sys
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_servers'))
from aggregate_cost import query_cost_data, NUMERIC_COLS, CATEGORICAL_COLS, map_metric, map_agg
from search_services import search_service
from load_cost_data import load_cost_data
from list_partitions import list_partitions
from lookup_entity import lookup_entity
from dotenv import load_dotenv
import re

load_dotenv()

#-----Datetime check-----#
def parse_time_filters(user_input: str, filters: dict):
    """Convert phrases like 'last month' into year/month filters"""
    now = datetime.utcnow()
    text = user_input.lower()
    if "last month" in text:
        month = now.month - 1
        year = now.year
        if month == 0:
            month = 12
            year -= 1
        filters["year"] = year
        filters["month"] = month

    return filters

#-----Bedrock chat Model-----#
llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL_ID"),
    region_name="us-gov-west-1",
    model_kwargs={
        "temperature": 0.0, 
        "max_tokens": 3000,
        "anthropic_version": "bedrock-2023-05-31",
    }
)

class QueryCostDataInput(BaseModel):
    metric: str
    agg: Literal["sum","avg","min","max","count"]
    filters: Optional[dict] = None
    group_by: Optional[List[str]] = None
    limit: int = 100

class SearchServiceInput(BaseModel):
    query: str = Field(..., description="Natural language question about data dimensions")

class LoadCostDataInput(BaseModel):
    year: int=Field(..., description="Years like 2006")
    month: int=Field(..., description="Months like 1-12")

class ListPartitionInput(BaseModel):
    """No parameters - lists all available partitions"""
    pass

class LookupEntityInput(BaseModel):
    name: str=Field(..., description="Name of program office, application, or account" )



def call_query_cost_data(
    metric: str,
    agg: Literal["sum", "avg", "min", "max", "count"],
    filters: Optional[dict] = None,
    group_by: Optional[List[str]] = None,
    limit: int = 100,
) -> str:
    """Query cost"""
    filters = filters or {}

    df_result = query_cost_data(
        metric=metric,
        agg=agg,
        group_by=group_by,
        filters=filters,
        limit=limit,
    )

    if isinstance(df_result, str):
        return df_result

    return f"💰 {metric} {agg}:\n```\n{df_result.to_dict(orient='records')}\n```"



def call_search_service(query:str) -> str:
    """Search for AWS services"""
    result = search_service(query)
    if result["found"]:
        return (f"EXPLORATION: '{query}'\n```\n{result['results']}\n```")
    return f"{result['answer']}"

def call_load_cost_data(year: int, month: int) -> str:
    """Load cost data if no aggregation needed"""
    df = load_cost_data(year=year, month=month)
    return f"LOADED: {year}-{month:02d} ({len(df)} rows)\n```\n{df.head(3).to_dict()}\n... {len(df)-3} more\n```"

def call_list_partition() -> str:
    """List all existing partitions in S3"""
    partitions = list_partitions()
    return f"PARTITIONS: {len(partitions)} available:\n```\n{partitions[:20]}{'...' if len(partitions) > 20 else ''}\n```"

def call_lookup_entity(name:str) -> str:
    """Look up a program office, an account name, or an application"""
    result = lookup_entity(name)
    if result["entity"] is None:
        return f"ENTITY NOT FOUND: {name}"

    return f"""
        ENTITY IDENTIFIED
        name: {name}
        entity_type: {result['entity']}
        value: {result['value']}
        """

# Bind all 4 tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "call_query_cost_data",
            "description": "ALL spending, cost, usage, discounts, top N analysis",
            "parameters": QueryCostDataInput.model_json_schema()
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "call_search_service",
            "description": "Explore data dimensions: services, applications, program offices",
            "parameters": SearchServiceInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_load_cost_data",
            "description": "Load specific year-month (rare - usually not needed)",
            "parameters": LoadCostDataInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_list_partitions",
            "description": "List available data partitions (data availability only)",
            "parameters": ListPartitionInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_lookup_entity",
            "description": "Identify program_office/application/account names BEFORE cost queries",
            "parameters": LookupEntityInput.model_json_schema()
        }
    }
]

lll_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Nodes
def agent(state: AgentState):
    """Agent node"""
    return {"messages": [lll_with_tools.invoke(state['messages'])]}


# tool_node = ToolNode([
#     call_query_cost_data,
#     call_search_service,
#     call_load_cost_data,
#     call_list_partition,
#     call_lookup_entity
# ])
def execute_tools(state: AgentState):
    """Execute tool calls"""
    try:
        messages = state['messages']
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": [AIMessage(content="No tools to execute")]}
        
        results = []
        for tool_call in last_message.tool_calls:
            func_name = tool_call['name']
            args = tool_call['args']
            
            print(f"🛠️ Calling {func_name} with {args}")
            
            # Map to your functions
            if func_name == "call_query_cost_data":
                result = call_query_cost_data(**args)
            elif func_name == "call_search_service":
                result = call_search_service(**args)
            elif func_name == "call_load_cost_data":
                result = call_load_cost_data(**args)
            elif func_name == "call_list_partition":
                result = call_list_partition()
            elif func_name == "call_lookup_entity":
                result = call_lookup_entity(**args)
            else:
                result = f"Unknown tool: {func_name}"
            
            print(f"🛠️ Result: {result[:200]}...")
            results.append(ToolMessage(
                content=result,
                tool_call_id=tool_call['id']
            ))
        
        return {"messages": results}
    
    except Exception as e:
        print(f"❌ Tool error: {e}", file=sys.stderr)
        return {"messages": [ToolMessage(content=f"Tool failed: {str(e)}")]}

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent)
workflow.add_node("tools", execute_tools)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent",tools_condition)
# workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "agent")

app = workflow.compile()

#----ROUTING INSTRUCTIONS-----#
system_prompt = f"""
You are an AWS Cost Analysis assistant. Use the tools to answer questions about cost and usage.

DATA SOURCE
- All data comes from AWS CUR parquet files stored in S3.
- Queries are executed via Python tools.
- Do NOT guess numbers. All numeric answers must come from tools.

TOOLS

1) lookup_entity(name)
- Use WHEN the user mentions a name that could be a program_office, application, or account.
- Returns: entity_type (one of "program_office", "application", "line_item_usage_account_name") and value.
- Always call this BEFORE any cost query that refers to a named entity.

2) query_cost_data(metric, agg, group_by=None, filters=None, limit=100)
- Use for ALL numeric questions: spending, cost, usage, rates, discounts, "top N", etc.
- metric: one of {', '.join(sorted(NUMERIC_COLS))}
- agg: sum, avg, min, max, count

3) list_partitions()
- Use ONLY for data availability questions: "what months exist?", "what partitions do we have?"

4) load_cost_data(year, month)
- Use ONLY when you need to load a specific year/month partition explicitly (rare; cost_data usually already has everything loaded).

METRIC CHOICES
- If user asks about "spend", "spending", "total cost" and does not specify, use metric="total_unblended_cost", agg="sum".
- For "usage", use metric="total_usage_amount".
- For "rate", use metric="line_item_unblended_rate".
- For discount/savings questions, use one of: edp_discount, spp_discount, credit_amount, sp_covered_cost.

DIMENSIONS (can be used in filters or group_by):
{', '.join(sorted(CATEGORICAL_COLS))}

SERVICE DIMENSION
- AWS services are identified by: product_servicecode
- When grouping services, ALWAYS use group_by=["product_servicecode"]

CURRENT DATA: Only February 2026 (year=2026, month=2) available
- "Last month" = 2026-02
- Do not use 2024/2025 dates

ROUTING RULES
1. If question involves cost, spending, usage, top N, or percentages → CALL query_cost_data.
2. If question involves "what is X" or "what applications/services/offices exist" → CALL search_service.
3. If question mentions a name (e.g. PIEE) and you are not sure what it is → CALL lookup_entity(name) first, then pass its entity_type/value into filters for query_cost_data.
4. If question is about available months or partitions → CALL list_partitions.
5. Never invent filters or metrics. Derive them from the question and the rules above.

EXAMPLE PLANS (do not echo, just follow pattern)
- "What is PIEE spending last month?"
  • Call lookup_entity("PIEE") → e.g. program_office="PIEE"
  • Determine time range from "last month" using today's date.
  • Call query_cost_data(metric="total_unblended_cost", agg="sum", filters=..., group_by=None)

- "Top 5 services by cost for DAAS in 2026"
  • lookup_entity("DAAS") → program_office="DAAS"
  • query_cost_data(metric="total_unblended_cost", agg="sum", group_by=["product_servicecode"], filters={{"program_office": "DAAS", "year": 2026}}, limit=5)
"""


def chat(user_input: str, chat_history: List[BaseMessage] = None):
    """User chat interface"""
    # messages = chat_history or []
    messages = [SystemMessage(content=system_prompt)] + (chat_history or [])
    messages.append(HumanMessage(content=user_input))
    # messages.append(HumanMessage(content=f"{system_prompt}\n\nQ: {user_input}"))

    # Let LangGraph + tools_condition drive tool calling
    result = app.invoke({"messages": messages})
    last = result["messages"][-1]
    return last.content if isinstance(last, AIMessage) else str(last), result["messages"]

if __name__ == "__main__":
    print("🎯 AWS COST ANALYST - ALL 4 TOOLS LIVE!")
    print("📊 query_cost_data | 🔍 search_service | 📥 load_cost_data | 📁 list_partitions")
    print("=" * 70)
    
    history = []
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            if user_input.lower() in ['quit', 'exit', '/clear']:
                if user_input.lower() == '/clear':
                    history = []
                    print("🧹 History cleared!")
                else:
                    print("👋 Thanks for using Cost Analyst!")
                break
            
            response, history = chat(user_input, history)
            print(f"\n🤖 Analyst: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Check: pip install langgraph langchain-aws pydantic")
