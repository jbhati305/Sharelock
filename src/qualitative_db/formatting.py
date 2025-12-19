"""
Output formatting utilities for LLM context.
"""

from .database import QualitativeDataVectorDB


def format_result_for_llm(result: dict, include_snippets: bool = True) -> str:
    """Format a single result for LLM context."""
    metadata = result['metadata']
    
    output = f"""
=== {metadata.get('section', 'Section')} ===
Company: {metadata.get('company_name')} | Year: {metadata.get('doc_year')} | Type: {metadata.get('doc_type')}
Topic: {metadata.get('topic')} | Quality: {metadata.get('content_quality', 'N/A')} | Table: {'Yes' if metadata.get('is_table') else 'No'}
Pages: {metadata.get('page_numbers')} | Relevance: {result['relevance_score']:.1%}
"""
    
    if include_snippets and result.get('matched_snippets'):
        output += "\n[Key matches]:\n"
        for snippet in result['matched_snippets'][:2]:
            text = snippet['text'][:100].replace('\n', ' ')
            output += f"  → \"{text}...\"\n"
    
    output += f"\n[Content]:\n{result['text']}\n"
    
    return output


def get_context_for_llm(
    db: QualitativeDataVectorDB,
    query: str,
    n_results: int = 5,
    **filters
) -> str:
    """Get formatted context ready for LLM prompts."""
    results = db.query(query, n_results=n_results, high_quality_only=True, **filters)
    
    if not results:
        return "No relevant information found in the database."
    
    parts = [f"Found {len(results)} relevant sections for: '{query}'\n"]
    
    for i, result in enumerate(results, 1):
        parts.append(f"\n[Source {i}]")
        parts.append(format_result_for_llm(result))
    
    return "\n".join(parts)


def print_query_results(results: list[dict], max_text_len: int = 600):
    """Print query results in a readable format."""
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"{'─'*70}")
        print(f"Result {i} | Relevance: {result['relevance_score']:.1%} | Quality: {meta.get('content_quality', 'N/A')}")
        print(f"Section: {meta.get('section', 'N/A')}")
        print(f"Company: {meta.get('company_name')} | Year: {meta.get('doc_year')} | Topic: {meta.get('topic')}")
        print(f"Table: {'Yes' if meta.get('is_table') else 'No'} | Pages: {meta.get('page_numbers')}")
        
        if result.get('matched_snippets'):
            print(f"\n🎯 Matched:")
            for snippet in result['matched_snippets'][:2]:
                text = snippet['text'][:80].replace('\n', ' ')
                print(f"   \"{text}...\"")
        
        print(f"\n📄 Context:")
        print(f"{'─'*70}")
        text = result['text']
        if len(text) > max_text_len:
            text = text[:max_text_len] + "..."
        print(text)
        print()

