"""
Tool: get_holders_info

Fetches institutional and insider holdings using yfinance.
"""

import yfinance as yf


def get_holders_info(ticker: str) -> dict:
    """
    Get institutional holders and insider holdings for a stock.

    Args:
        ticker: Stock ticker symbol
                - US stocks: 'AAPL', 'GOOGL', 'MSFT'
                - Indian NSE stocks: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'

    Returns:
        Dictionary containing:
        - institutional_holders: List of major institutional holders
        - major_holders: Breakdown of holder types
        - insider_holdings: Insider transaction data (if available)
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get major holders breakdown
        major_holders = {}
        try:
            major_holders_df = stock.major_holders
            if major_holders_df is not None and not major_holders_df.empty and len(major_holders_df.columns) >= 2:
                for idx in range(len(major_holders_df)):
                    try:
                        value = major_holders_df.iloc[idx, 0]
                        label = major_holders_df.iloc[idx, 1]
                        major_holders[str(label)] = value
                    except (IndexError, KeyError):
                        continue
        except Exception:
            pass
        
        # Get institutional holders
        institutional_holders = []
        try:
            inst_holders_df = stock.institutional_holders
            if inst_holders_df is not None and not inst_holders_df.empty:
                for idx in range(min(10, len(inst_holders_df))):
                    try:
                        row = inst_holders_df.iloc[idx]
                        institutional_holders.append({
                            "holder": row.get("Holder") if hasattr(row, 'get') else row["Holder"] if "Holder" in row.index else None,
                            "shares": int(row.get("Shares", 0) or row["Shares"]) if "Shares" in row.index else None,
                            "date_reported": str(row.get("Date Reported", "")) if "Date Reported" in row.index else None,
                            "percent_out": row.get("% Out") if "% Out" in row.index else None,
                            "value": row.get("Value") if "Value" in row.index else None,
                        })
                    except (IndexError, KeyError, TypeError):
                        continue
        except Exception:
            pass
        
        # Get mutual fund holders
        mutualfund_holders = []
        try:
            mf_holders_df = stock.mutualfund_holders
            if mf_holders_df is not None and not mf_holders_df.empty:
                for idx in range(min(10, len(mf_holders_df))):
                    try:
                        row = mf_holders_df.iloc[idx]
                        mutualfund_holders.append({
                            "holder": row.get("Holder") if hasattr(row, 'get') else row["Holder"] if "Holder" in row.index else None,
                            "shares": int(row.get("Shares", 0) or row["Shares"]) if "Shares" in row.index else None,
                            "date_reported": str(row.get("Date Reported", "")) if "Date Reported" in row.index else None,
                            "percent_out": row.get("% Out") if "% Out" in row.index else None,
                            "value": row.get("Value") if "Value" in row.index else None,
                        })
                    except (IndexError, KeyError, TypeError):
                        continue
        except Exception:
            pass

        return {
            "ticker": ticker.upper(),
            "major_holders": major_holders if major_holders else "Data not available for this stock",
            "institutional_holders": institutional_holders if institutional_holders else "Data not available for this stock",
            "mutualfund_holders": mutualfund_holders if mutualfund_holders else "Data not available for this stock",
            "institutional_count": len(institutional_holders),
            "mutualfund_count": len(mutualfund_holders),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch holders info for '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }
