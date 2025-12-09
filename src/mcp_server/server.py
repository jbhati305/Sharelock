"""
MCP Server for Stock Market Analysis Tools.

This server provides tools for fetching stock market data,
company fundamentals, and financial analysis.
Focused on Indian Markets (NSE).
"""

from mcp.server.fastmcp import FastMCP

from src.tools import (
    # Market Data Tools
    get_stock_price,
    get_historical_data,
    get_nse_stock_price,
    # Company Fundamentals Tools
    get_company_profile,
    get_financial_ratios,
    get_trade_info,
    get_corporate_actions,
)

# Initialize MCP server
mcp = FastMCP("Sharelock Stock Analysis")

# Register Market Data Tools
mcp.tool()(get_stock_price)
mcp.tool()(get_historical_data)
mcp.tool()(get_nse_stock_price)

# Register Company Fundamentals Tools
mcp.tool()(get_company_profile)
mcp.tool()(get_financial_ratios)
mcp.tool()(get_trade_info)
mcp.tool()(get_corporate_actions)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
