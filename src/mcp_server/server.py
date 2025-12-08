"""
MCP Server for Stock Market Analysis Tools.

This server provides tools for fetching stock market data,
company fundamentals, and financial analysis.
"""

import yfinance as yf
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Sharelock Stock Analysis")


@mcp.tool()
def get_stock_price(ticker: str) -> dict:
    """
    Get current stock price and market data for a given ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
    #TODO: Add more data what we want to get from the stock market
    Returns:
        Dictionary containing:
        - current_price: Current stock price
        - open: Opening price for the day
        - high: Day's high
        - low: Day's low
        - close: Previous close price
        - volume: Trading volume
        - market_cap: Market capitalization
        - currency: Currency of the stock
        - exchange: Stock exchange
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current/fast info
        fast_info = stock.fast_info

        return {
            "ticker": ticker.upper(),
            "current_price": fast_info.get("lastPrice") or info.get("currentPrice"),
            "open": info.get("open") or fast_info.get("open"),
            "high": info.get("dayHigh") or fast_info.get("dayHigh"),
            "low": info.get("dayLow") or fast_info.get("dayLow"),
            "previous_close": info.get("previousClose") or fast_info.get("previousClose"),
            "volume": info.get("volume") or fast_info.get("lastVolume"),
            "market_cap": info.get("marketCap") or fast_info.get("marketCap"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "Unknown"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "name": info.get("shortName") or info.get("longName"),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch data for ticker '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

