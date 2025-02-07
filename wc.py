from typing import Any, List, Dict
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
WOOCOMMERCE_API_BASE = os.getenv("WOOCOMMERCE_API_BASE")
USER_AGENT = "wc-mcp/1.0"
CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() != "false"

# Initialize FastMCP server
mcp = FastMCP("woocommerce")

async def make_wc_request(method: str, url: str, data=None, params=None) -> dict[str, Any] | None:
    """Make a request to the WooCommerce API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    auth = (CONSUMER_KEY, CONSUMER_SECRET)
    async with httpx.AsyncClient(verify=VERIFY_SSL) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, auth=auth, params=params, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, headers=headers, auth=auth, timeout=30.0)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data, headers=headers, auth=auth, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def wc_list_products() -> List[Dict[str, Any]]:
    """Get a list of products from WooCommerce.
    
    Returns:
        List of products with their details.
    """
    url = f"{WOOCOMMERCE_API_BASE}/products"
    data = await make_wc_request("GET", url)

    if not data:
        return {"error": "Unable to fetch products."}
    
    if isinstance(data, dict) and "error" in data:
        return {"error": f"Error fetching products: {data['error']}"}

    if not data:
        return {"error": "No products found."}

    return [{
        "id": product.get("id"),
        "name": product.get("name"),
        "price": product.get("price"),
        "stock_status": product.get("stock_status"),
        "categories": [cat["name"] for cat in product.get("categories", [])]
    } for product in data]

@mcp.tool()
async def wc_list_orders(status: str = None, after: str = None, before: str = None) -> List[Dict[str, Any]]:
    """Get a list of orders from WooCommerce.
    
    Args:
        status: Filter orders by status (processing, completed, on-hold, etc.)
        after: Show orders after this date (YYYY-MM-DD)
        before: Show orders before this date (YYYY-MM-DD)
    
    Returns:
        Raw WooCommerce API response
    """
    params = {}
    if status:
        params['status'] = status
    if after:
        params['after'] = f"{after}T00:00:00Z"
    if before:
        params['before'] = f"{before}T23:59:59Z"

    url = f"{WOOCOMMERCE_API_BASE}/orders"
    data = await make_wc_request("GET", url, params=params)

    if not data:
        return {"error": "Unable to fetch orders."}
    
    if isinstance(data, dict) and "error" in data:
        return {"error": f"Error fetching orders: {data['error']}"}

    return data

@mcp.tool()
async def wc_get_order(order_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific order.
    
    Args:
        order_id: The ID of the order to retrieve
    
    Returns:
        Raw WooCommerce API response including order details and notes
    """
    url = f"{WOOCOMMERCE_API_BASE}/orders/{order_id}"
    order = await make_wc_request("GET", url)

    if not order:
        return {"error": "Unable to fetch order."}
    
    if isinstance(order, dict) and "error" in order:
        return {"error": f"Error fetching order: {order['error']}"}

    # Fetch notes for the order
    notes_url = f"{WOOCOMMERCE_API_BASE}/orders/{order_id}/notes"
    notes = await make_wc_request("GET", notes_url)
    
    if isinstance(notes, list):
        order['notes'] = notes
    
    return order

@mcp.tool()
async def wc_update_product(product_id: int, name: str = None, regular_price: str = None, 
                          sale_price: str = None, description: str = None) -> Dict[str, Any]:
    """Update a WooCommerce product."""
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if regular_price is not None:
        update_data["regular_price"] = str(regular_price)
    if sale_price is not None:
        update_data["sale_price"] = str(sale_price)
    if description is not None:
        update_data["description"] = description

    url = f"{WOOCOMMERCE_API_BASE}/products/{product_id}"
    response = await make_wc_request("PUT", url, update_data)

    if not response:
        return {"error": "Unable to update product."}

    if isinstance(response, dict) and "error" in response:
        return {"error": f"Error updating product: {response['error']}"}

    return {
        "success": True,
        "product": {
            "id": response.get("id"),
            "name": response.get("name"),
            "status": response.get("status")
        }
    }

