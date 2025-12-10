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
from .company_profile import get_company_profile
from .financial_ratios import get_financial_ratios
from .shareholding_pattern import get_holders_info
from .corporate_actions import get_corporate_actions

__all__ = [
    # Market Data
    "get_stock_price",
    "get_historical_data",
    # Company Fundamentals
    "get_company_profile",
    "get_financial_ratios",
    "get_holders_info",
    "get_corporate_actions",
]
