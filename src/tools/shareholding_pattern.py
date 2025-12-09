"""
Tool: get_trade_info

Fetches trade info including delivery data for NSE listed companies.
Delivery percentage is a key metric for Indian market analysis.
"""

from nsepython import nsefetch


def get_trade_info(symbol: str) -> dict:
    """
    Get trade info and delivery data for an NSE listed company.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK')

    Returns:
        Dictionary containing:
        - symbol: Stock symbol
        - quantity_traded: Total quantity traded
        - delivery_quantity: Delivery quantity
        - delivery_percentage: Delivery to traded percentage (higher = more long-term buying)
        - total_traded_volume: Total traded volume in lakhs
        - total_traded_value: Total traded value in crores
        - market_cap: Total market cap in crores
        - free_float_market_cap: Free float market cap in crores
        - impact_cost: Impact cost
        - volatility: Daily and annual volatility
    """
    try:
        # Fetch trade info
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}&section=trade_info"
        data = nsefetch(url)

        if not data:
            return {
                "error": f"No trade info found for symbol '{symbol}'.",
                "symbol": symbol.upper(),
            }

        # Extract data
        security_dp = data.get("securityWiseDP", {})
        market_depth = data.get("marketDeptOrderBook", {})
        trade_info = market_depth.get("tradeInfo", {})
        var_info = market_depth.get("valueAtRisk", {})

        return {
            "symbol": symbol.upper(),
            # Delivery data
            "quantity_traded": security_dp.get("quantityTraded"),
            "delivery_quantity": security_dp.get("deliveryQuantity"),
            "delivery_percentage": security_dp.get("deliveryToTradedQuantity"),
            "delivery_date": security_dp.get("secWiseDelPosDate"),
            # Volume data (in lakhs/crores)
            "total_traded_volume": trade_info.get("totalTradedVolume"),
            "total_traded_value": trade_info.get("totalTradedValue"),
            # Market cap (in crores)
            "total_market_cap": trade_info.get("totalMarketCap"),
            "free_float_market_cap": trade_info.get("ffmc"),
            # Risk metrics
            "impact_cost": trade_info.get("impactCost"),
            "daily_volatility": trade_info.get("cmDailyVolatility"),
            "annual_volatility": trade_info.get("cmAnnualVolatility"),
            # VAR margins
            "security_var": var_info.get("securityVar"),
            "var_margin": var_info.get("varMargin"),
            "extreme_loss_margin": var_info.get("extremeLossMargin"),
            "applicable_margin": var_info.get("applicableMargin"),
            # Order book summary
            "total_buy_quantity": market_depth.get("totalBuyQuantity"),
            "total_sell_quantity": market_depth.get("totalSellQuantity"),
            "exchange": "NSE",
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch trade info for '{symbol}': {str(e)}",
            "symbol": symbol.upper(),
        }
