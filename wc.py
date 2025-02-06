from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# Initialize FastMCP server
mcp = FastMCP("woocommerce")

# Constants
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

WOOCOMMERCE_API_BASE = os.getenv("WOOCOMMERCE_API_BASE")
if not WOOCOMMERCE_API_BASE:
    WOOCOMMERCE_API_BASE = "http://localhost:8888/wp-json/wc/v3"
USER_AGENT = "wc-mcp/1.0"

# SSL verification setting
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() != "false"

async def make_wc_request(url: str) -> dict[str, Any] | None:
    """Make a request to the WooCommerce API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    auth = (os.getenv("WOOCOMMERCE_CONSUMER_KEY"), os.getenv("WOOCOMMERCE_CONSUMER_SECRET"))
    async with httpx.AsyncClient(verify=VERIFY_SSL) as client:
        try:
            response = await client.get(url, headers=headers, auth=auth, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def format_product(product: dict) -> str:
    """Format a WooCommerce product into a readable string."""
    return f"""
Name: {product.get('name', 'Unnamed')}
Price: {product.get('price', 'Unavailable')}
Stock Status: {product.get('stock_status', 'unknown')}
Categories: {', '.join(cat['name'] for cat in product.get('categories', []))}
"""

@mcp.tool()
async def wc_list_products() -> str:
    """Get a list of products from WooCommerce.
    
    Returns a formatted string containing product information.
    """
    url = f"{WOOCOMMERCE_API_BASE}/products"
    data = await make_wc_request(url)

    if not data:
        return "Unable to fetch products."
    
    if isinstance(data, dict) and "error" in data:
        return f"Error fetching products: {data['error']}"

    if not data:
        return "No products found."

    products = [format_product(product) for product in data]
    return "\n---\n".join(products)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 