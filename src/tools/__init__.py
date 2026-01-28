"""
Stock Market Analysis Tools.

All tools use yfinance for data.
For Indian stocks, use .NS suffix (NSE) or .BO suffix (BSE).
Examples: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'
"""

# Market Data Tools
from .stock_price import get_stock_price
from .historical_data import get_historical_data

# Company Fundamentals Tools
from .get_scraped_data import get_scraped_data

__all__ = [
    # Market Data
    "get_stock_price",
    "get_historical_data",
    # Company Fundamentals
    "get_scraped_data",
]

