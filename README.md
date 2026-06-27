# Sharelock

A multi-agent stock analysis system built with LangGraph and Ollama. Six specialized analysts run in parallel, then an Investment Committee orchestrator synthesizes their reports into a final verdict.

## How It Works

```
                    ┌─────────────────────┐
                    │   Input: Ticker      │
                    └────────┬────────────┘
                             │ (parallel)
          ┌──────────────────┼──────────────────┐
          ▼          ▼       ▼       ▼     ▼    ▼
   Fundamental  Technical  Valuation  Risk  Sentiment  Macro
     Analyst     Analyst   Specialist Manager Analyst  Specialist
          └──────────────────┬──────────────────┘
                             ▼
                  Investment Committee (Orchestrator)
                             │
                             ▼
              Verdict: Strong Buy / Buy / Hold / Sell / Drop
```

### Agents

| Agent | Focus |
|---|---|
| **Fundamental Analyst** | Revenue trends, margins, ROE/ROCE, debt levels |
| **Technical Analyst** | Price action, support/resistance, volume patterns |
| **Valuation Specialist** | P/E, P/B, PEG ratios vs. historical averages |
| **Risk Manager** | Promoter pledging, balance sheet red flags, sector risks |
| **Sentiment Analyst** | Corporate announcements, market perception |
| **Macro Specialist** | Industry tailwinds/headwinds, rate/inflation impact |

All agents run in parallel via LangGraph. The **Investment Committee** (orchestrator) reads all six reports and issues a final conclusion.

### Tools

- **`stock_price_tool`** — live price via yfinance (supports `.NS` / `.BO` suffixes for NSE/BSE)
- **`historical_data_tool`** — OHLCV history via yfinance
- **`fundamental_data_tool`** — scraped fundamentals (Screener.in via Playwright)
- **Qualitative DB** — PDF earnings reports chunked, classified, and stored in ChromaDB for semantic retrieval

### MCP Server

Sharelock also ships as an MCP server, exposing its tools to any MCP-compatible client:

```bash
sharelock-mcp
```

Tools exposed: `get_stock_price`, `get_historical_data`, `get_scraped_data`

## Setup

**Requirements:** Python 3.13+, [uv](https://github.com/astral-sh/uv), [Ollama](https://ollama.com/)

```bash
# Install dependencies
uv sync

# Pull the local model
ollama pull qwen2.5:14b

# Install Playwright browser
uv run playwright install chromium
```

## Usage

### Run a stock analysis

```bash
uv run python -m src.agents.multi_agent_system RELIANCE.NS
```

Output includes individual analyst reports followed by the Investment Committee verdict.

### Build the qualitative knowledge base

```bash
# Add a PDF (e.g. an earnings report)
uv run python -m src.qualitative_db add data/report.pdf

# Query it
uv run python -m src.qualitative_db query "revenue growth FY24"
```

### Run as an MCP server

```bash
sharelock-mcp
# or
uv run python -m src.mcp_server.server
```

## Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — parallel agent graph and state management
- **[Ollama](https://ollama.com/) + qwen2.5:14b** — local LLM inference (no API key needed)
- **[yfinance](https://github.com/ranaroussi/yfinance)** — market data
- **[Playwright](https://playwright.dev/)** — fundamentals scraping
- **[ChromaDB](https://www.trychroma.com/)** — vector store for qualitative data
- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server

