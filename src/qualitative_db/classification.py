"""
Topic classification and query utilities.
"""

from .config import TOPIC_KEYWORDS, QUERY_SYNONYMS


def classify_topics(text: str) -> tuple[str, list[str]]:
    """
    Classify chunk into primary and secondary topics.
    
    Returns: (primary_topic, list of secondary topics)
    """
    text_lower = text.lower()
    
    topic_scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            topic_scores[topic] = score
    
    if not topic_scores:
        return 'general', []
    
    sorted_topics = sorted(topic_scores.items(), key=lambda x: -x[1])
    
    primary = sorted_topics[0][0]
    threshold = sorted_topics[0][1] / 2
    secondary = [t for t, s in sorted_topics[1:4] if s >= threshold]
    
    return primary, secondary


def expand_query(query: str) -> str:
    """Expand query with synonyms for better retrieval."""
    expanded = query
    query_lower = query.lower()
    
    for term, synonyms in QUERY_SYNONYMS.items():
        if term in query_lower:
            expanded += " " + " ".join(synonyms)
    
    return expanded

