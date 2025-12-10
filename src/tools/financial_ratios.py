"""
Tool: get_financial_ratios

Fetches key financial ratios using yfinance.
Supports both global and Indian markets.
"""

import yfinance as yf


def get_financial_ratios(ticker: str) -> dict:
    """
    Get key financial ratios for a stock.

    Args:
        ticker: Stock ticker symbol
                - US stocks: 'AAPL', 'GOOGL', 'MSFT'
                - Indian NSE stocks: 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'

    Returns:
        Dictionary containing:
        - Valuation: PE ratio, Forward PE, PEG, Price to Book, Price to Sales
        - Profitability: Profit margins, Operating margins, ROE, ROA
        - Growth: Revenue growth, Earnings growth
        - Dividends: Dividend rate, Dividend yield, Payout ratio
        - Debt: Debt to equity, Current ratio, Quick ratio
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
            "name": info.get("shortName") or info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            # Valuation Ratios
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "enterprise_value": info.get("enterpriseValue"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
            # Profitability
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "ebitda_margin": info.get("ebitdaMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            # Growth
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
            # Per Share Data
            "eps_trailing": info.get("trailingEps"),
            "eps_forward": info.get("forwardEps"),
            "book_value": info.get("bookValue"),
            "revenue_per_share": info.get("revenuePerShare"),
            # Dividends
            "dividend_rate": info.get("dividendRate"),
            "dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            "five_year_avg_dividend_yield": info.get("fiveYearAvgDividendYield"),
            # Debt & Liquidity
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            # Market Data
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_day_average": info.get("fiftyDayAverage"),
            "two_hundred_day_average": info.get("twoHundredDayAverage"),
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch financial ratios for '{ticker}': {str(e)}",
            "ticker": ticker.upper(),
        }
