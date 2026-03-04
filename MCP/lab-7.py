import os
import asyncio
from typing import Any
from mcp.server.fastmcp import FastMCP

class FastMCP:
    """Mock FastMCP server for learning"""
    def __init__(self,name):
        self.name = name
        self.tools = []

    def tool(self):
        """Mock tool decorator"""
        def decorator(func):
            self.tools.append({
                'name': func.__name__,
                'function': func
            })
            return func
        return decorator
    
    def run(self, transport = 'stdio'):
        print(f"🚀 {self.name} MCP server would run with {transport} transport")
        print(f"📦 Available tools: {[t['name'] for t in self.tools]}")

mcp = FastMCP("Calculator")

@mcp.tool()
def add (a:float, b:float) -> float:
    result = a+b
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    result= a * b
    return result


@mcp.tool()
def divide(a: float, b: float) -> str:
    if b == 0:
        return "Error: Cannot divide by zero"
    result = a / b
    return f"{a} ÷ {b} = {result}"

def test_tools():
    """Test MCP tools"""
    result = add(5,98)
    print(f"Response: {result}")

    result = multiply(88, 4)
    print(f"response: {result}")
test_tools()