import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.mcp import MCPServerStdio
import os
from dotenv import load_dotenv, find_dotenv

# Load env
load_dotenv(find_dotenv())

# Global MCP server and agent
mcp_server = None
agent = None


class ItemInput(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str
    price: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_server, agent

    # Setup Gemini client
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    # Model
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=external_client,
    )

    # MCP Server
    mcp_server = MCPServerStdio(
        {
            "command": "uv",
            "args": ["run", "python", "mcpserver.py"],
        }
    )

    # Connect to MCP server
    await mcp_server.connect()

    # Agent
    agent = Agent(
        name="MCP CRUD Assistant",
        model=llm_model,
        mcp_servers=[mcp_server],
        instructions="You are an intelligent CRUD assistant. Use MCP tools for all CRUD actions. Store and read data only via MCP. Data is stored in data.json. Be concise and helpful.",
    )

    yield

    # Cleanup
    if mcp_server:
        await mcp_server.__aexit__(None, None, None)


app = FastAPI(title="MCP Chatbot API", lifespan=lifespan)


@app.post("/items")
async def create_item(item: ItemInput):
    """Add a new item via MCP agent"""
    result = await Runner.run(
        starting_agent=agent,
        input=f"add item with name '{item.name}' and price {item.price}",
    )
    return {"message": "Item created", "response": result.final_output}


@app.get("/items")
async def list_items():
    """List all items via MCP agent"""
    result = await Runner.run(
        starting_agent=agent,
        input="list all items",
    )
    return {"items": result.final_output}


@app.put("/items/{item_id}")
async def update_item(item_id: str, item: ItemUpdate):
    """Update an item by ID via MCP agent"""
    result = await Runner.run(
        starting_agent=agent,
        input=f"update item with id '{item_id}' to name '{item.name}' and price {item.price}",
    )
    return {"message": "Item updated", "response": result.final_output}


@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    """Delete an item by ID via MCP agent"""
    result = await Runner.run(
        starting_agent=agent,
        input=f"delete item with id '{item_id}'",
    )
    return {"message": "Item deleted", "response": result.final_output}


@app.post("/chat")
async def chat(message: str):
    """Send a chat message to the MCP agent"""
    result = await Runner.run(
        starting_agent=agent,
        input=message,
    )
    return {"response": result.final_output}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
