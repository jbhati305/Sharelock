"""
Tool: get_nse_stock_price

Fetches current stock price and market data from NSE (National Stock Exchange of India).
Uses nsepython library for reliable data fetching.
"""

from nsepython import nse_eq


def get_nse_stock_price(symbol: str) -> dict:
    """
    Get current stock price and market data for an NSE listed stock.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK')

    Returns:
        Dictionary containing:
        - symbol: Stock symbol
        - company_name: Company name
        - last_price: Last traded price
        - open: Opening price
        - high: Day's high
        - low: Day's low
        - previous_close: Previous close price
        - change: Price change
        - percent_change: Percentage change
        - volume: Total traded volume
        - fifty_two_week_high: 52-week high
        - fifty_two_week_low: 52-week low
    """
    try:
        quote = nse_eq(symbol.upper())

        if not quote or "error" in quote:
            return {
                "error": f"No data found for symbol '{symbol}'. Make sure it's a valid NSE symbol.",
                "symbol": symbol.upper(),
            }

        # Extract price info
        price_info = quote.get("priceInfo", {})
        security_info = quote.get("securityInfo", {})
        info = quote.get("info", {})

        return {
            "symbol": info.get("symbol", symbol.upper()),
            "company_name": info.get("companyName"),
            "industry": info.get("industry"),
            "last_price": price_info.get("lastPrice"),
            "open": price_info.get("open"),
            "high": price_info.get("intraDayHighLow", {}).get("max"),
            "low": price_info.get("intraDayHighLow", {}).get("min"),
            "previous_close": price_info.get("previousClose"),
            "change": price_info.get("change"),
            "percent_change": price_info.get("pChange"),
            "vwap": price_info.get("vwap"),
            "volume": security_info.get("tradedVolume"),
            "total_buy_quantity": security_info.get("totalBuyQuantity"),
            "total_sell_quantity": security_info.get("totalSellQuantity"),
            "fifty_two_week_high": price_info.get("weekHighLow", {}).get("max"),
            "fifty_two_week_low": price_info.get("weekHighLow", {}).get("min"),
            "upper_band": price_info.get("upperCP"),
            "lower_band": price_info.get("lowerCP"),
            "face_value": security_info.get("faceValue"),
            "currency": "INR",
            "exchange": "NSE",
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch NSE data for symbol '{symbol}': {str(e)}",
            "symbol": symbol.upper(),
        }
