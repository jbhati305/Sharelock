# Stock Market Analysis Agent - Tools & Features

## 1. Market Data Fetching Tools

Your agent can't analyze anything unless it can fetch accurate market data.

### Tool: `get_stock_price(ticker)`
Returns:
- Current price
- OHLC (Open, High, Low, Close)
- Volume
- Market cap

### Tool: `get_historical_data(ticker, start_date, end_date)`
Returns:
- Daily / weekly / monthly candles
- Adjusted prices for splits/dividends
- Volume history

### Tool: `get_intraday_data(ticker, interval)` (optional)
Returns:
- 1-min, 5-min, 15-min data
- Used for trading-style analysis

---

## 2. Company Fundamentals Tools

For real company analysis, you need fundamentals.

### Tool: `get_financial_statements(ticker, statement_type)`
Parameters:
- `statement_type`: `income_statement` | `balance_sheet` | `cashflow`

Returns:
- Revenue, expenses, net income
- Assets, liabilities, equity
- Free cash flow
- CAPEX

### Tool: `get_ratios(ticker)`
Returns:
- Valuation ratios: P/E, P/B, PEG
- Profitability ratios: ROE, ROA, ROIC
- Margin ratios: Gross/Operating/Net margins
- Leverage ratios: Debt-to-equity
- Liquidity ratios: Current ratio

### Tool: `get_company_profile(ticker)`
Returns:
- Sector & industry
- CEO
- Headquarters
- Employees
- Business description

---

## 3. News, Sentiment, & Events Tools

### Tool: `get_company_news(ticker, limit)`
Returns:
- Title
- Source
- Published date
- Summary

### Tool: `analyze_news_sentiment(news_list)`
Outputs:
- Sentiment score
- Risk score
- Positive/negative event tagging

### Tool: `get_earnings_calendar(ticker)`
Returns:
- Next earnings date
- Earnings estimate
- Expected volatility

---

## 4. Macro & Industry Analysis Tools

Many agents fail because they analyze companies in isolation.

### Tool: `get_macroeconomic_indicators(indicator_name)`
Examples:
- GDP growth
- Interest rates
- CPI / inflation
- Unemployment rate

### Tool: `get_industry_metrics(industry_name)`
Returns:
- Industry growth rate
- Competitor list
- Industry average P/E, ROE, margins

---

## 5. Analytics & Modeling Tools

### Tool: `calculate_technical_indicators(data, indicators=[...])`
Examples:
- SMA, EMA
- RSI
- MACD
- Bollinger Bands
- Beta

### Tool: `run_dcf_model(financials)`
Outputs:
- Fair value estimate
- Discount rate
- Sensitivity analysis

### Tool: `run_comparable_valuation(ticker)`
Compares target stock to peers.

### Tool: `portfolio_optimizer(assets, constraints)`
Features:
- Mean-variance optimization
- Efficient frontier
- Risk analysis

---

## 6. Data Storage & Memory Tools

### Tool: `save_analysis_session(data)`
Stores:
- Company data
- Agent-generated insights
- Charts

### Tool: `load_saved_analysis(session_id)`
Lets agent resume an analysis.

---

## 7. Reporting + Visualization Tools

### Tool: `generate_report(analysis_data, format)`
Formats:
- PDF
- Markdown
- HTML

### Tool: `generate_chart(series, chart_type)`
Chart types:
- Price trend
- Volume
- Moving averages
- Pie charts for revenue segments
