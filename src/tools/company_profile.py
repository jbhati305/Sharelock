"""
Tool: get_company_profile

Fetches company profile and basic information using yfinance.
Supports both global and Indian markets.
"""

import yfinance as yf


def get_company_profile(ticker: str) -> dict:
    """
    Get company profile and basic information.

    Args:
        ticker: Stock ticker symbol
                - US stocks: 'AAPL', 'GOOGL', 'MSFT'
                - Indian NSE stocks: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'

    Returns:
        Dictionary containing:
        - ticker: Stock symbol
        - name: Company name
        - sector: Business sector
        - industry: Industry classification
        - description: Business description
        - website: Company website
        - country: Country of headquarters
        - city: City of headquarters
        - employees: Number of full-time employees
        - ceo: CEO name (if available)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("quoteType") == "NONE":
            return {
                "error": f"No data found for ticker '{ticker}'. Check the symbol.",
                "ticker": ticker.upper(),
            }

        return {
            "ticker": ticker.upper(),
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary"),
            "website": info.get("website"),
            "country": info.get("country"),
            "city": info.get("city"),
            "state": info.get("state"),
            "employees": info.get("fullTimeEmployees"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "quote_type": info.get("quoteType"),
            "market": info.get("market"),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch company profile for '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }
