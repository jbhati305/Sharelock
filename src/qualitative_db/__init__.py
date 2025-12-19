"""
Qualitative Data Vector Database Package

A ChromaDB-based vector database for storing and querying company qualitative data
from PDF documents (annual reports, prospectuses, earnings calls, etc.)

Features:
- Parent-child chunking for precise search with full context retrieval
- Table extraction and Markdown conversion
- Structured financial metrics extraction
- Topic classification and query expansion
- Rich metadata for filtering

Usage:
    from qualitative_db import QualitativeDataVectorDB, get_context_for_llm
    
    db = QualitativeDataVectorDB()
    
    # Add a document
    db.add_document(
        pdf_path="report.pdf",
        company_name="Meesho",
        doc_year=2024,
        doc_type="prospectus",
        company_sector="technology"
    )
    
    # Query
    results = db.query("What is the revenue growth?", n_results=5)
    
    # Get LLM-ready context
    context = get_context_for_llm(db, "Explain the business model")
"""

from .config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    TOPIC_KEYWORDS,
    QUERY_SYNONYMS,
)

from .database import QualitativeDataVectorDB

from .formatting import (
    format_result_for_llm,
    get_context_for_llm,
    print_query_results,
)

from .extractors import (
    extract_content_from_pdf,
    extract_entities,
    extract_financial_metrics,
)

from .chunking import (
    create_parent_child_chunks,
    create_child_chunks,
    assess_content_quality,
)

from .classification import (
    classify_topics,
    expand_query,
)

__all__ = [
    # Main class
    'QualitativeDataVectorDB',
    
    # Formatting
    'format_result_for_llm',
    'get_context_for_llm',
    'print_query_results',
    
    # Extractors
    'extract_content_from_pdf',
    'extract_entities',
    'extract_financial_metrics',
    
    # Chunking
    'create_parent_child_chunks',
    'create_child_chunks',
    'assess_content_quality',
    
    # Classification
    'classify_topics',
    'expand_query',
    
    # Config
    'TOPIC_KEYWORDS',
    'QUERY_SYNONYMS',
]

