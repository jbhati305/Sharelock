"""
Tool: get_company_profile

Fetches company profile and basic information from NSE India.
"""

from nsepython import nse_eq


def get_company_profile(symbol: str) -> dict:
    """
    Get company profile and basic information for an NSE listed company.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK')

    Returns:
        Dictionary containing:
        - symbol: Stock symbol
        - company_name: Full company name
        - industry: Industry classification
        - isin: ISIN code
        - series: Trading series (EQ, BE, etc.)
        - face_value: Face value of shares
        - issued_size: Total issued shares
        - listing_date: Date of listing
        - market_lot: Market lot size
        - is_suspended: Whether trading is suspended
    """
    try:
        quote = nse_eq(symbol.upper())

        if not quote or "error" in quote:
            return {
                "error": f"No data found for symbol '{symbol}'. Make sure it's a valid NSE symbol.",
                "symbol": symbol.upper(),
            }

        info = quote.get("info", {})
        security_info = quote.get("securityInfo", {})
        metadata = quote.get("metadata", {})

        return {
            "symbol": info.get("symbol", symbol.upper()),
            "company_name": info.get("companyName"),
            "industry": info.get("industry"),
            "isin": metadata.get("isin") or info.get("isin"),
            "series": metadata.get("series"),
            "face_value": security_info.get("faceValue"),
            "issued_size": security_info.get("issuedSize"),
            "listing_date": metadata.get("listingDate"),
            "market_lot": security_info.get("boardStatus"),
            "is_suspended": security_info.get("isSuspended", False),
            "is_slb": security_info.get("slb", False),
            "class_of_share": security_info.get("classOfShare"),
            "surveillance": security_info.get("surveillance"),
            "exchange": "NSE",
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch company profile for '{symbol}': {str(e)}",
            "symbol": symbol.upper(),
        }

