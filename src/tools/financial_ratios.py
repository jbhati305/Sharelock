"""
Tool: get_financial_ratios

Fetches key financial ratios for NSE listed companies.
"""

from nsepython import nsefetch


def get_financial_ratios(symbol: str) -> dict:
    """
    Get key financial ratios for an NSE listed company.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK')

    Returns:
        Dictionary containing:
        - symbol: Stock symbol
        - company_name: Company name
        - industry: Industry classification
        - pe_ratio: Price to Earnings ratio
        - sector_pe: Sector average PE
        - last_price: Last traded price
        - market_cap: Market capitalization
        - face_value: Face value
        - indices: List of indices the stock belongs to
    """
    try:
        # Fetch quote data
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"
        quote = nsefetch(url)

        if not quote:
            return {
                "error": f"No data found for symbol '{symbol}'. Make sure it's a valid NSE symbol.",
                "symbol": symbol.upper(),
            }

        info = quote.get("info", {})
        metadata = quote.get("metadata", {})
        price_info = quote.get("priceInfo", {})
        security_info = quote.get("securityInfo", {})
        industry_info = quote.get("industryInfo", {})

        return {
            "symbol": info.get("symbol", symbol.upper()),
            "company_name": info.get("companyName"),
            "industry": info.get("industry"),
            # Price data
            "last_price": price_info.get("lastPrice"),
            "previous_close": price_info.get("previousClose"),
            "change": price_info.get("change"),
            "percent_change": price_info.get("pChange"),
            # Valuation ratios
            "pe_ratio": metadata.get("pdSymbolPe"),
            "sector_pe": metadata.get("pdSectorPe"),
            "sector_index": metadata.get("pdSectorInd"),
            # Security info
            "face_value": security_info.get("faceValue"),
            "market_cap": security_info.get("marketCap"),
            "issued_size": security_info.get("issuedSize"),
            # Industry classification
            "basic_industry": industry_info.get("basicIndustry"),
            "macro_sector": industry_info.get("macro"),
            "sector": industry_info.get("sector"),
            # Index membership
            "indices": metadata.get("pdSectorIndAll", []),
            "is_fno": info.get("isFNOSec", False),
            "currency": "INR",
            "exchange": "NSE",
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch financial ratios for '{symbol}': {str(e)}",
            "symbol": symbol.upper(),
        }
