"""
PDF and content extraction functions.
"""

import re
from typing import Optional
import pdfplumber

from .config import SECTION_PATTERNS, ENTITY_PATTERNS, FINANCIAL_PATTERNS


def is_quality_table(table: list[list], min_rows: int = 2, min_cols: int = 2) -> bool:
    """Check if a table has meaningful content."""
    if not table or len(table) < min_rows:
        return False
    
    # Check for non-empty columns
    non_empty_cols = 0
    if table[0]:
        for i in range(len(table[0])):
            col_values = [row[i] if i < len(row) else None for row in table]
            non_empty = sum(1 for v in col_values if v and str(v).strip())
            if non_empty >= min_rows // 2:
                non_empty_cols += 1
    
    if non_empty_cols < min_cols:
        return False
    
    # Check for too many empty cells
    total_cells = sum(len(row) for row in table)
    empty_cells = sum(1 for row in table for cell in row if not cell or not str(cell).strip())
    
    if total_cells > 0 and empty_cells / total_cells > 0.6:
        return False
    
    return True


def table_to_markdown(table: list[list]) -> str:
    """Convert table to clean Markdown format."""
    if not table or not table[0]:
        return ""
    
    def clean_cell(cell):
        if cell is None:
            return ""
        text = str(cell).replace('\n', ' ').replace('|', '/').strip()
        if len(text) > 50:
            text = text[:47] + "..."
        return text
    
    max_cols = max(len(row) for row in table)
    
    normalized = []
    for row in table:
        cleaned = [clean_cell(cell) for cell in row]
        while len(cleaned) < max_cols:
            cleaned.append("")
        normalized.append(cleaned[:max_cols])
    
    total_content = sum(len(cell) for row in normalized for cell in row)
    if total_content < 20:
        return ""
    
    lines = []
    header = normalized[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def extract_content_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text and quality tables from PDF."""
    content_blocks = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract tables with quality filtering
            tables = page.extract_tables({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "intersection_tolerance": 5,
            })
            
            for table in tables:
                if is_quality_table(table, min_rows=3, min_cols=2):
                    markdown = table_to_markdown(table)
                    if markdown and len(markdown) > 100:
                        content_blocks.append({
                            'text': markdown,
                            'page_num': page_num,
                            'is_table': True,
                            'section': f'Table (Page {page_num})'
                        })
            
            # Extract text
            text = page.extract_text()
            if text and text.strip() and len(text.strip()) > 50:
                content_blocks.append({
                    'text': text,
                    'page_num': page_num,
                    'is_table': False,
                    'section': None
                })
    
    return content_blocks


def detect_section_header(text: str) -> Optional[str]:
    """Detect section header from text."""
    lines = text.strip().split('\n')
    if not lines:
        return None
    
    first_line = lines[0].strip()
    
    for pattern in SECTION_PATTERNS:
        if re.match(pattern, first_line, re.IGNORECASE):
            header = first_line.strip()
            header = re.sub(r':\s*$', '', header)
            header = re.sub(r'\s+', ' ', header)
            return header[:100]
    
    return None


def extract_entities(text: str) -> dict:
    """Extract named entities from text."""
    entities = {}
    
    for entity_type, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            unique_matches = list(dict.fromkeys(matches))[:10]
            entities[entity_type] = unique_matches
    
    return entities


def extract_financial_metrics(text: str) -> list[dict]:
    """Extract structured financial metrics from text."""
    metrics = []
    
    for metric_type, pattern in FINANCIAL_PATTERNS.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            
            metrics.append({
                'type': metric_type,
                'value': match.group(1) if match.groups() else match.group(0),
                'context': context.strip()
            })
    
    return metrics[:10]

