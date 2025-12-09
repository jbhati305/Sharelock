"""
Tool: get_corporate_actions

Fetches corporate actions (dividends, bonus, splits, rights) for NSE listed companies.
"""

from nsepython import nsefetch


def get_corporate_actions(symbol: str) -> dict:
    """
    Get corporate actions for an NSE listed company.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK')

    Returns:
        Dictionary containing:
        - symbol: Stock symbol
        - actions: List of corporate actions (dividends, bonus, splits, rights)
        Each action contains:
            - ex_date: Ex-date for the action
            - purpose: Purpose/type of action
            - record_date: Record date
            - bc_start_date: Book closure start date
            - bc_end_date: Book closure end date
    """
    try:
        # Fetch corporate actions
        url = f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol={symbol.upper()}"
        data = nsefetch(url)

        if not data:
            return {
                "error": f"No corporate actions found for symbol '{symbol}'.",
                "symbol": symbol.upper(),
                "actions": [],
            }

        # Process corporate actions
        actions = []
        for action in data:
            actions.append({
                "ex_date": action.get("exDate"),
                "purpose": action.get("subject"),
                "record_date": action.get("recDate"),
                "bc_start_date": action.get("bcStartDate"),
                "bc_end_date": action.get("bcEndDate"),
                "face_value": action.get("faceVal"),
            })

        return {
            "symbol": symbol.upper(),
            "actions": actions,
            "total_actions": len(actions),
            "exchange": "NSE",
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch corporate actions for '{symbol}': {str(e)}",
            "symbol": symbol.upper(),
        }