@mcp.tool()
async def wc_manage_inventory(product_id: int, stock_quantity: int = None, 
                            stock_status: str = None) -> str:
    """Update inventory for a WooCommerce product.
    
    Args:
        product_id: The ID of the product to update
        stock_quantity: New stock quantity
        stock_status: Stock status (in_stock, out_of_stock, on_backorder)
    
    Returns:
        The result of the inventory update.
    """
    update_data = {}
    if stock_quantity is not None:
        update_data["stock_quantity"] = stock_quantity
    if stock_status is not None:
        update_data["stock_status"] = stock_status

    return await wc_update_product(product_id, **update_data)

# @mcp.tool()
# async def wc_get_reports(report_type: str = "sales", period: str = "all", 
#                         date_min: str = None, date_max: str = None) -> Dict[str, Any]:
#     """Get reports and analytics from WooCommerce."""
#     params = {}
#     
#     if report_type == "sales":
#         url = f"{WOOCOMMERCE_API_BASE}/reports/sales"
#         
#         if date_min and date_max:
#             params.update({
#                 'date_min': f"{date_min}",
#                 'date_max': f"{date_max}",
#                 'period': 'year'
#             })
#         elif period != "all":
#             now = datetime.now()
#             if period == "year":
#                 year = int(date_min[:4]) if date_min else now.year
#                 params.update({
#                     'date_min': f"{year}-01-01",
#                     'date_max': f"{year}-12-31",
#                     'period': 'year'
#                 })
# 
#     data = await make_wc_request("GET", url, params=params)
# 
#     if not data:
#         return {"error": "Unable to fetch reports."}
#     
#     if isinstance(data, dict) and "error" in data:
#         return {"error": f"Error fetching reports: {data['error']}"}
# 
#     return data

@mcp.tool()
async def wc_update_order_status(order_id: int, status: str, note: str = None) -> Dict[str, Any]:
    """Update an order's status and optionally add a note.
    
    Args:
        order_id: The ID of the order to update
        status: New status (pending, processing, completed, on-hold, cancelled, refunded)
        note: Optional note to add to the order
    
    Returns:
        Updated order details
    """
    update_data = {"status": status}
    
    url = f"{WOOCOMMERCE_API_BASE}/orders/{order_id}"
    response = await make_wc_request("PUT", url, update_data)

    if not response:
        return {"error": "Unable to update order."}

    if isinstance(response, dict) and "error" in response:
        return {"error": f"Error updating order: {response['error']}"}

    # Add note if provided
    if note:
        note_url = f"{WOOCOMMERCE_API_BASE}/orders/{order_id}/notes"
        note_data = {
            "note": note,
            "customer_note": False  # Set to True if you want the customer to see this note
        }
        note_response = await make_wc_request("POST", note_url, note_data)
        
        if isinstance(note_response, dict) and "error" in note_response:
            return {
                "warning": f"Order status updated but failed to add note: {note_response['error']}",
                "order": {
                    "id": response.get("id"),
                    "status": response.get("status"),
                    "date_modified": response.get("date_modified")
                }
            }

    return {
        "success": True,
        "order": {
            "id": response.get("id"),
            "status": response.get("status"),
            "date_modified": response.get("date_modified"),
            "note_added": bool(note)
        }
    }

@mcp.tool()
async def wc_add_order_note(order_id: int, note: str, customer_visible: bool = False) -> Dict[str, Any]:
    """Add a note to an order.
    
    Args:
        order_id: The ID of the order
        note: The note content
        customer_visible: Whether the customer can see this note
    
    Returns:
        The created note details
    """
    url = f"{WOOCOMMERCE_API_BASE}/orders/{order_id}/notes"
    data = {
        "note": note,
        "customer_note": customer_visible
    }
    
    response = await make_wc_request("POST", url, data)

    if not response:
        return {"error": "Unable to add note to order."}

    if isinstance(response, dict) and "error" in response:
        return {"error": f"Error adding note: {response['error']}"}

    return {
        "success": True,
        "note": {
            "id": response.get("id"),
            "author": response.get("author", "system"),
            "date": response.get("date_created"),
            "note": response.get("note"),
            "customer_visible": response.get("customer_note", False)
        }
    }

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
