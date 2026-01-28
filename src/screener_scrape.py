#!/usr/bin/env python3
"""
Screener.in Stock Data Scraper
Extracts comprehensive stock data including financials, ratios, and more.
"""

import asyncio
import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from playwright.async_api import async_playwright, Page, Browser


@dataclass
class StockData:
    """Data class to hold all scraped stock information."""
    symbol: str = ""
    name: str = ""
    current_price: str = ""
    change_percent: str = ""
    
    # Key metrics
    market_cap: str = ""
    pe_ratio: str = ""
    book_value: str = ""
    dividend_yield: str = ""
    roce: str = ""
    roe: str = ""
    face_value: str = ""
    
    # Additional ratios
    ratios: dict = field(default_factory=dict)
    
    # Quarterly results
    quarterly_results: list = field(default_factory=list)
    
    # Profit & Loss
    profit_loss: list = field(default_factory=list)
    
    # Balance Sheet
    balance_sheet: list = field(default_factory=list)
    
    # Cash Flow
    cash_flow: list = field(default_factory=list)
    
    # Shareholding pattern
    shareholding: list = field(default_factory=list)
    
    # Pros and Cons
    pros: list = field(default_factory=list)
    cons: list = field(default_factory=list)
    
    # Peer comparison
    peers: list = field(default_factory=list)
    
    # Documents
    annual_reports: list = field(default_factory=list)
    concall_transcripts: list = field(default_factory=list)
    credit_ratings: list = field(default_factory=list)
    investor_presentations: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class ScreenerScraper:
    """Web scraper for screener.in stock data."""
    
    BASE_URL = "https://www.screener.in"
    LOGIN_URL = "https://www.screener.in/login/"
    
    def __init__(self, email: str = "", password: str = "", headless: bool = True):
        self.email = email
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in = False
    
    async def start(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
    
    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def login(self) -> bool:
        """Login to screener.in with provided credentials."""
        if not self.email or not self.password:
            print("⚠️  No credentials provided. Some data may be restricted.")
            return False
        
        if not self.page:
            print("❌ Browser not initialized. Call start() first.")
            return False
        
        try:
            print("🔐 Logging in to screener.in...")
            await self.page.goto(self.LOGIN_URL, wait_until="networkidle")
            
            # Fill login form
            await self.page.fill('input[name="username"]', self.email)
            await self.page.fill('input[name="password"]', self.password)
            
            # Submit form
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state("networkidle")
            
            # Check if login was successful
            if "login" not in self.page.url.lower():
                print("✅ Login successful!")
                self.logged_in = True
                return True
            else:
                print("❌ Login failed. Please check your credentials.")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    async def search_stock(self, query: str) -> str:
        """Search for a stock and return its URL."""
        search_url = f"{self.BASE_URL}/company/{query}/"
        return search_url
    
    async def _extract_text(self, selector: str, default: str = "") -> str:
        """Safely extract text from an element."""
        if not self.page:
            return default
        try:
            element = await self.page.query_selector(selector)
            if element:
                return (await element.inner_text()).strip()
        except:
            pass
        return default
    
    async def _extract_table_data(self, section_id: str) -> list[dict[str, Any]]:
        """Extract data from a financial table section."""
        data: list[dict[str, Any]] = []
        if not self.page:
            return data
        try:
            section = await self.page.query_selector(f"#{section_id}")
            if not section:
                section = await self.page.query_selector(f"section#{section_id}")
            
            if section:
                table = await section.query_selector("table")
                if table:
                    # Get headers
                    headers = []
                    header_cells = await table.query_selector_all("thead th")
                    for cell in header_cells:
                        headers.append((await cell.inner_text()).strip())
                    
                    # Get rows
                    rows = await table.query_selector_all("tbody tr")
                    for row in rows:
                        cells = await row.query_selector_all("td")
                        row_data: dict[str, Any] = {}
                        cell_texts: list[str] = []
                        for cell in cells:
                            cell_texts.append((await cell.inner_text()).strip())
                        
                        if cell_texts and headers:
                            label = cell_texts[0] if cell_texts else ""
                            
                            # Skip rows that are just links or metadata (e.g., "Raw PDF")
                            if label.lower() in ["raw pdf", "pdf", "link", ""]:
                                continue
                            
                            row_data["label"] = label
                            for i, header in enumerate(headers[1:], 1):
                                if i < len(cell_texts):
                                    row_data[header] = cell_texts[i]
                            data.append(row_data)
        except Exception as e:
            print(f"Warning: Could not extract {section_id}: {e}")
        
        return data
    
    async def _extract_key_metrics(self) -> dict[str, str]:
        """Extract key metrics from the top section."""
        metrics: dict[str, str] = {}
        if not self.page:
            return metrics
        try:
            # Find all list items in the top ratios section
            ratio_items = await self.page.query_selector_all("#top-ratios li")
            for item in ratio_items:
                text = await item.inner_text()
                parts = text.split("\n")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    metrics[key] = value
        except Exception as e:
            print(f"Warning: Could not extract key metrics: {e}")
        
        return metrics
    
    async def _extract_pros_cons(self) -> tuple[list[str], list[str]]:
        """Extract pros and cons lists."""
        pros: list[str] = []
        cons: list[str] = []
        
        if not self.page:
            return pros, cons
        
        try:
            # Pros
            pros_section = await self.page.query_selector(".pros")
            if pros_section:
                items = await pros_section.query_selector_all("li")
                for item in items:
                    pros.append((await item.inner_text()).strip())
            
            # Cons
            cons_section = await self.page.query_selector(".cons")
            if cons_section:
                items = await cons_section.query_selector_all("li")
                for item in items:
                    cons.append((await item.inner_text()).strip())
        except Exception as e:
            print(f"Warning: Could not extract pros/cons: {e}")
        
        return pros, cons
    
    async def _extract_peers(self) -> list[dict[str, str]]:
        """Extract peer comparison data."""
        peers: list[dict[str, str]] = []
        if not self.page:
            return peers
        try:
            peer_section = await self.page.query_selector("#peers")
            if peer_section:
                table = await peer_section.query_selector("table")
                if table:
                    # Get all rows from tbody
                    rows = await table.query_selector_all("tbody tr")
                    
                    if not rows:
                        return peers
                    
                    # First row contains headers (as th cells)
                    first_row = rows[0]
                    header_cells = await first_row.query_selector_all("th")
                    headers: list[str] = []
                    for cell in header_cells:
                        header_text = (await cell.inner_text()).strip()
                        headers.append(header_text if header_text else f"col_{len(headers)}")
                    
                    # Remaining rows contain data (as td cells)
                    for row in rows[1:]:
                        all_cells = await row.query_selector_all("td")
                        if all_cells and len(all_cells) > 1:
                            peer_data: dict[str, str] = {}
                            for i, cell in enumerate(all_cells):
                                if i < len(headers):
                                    header_name = headers[i]
                                    # Check for link (company name in "Name" column)
                                    link = await cell.query_selector("a")
                                    if link:
                                        name = (await link.inner_text()).strip()
                                        href = await link.get_attribute("href")
                                        peer_data[header_name] = name
                                        if href:
                                            peer_data["url"] = f"{self.BASE_URL}{href}"
                                    else:
                                        peer_data[header_name] = (await cell.inner_text()).strip()
                            if peer_data and peer_data.get("Name"):
                                peers.append(peer_data)
        except Exception as e:
            print(f"Warning: Could not extract peers: {e}")
        
        return peers
    
    async def _extract_documents(self) -> dict[str, list[dict[str, str]]]:
        """Extract links to annual reports, concall transcripts, and other documents."""
        documents: dict[str, list[dict[str, str]]] = {
            "annual_reports": [],
            "concall_transcripts": [],
            "credit_ratings": [],
            "investor_presentations": []
        }
        
        if not self.page:
            return documents
        
        try:
            # Find the documents section
            doc_section = await self.page.query_selector("#documents")
            if not doc_section:
                # Try alternative selector
                doc_section = await self.page.query_selector("section#documents")
            
            if doc_section:
                # Find all document links
                doc_items = await doc_section.query_selector_all("li")
                
                for item in doc_items:
                    link = await item.query_selector("a")
                    if link:
                        text = (await link.inner_text()).strip()
                        href = await link.get_attribute("href")
                        
                        if not href:
                            continue
                        
                        # Make URL absolute if relative
                        if href.startswith("/"):
                            href = f"{self.BASE_URL}{href}"
                        
                        doc_entry = {
                            "title": text,
                            "url": href
                        }
                        
                        # Categorize based on text content
                        text_lower = text.lower()
                        if "annual report" in text_lower or "ar " in text_lower:
                            documents["annual_reports"].append(doc_entry)
                        elif "concall" in text_lower or "con call" in text_lower or "transcript" in text_lower or "earnings call" in text_lower:
                            documents["concall_transcripts"].append(doc_entry)
                        elif "credit" in text_lower or "rating" in text_lower:
                            documents["credit_ratings"].append(doc_entry)
                        elif "presentation" in text_lower or "investor" in text_lower:
                            documents["investor_presentations"].append(doc_entry)
                        else:
                            # Default to concall if it looks like quarterly report
                            if any(q in text_lower for q in ["q1", "q2", "q3", "q4", "quarter"]):
                                documents["concall_transcripts"].append(doc_entry)
                            else:
                                documents["annual_reports"].append(doc_entry)
            
            # Also try to find documents in a different structure (some pages have them differently)
            # Look for direct links to BSE/NSE annual reports
            annual_report_links = await self.page.query_selector_all('a[href*="annual-report"], a[href*="annualreport"]')
            for link in annual_report_links:
                text = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
                if href and text:
                    if href.startswith("/"):
                        href = f"{self.BASE_URL}{href}"
                    doc_entry = {"title": text, "url": href}
                    if doc_entry not in documents["annual_reports"]:
                        documents["annual_reports"].append(doc_entry)
            
            # Look for concall links
            concall_links = await self.page.query_selector_all('a[href*="concall"], a[href*="transcript"]')
            for link in concall_links:
                text = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
                if href and text:
                    if href.startswith("/"):
                        href = f"{self.BASE_URL}{href}"
                    doc_entry = {"title": text, "url": href}
                    if doc_entry not in documents["concall_transcripts"]:
                        documents["concall_transcripts"].append(doc_entry)
                        
        except Exception as e:
            print(f"Warning: Could not extract documents: {e}")
        
        return documents
    
    async def _extract_shareholding(self) -> list[dict[str, str]]:
        """Extract shareholding pattern data."""
        shareholding: list[dict[str, str]] = []
        if not self.page:
            return shareholding
        try:
            section = await self.page.query_selector("#shareholding")
            if section:
                table = await section.query_selector("table")
                if table:
                    headers: list[str] = []
                    header_cells = await table.query_selector_all("thead th")
                    for i, cell in enumerate(header_cells):
                        header_text = (await cell.inner_text()).strip()
                        # First column is the category/holder type
                        if i == 0 and not header_text:
                            headers.append("category")
                        else:
                            headers.append(header_text)
                    
                    rows = await table.query_selector_all("tbody tr")
                    for row in rows:
                        cells = await row.query_selector_all("td")
                        row_data: dict[str, str] = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                value = (await cell.inner_text()).strip()
                                # Clean up non-breaking spaces
                                value = value.replace('\u00a0', ' ')
                                row_data[headers[i]] = value
                        if row_data:
                            shareholding.append(row_data)
        except Exception as e:
            print(f"Warning: Could not extract shareholding: {e}")
        
        return shareholding
    
    async def scrape_stock(self, stock_symbol: str) -> StockData:
        """Scrape all available data for a stock."""
        stock_data = StockData(symbol=stock_symbol)
        
        if not self.page:
            print("❌ Browser not initialized. Call start() first.")
            return stock_data
        
        # Navigate to stock page
        stock_url = await self.search_stock(stock_symbol)
        print(f"📊 Fetching data for: {stock_symbol}")
        print(f"   URL: {stock_url}")
        
        try:
            await self.page.goto(stock_url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            return stock_data
        
        # Check if stock exists
        if "Page not found" in await self.page.content():
            print(f"❌ Stock '{stock_symbol}' not found!")
            return stock_data
        
        # Extract company name
        stock_data.name = await self._extract_text("h1.margin-0")
        if not stock_data.name:
            stock_data.name = await self._extract_text("h1")
        
        print(f"   Company: {stock_data.name}")
        
        # Extract current price and change from #top section
        top_section = await self.page.query_selector("#top")
        if top_section:
            top_text = await top_section.inner_text()
            lines = [line.strip() for line in top_text.split('\n') if line.strip()]
            
            # Price is usually the second line (after company name), starts with ₹
            for i, line in enumerate(lines):
                if line.startswith('₹'):
                    # Extract price (remove ₹ and commas)
                    stock_data.current_price = line.replace('₹', '').strip()
                    # Next line is usually the change percentage
                    if i + 1 < len(lines):
                        change_line = lines[i + 1]
                        # Check if it's a percentage change (contains %)
                        if '%' in change_line:
                            stock_data.change_percent = change_line.strip()
                    break
        
        # Extract key metrics
        print("   📈 Extracting key metrics...")
        metrics = await self._extract_key_metrics()
        stock_data.ratios = metrics
        
        # Fallback: get price from ratios if not found in top section
        if not stock_data.current_price:
            stock_data.current_price = metrics.get("Current Price", "").replace('₹', '').strip()
        
        print(f"   Price: ₹{stock_data.current_price} ({stock_data.change_percent})")
        
        # Map common metrics
        stock_data.market_cap = metrics.get("Market Cap", "")
        stock_data.pe_ratio = metrics.get("Stock P/E", "")
        stock_data.book_value = metrics.get("Book Value", "")
        stock_data.dividend_yield = metrics.get("Dividend Yield", "")
        stock_data.roce = metrics.get("ROCE", "")
        stock_data.roe = metrics.get("ROE", "")
        stock_data.face_value = metrics.get("Face Value", "")
        
        # Extract pros and cons
        print("   ✅ Extracting pros and cons...")
        stock_data.pros, stock_data.cons = await self._extract_pros_cons()
        
        # Extract quarterly results
        print("   📅 Extracting quarterly results...")
        stock_data.quarterly_results = await self._extract_table_data("quarters")
        
        # Extract profit & loss
        print("   💰 Extracting profit & loss statement...")
        stock_data.profit_loss = await self._extract_table_data("profit-loss")
        
        # Extract balance sheet
        print("   📋 Extracting balance sheet...")
        stock_data.balance_sheet = await self._extract_table_data("balance-sheet")
        
        # Extract cash flow
        print("   💵 Extracting cash flow statement...")
        stock_data.cash_flow = await self._extract_table_data("cash-flow")
        
        # Extract shareholding pattern
        print("   👥 Extracting shareholding pattern...")
        stock_data.shareholding = await self._extract_shareholding()
        
        # Extract peer comparison
        print("   🏢 Extracting peer comparison...")
        stock_data.peers = await self._extract_peers()
        
        # Extract documents (annual reports, concall transcripts, etc.)
        print("   📄 Extracting document links...")
        documents = await self._extract_documents()
        stock_data.annual_reports = documents["annual_reports"]
        stock_data.concall_transcripts = documents["concall_transcripts"]
        stock_data.credit_ratings = documents["credit_ratings"]
        stock_data.investor_presentations = documents["investor_presentations"]
        
        print(f"✅ Data extraction complete for {stock_data.name}")
        
        return stock_data
    
    async def save_to_json(self, stock_data: StockData, filename: Optional[str] = None):
        """Save scraped data to a JSON file."""
        if filename is None:
            filename = f"{stock_data.symbol}_data.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(stock_data.to_json())
        
        print(f"💾 Data saved to: {filename}")


async def main():
    """Main function to run the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Screener.in Stock Data Scraper")
    parser.add_argument("stock", help="Stock symbol to scrape (e.g., RELIANCE, TCS, INFY)")
    parser.add_argument("-e", "--email", help="Screener.in login email", default="")
    parser.add_argument("-p", "--password", help="Screener.in login password", default="")
    parser.add_argument("-o", "--output", help="Output JSON filename")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--print-json", action="store_true", help="Print JSON to stdout")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 Screener.in Stock Data Scraper")
    print("=" * 60)
    
    scraper = ScreenerScraper(
        email=args.email,
        password=args.password,
        headless=not args.no_headless
    )
    
    try:
        await scraper.start()
        
        # Login if credentials provided
        if args.email and args.password:
            await scraper.login()
        
        # Scrape stock data
        stock_data = await scraper.scrape_stock(args.stock.upper())
        
        # Save to JSON
        output_file = args.output or f"{args.stock.upper()}_data.json"
        await scraper.save_to_json(stock_data, output_file)
        
        # Print JSON if requested
        if args.print_json:
            print("\n" + "=" * 60)
            print("📄 JSON Output:")
            print("=" * 60)
            print(stock_data.to_json())
        
    finally:
        await scraper.close()
    
    print("\n" + "=" * 60)
    print("✨ Scraping completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

