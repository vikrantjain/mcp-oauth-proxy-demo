import asyncio
from fastmcp import Client

#client = Client("mcp-server.py") # will not work as the server is sync.
client = Client("http://localhost:8000/mcp", auth="oauth")
#client = Client("http://localhost:8000/sse")


async def call_tool(name: str):
    async with client:
        await client.ping()
        result = await client.call_tool("greet", {"name": name})        
        print(result)

async def get_resource():
    async with client:
        result = await client.read_resource("resource://profile")
        print(type(result[0]))
        print(result)

async def get_prompt(topic: str):
    async with client:
        result = await client.get_prompt("ask_about_topic", {"topic": topic})
        print(type(result))
        print(result)

asyncio.run(call_tool("Vikrant"))

asyncio.run(get_resource())

asyncio.run(get_prompt("AI"))