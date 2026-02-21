from mcp.server.fastmcp import FastMCP
from crud import create_item, read_items, update_item, delete_item

mcp = FastMCP("CRUD MCP Server")


@mcp.tool()
def add_item(name: str, price: float):
    """Add a new item with auto-generated ID"""
    return create_item({"name": name, "price": price})


@mcp.tool()
def list_items():
    """List all items"""
    return read_items()


@mcp.tool()
def edit_item(item_id: str, name: str, price: float):
    """Edit item by ID"""
    return update_item(item_id, {"name": name, "price": price})


@mcp.tool()
def remove_item(item_id: str):
    """Delete item by ID"""
    return delete_item(item_id)


if __name__ == "__main__":
    mcp.run()
