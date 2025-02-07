# WooCommerce MCP Server

A MCP (Multi-Command Protocol) server for interacting with WooCommerce. This server provides tools to fetch and manage WooCommerce products and other data.

## Installation

```
uv venv 
source .venv/bin/activate 
uv pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your WooCommerce settings in the `.env` file:
   ```plaintext
   WOOCOMMERCE_API_BASE=http://your_site_url.com/wp-json/wc/v3
   WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
   WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret
   ```

### Obtaining API Credentials

1. **Log into WooCommerce Admin**:
   - Navigate to `WooCommerce > Settings`
   - Click on the `Advanced` tab
   - Go to `REST API`

2. **Create a New Key**:
   - Click `Add Key`
   - Fill in the Description and grant `Read/Write` permissions
   - Click `Generate API Key`

3. **Copy Your Keys**:
   - Save the generated `Consumer Key` and `Consumer Secret`
   - Add these to your `.env` file

## Available Tools

The server provides the following MCP tools:

- `wc_list_products`: Fetches and displays a list of WooCommerce products
- `wc_list_orders`: Fetches and displays a list of WooCommerce orders
- `wc_get_order`: Fetches detailed information about a specific WooCommerce order
- `wc_update_product`: Updates product details
- `wc_manage_inventory`: Updates inventory for a WooCommerce product
- `wc_update_order_status`: Updates the status of a WooCommerce order
- `wc_add_order_note`: Adds a note to a WooCommerce order

## Usage

*Goose CLI*
```bash
goose session --with-extension "uv --directory /path/to/wp-mcp run wc.py"
```

*Claude*

Add the following to your `claude_desktop_config.json`:

```
{
  "mcpServers": {
    "wordpress": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/wp-mcp",
        "run",
        "wc.py"
      ]
    }
  }
}
```
