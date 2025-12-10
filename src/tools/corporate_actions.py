"""
Tool: get_corporate_actions

Fetches corporate actions (dividends, splits) using yfinance.
"""

import yfinance as yf


def get_corporate_actions(ticker: str) -> dict:
    """
    Get corporate actions (dividends and stock splits) for a stock.

    Args:
        ticker: Stock ticker symbol
                - US stocks: 'AAPL', 'GOOGL', 'MSFT'
                - Indian NSE stocks: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'

    Returns:
        Dictionary containing:
        - dividends: List of dividend payments with dates and amounts
        - splits: List of stock splits with dates and ratios
        - total_dividends: Total number of dividend records
        - total_splits: Total number of split records
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get dividends
        dividends_series = stock.dividends
        dividends = []
        if dividends_series is not None and not dividends_series.empty:
            for date, amount in dividends_series.tail(20).items():
                dividends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "amount": round(float(amount), 4),
                })
        
        # Get stock splits
        splits_series = stock.splits
        splits = []
        if splits_series is not None and not splits_series.empty:
            for date, ratio in splits_series.items():
                if ratio != 0:
                    splits.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "ratio": f"{int(ratio)}:1" if ratio >= 1 else f"1:{int(1/ratio)}",
                        "ratio_value": float(ratio),
                    })

        return {
            "ticker": ticker.upper(),
            "currency": info.get("currency", "USD"),
            # Current dividend info
            "dividend_rate": info.get("dividendRate"),
            "dividend_yield": info.get("dividendYield"),
            "ex_dividend_date": info.get("exDividendDate"),
            "payout_ratio": info.get("payoutRatio"),
            # Historical dividends (last 20)
            "dividends": dividends,
            "total_dividend_records": len(dividends_series) if dividends_series is not None else 0,
            # Stock splits
            "splits": splits,
            "total_splits": len(splits),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch corporate actions for '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }
