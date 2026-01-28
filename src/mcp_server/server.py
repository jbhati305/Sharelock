"""
MCP Server for Stock Market Analysis Tools.

This server provides tools for fetching stock market data,
company fundamentals, and financial analysis.

All tools use yfinance.
For Indian stocks, use .NS suffix (NSE) or .BO suffix (BSE).
"""

from mcp.server.fastmcp import FastMCP

from src.tools import (
    # Market Data Tools
    get_stock_price,
    get_historical_data,
    # Company Fundamentals Tools
    get_scraped_data,
)

# Initialize MCP server
mcp = FastMCP("Sharelock Stock Analysis")

# Register Market Data Tools
mcp.tool()(get_stock_price)
mcp.tool()(get_historical_data)

# Register Company Fundamentals Tools
mcp.tool()(get_scraped_data)



def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
