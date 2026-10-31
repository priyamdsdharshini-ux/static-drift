# Bonus: same agent, but triage/specialist tools are fetched from the MCP server at runtime.
# Terminal 1: python mcp_server.py     Terminal 2: python agent_mcp.py
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from llm import create_llm
from shared_tools import search_reference
from system_prompts import SYSTEM_PROMPT

async def main():
    client = MultiServerMCPClient(
        {"medical": {"url": "http://localhost:8001/mcp", "transport": "streamable_http"}}
    )
    mcp_tools = await client.get_tools()
    print("Tools fetched from MCP:", [t.name for t in mcp_tools])

    agent = create_agent(
        model=create_llm(),
        tools=[search_reference, *mcp_tools],
        system_prompt=SYSTEM_PROMPT
    )

    while True:
        q = input("\nAsk (or 'quit'): ")
        if q.lower() == "quit":
            break
        response = await agent.ainvoke({"messages": [{"role": "user", "content": q}]})
        print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
