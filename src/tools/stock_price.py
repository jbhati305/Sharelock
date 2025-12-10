"""
Tool: get_stock_price

Fetches current stock price and market data.
Supports both global markets and Indian NSE stocks.

For Indian NSE stocks, use the .NS suffix (e.g., 'RELIANCE.NS', 'TCS.NS')
For Indian BSE stocks, use the .BO suffix (e.g., 'RELIANCE.BO')
"""

import yfinance as yf


def get_stock_price(ticker: str) -> dict:
    """
    Get current stock price and market data for a given ticker symbol.

    Args:
        ticker: Stock ticker symbol
                - US stocks: 'AAPL', 'GOOGL', 'MSFT'
                - Indian NSE stocks: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'
                - Indian BSE stocks: 'RELIANCE.BO', 'TCS.BO'

    Returns:
        Dictionary containing:
        - ticker: Stock symbol
        - current_price: Current stock price
        - open: Opening price for the day
        - high: Day's high
        - low: Day's low
        - previous_close: Previous close price
        - volume: Trading volume
        - market_cap: Market capitalization
        - currency: Currency (USD, INR, etc.)
        - exchange: Stock exchange
        - fifty_two_week_high: 52-week high
        - fifty_two_week_low: 52-week low
        - name: Company name
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        fast_info = stock.fast_info

        return {
            "ticker": ticker.upper(),
            "current_price": fast_info.get("lastPrice") or info.get("currentPrice") or info.get("regularMarketPrice"),
            "open": info.get("open") or info.get("regularMarketOpen"),
            "high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "low": info.get("dayLow") or info.get("regularMarketDayLow"),
            "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "average_volume": info.get("averageVolume"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "Unknown"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "name": info.get("shortName") or info.get("longName"),
            "quote_type": info.get("quoteType"),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch data for ticker '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }
