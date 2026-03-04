import os
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# -----------------------------
# Initialize LLM
# -----------------------------
model = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0
)

# -----------------------------
# Configure MCP servers
# -----------------------------
client = MultiServerMCPClient(
    {
        "calculator": {
            "command": "python3", 
            "args": ["mcp_servers/calculator.py"],
            "transport": "stdio",
        },
        "weather": {
            "command": "python3",
            "args": ["mcp_servers/weather_server.py"],
            "transport": "stdio",
        }
    }
)

async def run_agent_with_mcp():
    # Load MCP tools
    tools = await client.get_tools()
    print("✅ Loaded MCP tools:")
    for t in tools:
        print("-", t.name)

    # Create agent
    agent = create_agent(model, tools)

    print("\n=== TEST 1: Calculator add ===")
    add_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What is 25 plus 17?"}]
    })
    print(f"Response: {add_response['messages'][-1].content}")

    print("\n=== TEST 2: Calculator multiply ===")
    multiply_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Calculate 8 times 9"}]
    })
    print(f"Response: {multiply_response['messages'][-1].content}")

    print("\n=== TEST 3: Calculator complex ===")
    complex_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What is (3+5) x 12?"}]
    })
    print(f"Response: {complex_response['messages'][-1].content}")

    print("\n=== TEST 4: General question ===")
    general_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What is the capital of France?"}]
    })
    print(f"Response: {general_response['messages'][-1].content}")

    print("\n=== TEST 5: Weather MCP ===")
    weather_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Compare weather in New York and Tokyo"}]
    })
    print(f"Response: {weather_response['messages'][-1].content}")


# -----------------------------
# Run async function safely
# -----------------------------
if __name__ == "__main__":
    try:
        # Works in terminal
        asyncio.run(run_agent_with_mcp())
    except RuntimeError:
        # If loop already exists (VS Code / Jupyter), use await directly
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_agent_with_mcp())