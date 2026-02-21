import os
from dotenv import load_dotenv
from pathlib import Path

# Load env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from mcp.server.fastmcp import FastMCP
from crud import init_db, create_item, read_items, update_item, delete_item

mcp = FastMCP("CRUD MCP Server")


@mcp.tool()
async def add_item(name: str, price: float):
    """Add a new item with auto-generated ID"""
    await init_db()
    result = await create_item({"name": name, "price": price})
    return f"Added item: {result['name']} with price {result['price']} and ID {result['id']}"


@mcp.tool()
async def list_items():
    """List all items"""
    await init_db()
    items = await read_items()
    if not items:
        return "No items found"
    return "\n".join([f"ID: {i['id']}, Name: {i['name']}, Price: {i['price']}" for i in items])


@mcp.tool()
async def edit_item(item_id: str, name: str, price: float):
    """Edit item by ID"""
    await init_db()
    result = await update_item(item_id, {"name": name, "price": price})
    return f"Updated item {result['id']}: {result['name']} - {result['price']}"


@mcp.tool()
async def remove_item(item_id: str):
    """Delete item by ID"""
    await init_db()
    result = await delete_item(item_id)
    return f"Deleted item: {result['name']}"


if __name__ == "__main__":
    mcp.run()
