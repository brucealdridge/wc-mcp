# WooCommerce MCP Server

A MCP (Multi-Command Protocol) server for interacting with WooCommerce. This server provides tools to fetch and manage WooCommerce products and other data.

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r wc-server-python/requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your WooCommerce settings in the `.env` file:
   ```plaintext
   WOOCOMMERCE_API_BASE=your_site_url/wp-json/wc/v3
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

## Usage

Run the server:
```bash
python wc-server-python/wc.py
```

The server will start and listen for MCP commands via standard input/output.

## Development

To add new WooCommerce API endpoints, extend the server by adding new tools using the `@mcp.tool()` decorator in `wc.py`.
