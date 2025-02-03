from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("wordpress")

# Constants
WP_API_BASE = "http://localhost:8888/wp-json/wp/v2"
USER_AGENT = "wp-mcp/1.0"

async def make_wp_request(url: str) -> dict[str, Any] | None:
    """Make a request to the WordPress API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def format_post(post: dict) -> str:
    """Format a WordPress post into a readable string."""
    return f"""
Title: {post.get('title', {}).get('rendered', 'Untitled')}
Status: {post.get('status', 'unknown')}
Date: {post.get('date', 'unknown')}
Link: {post.get('link', 'unknown')}
Excerpt: {post.get('excerpt', {}).get('rendered', 'No excerpt available').strip()}
"""

def format_page(page: dict) -> str:
    """Format a WordPress page into a readable string."""
    return f"""
Title: {page.get('title', {}).get('rendered', 'Untitled')}
Status: {page.get('status', 'unknown')}
Date: {page.get('date', 'unknown')}
Link: {page.get('link', 'unknown')}
Parent: {page.get('parent', 0)}
Menu Order: {page.get('menu_order', 0)}
"""

@mcp.tool()
async def wp_list_posts() -> str:
    """Get a list of public posts from WordPress.
    
    Returns a formatted string containing post information.
    """
    url = f"{WP_API_BASE}/posts"
    data = await make_wp_request(url)

    if not data:
        return "Unable to fetch posts."
    
    if isinstance(data, dict) and "error" in data:
        return f"Error fetching posts: {data['error']}"

    if not data:
        return "No posts found."

    posts = [format_post(post) for post in data]
    return "\n---\n".join(posts)

@mcp.tool()
async def wp_list_pages() -> str:
    """Get a list of pages from WordPress.
    
    Returns a formatted string containing page information.
    """
    url = f"{WP_API_BASE}/pages"
    data = await make_wp_request(url)

    if not data:
        return "Unable to fetch pages."
    
    if isinstance(data, dict) and "error" in data:
        return f"Error fetching pages: {data['error']}"

    if not data:
        return "No pages found."

    pages = [format_page(page) for page in data]
    return "\n---\n".join(pages)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 