"""
Tool: get_historical_data

Fetches historical stock price data for a given ticker symbol.
"""

import yfinance as yf


def get_historical_data(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> dict:
    """
    Get historical stock price data for a given ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        interval: Data interval - '1d' (daily), '1wk' (weekly), '1mo' (monthly)
                  Also supports: '1m', '5m', '15m', '30m', '1h' for intraday

    Returns:
        Dictionary containing:
        - ticker: Stock symbol
        - interval: Data interval used
        - start_date: Start date of data
        - end_date: End date of data
        - data: List of OHLCV candles with dates
        - count: Number of data points
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch historical data
        hist = stock.history(start=start_date, end=end_date, interval=interval)
        
        if hist.empty:
            return {
                "error": f"No data found for ticker '{ticker}' in the specified date range",
                "ticker": ticker.upper(),
            }
        
        # Convert to list of dictionaries
        candles = []
        for date, row in hist.iterrows():
            candles.append({
                "date": date.strftime("%Y-%m-%d %H:%M:%S") if interval in ["1m", "5m", "15m", "30m", "1h"] else date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
                "dividends": round(row.get("Dividends", 0), 4),
                "stock_splits": round(row.get("Stock Splits", 0), 4),
            })
        
        return {
            "ticker": ticker.upper(),
            "interval": interval,
            "start_date": start_date,
            "end_date": end_date,
            "data": candles,
            "count": len(candles),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch historical data for ticker '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }

