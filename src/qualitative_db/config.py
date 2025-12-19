"""
Configuration constants for the vector database.
"""

# Database settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "company_qualitative_data"

# Chunk sizes
CHILD_CHUNK_SIZE = 250
CHILD_CHUNK_OVERLAP = 75
PARENT_CHUNK_SIZE = 2000
PARENT_CHUNK_OVERLAP = 300

# Section header patterns
SECTION_PATTERNS = [
    r'^[A-Z][A-Z\s\-&,]{10,}$',
    r'^\d+\.[\d\.]*\s+[A-Z][A-Za-z\s]+',
    r'^[IVXLC]+\.\s+[A-Z]',
    r'^[A-Z][A-Za-z\s]+:\s*$',
    r'^(?:MANAGEMENT DISCUSSION|RISK FACTORS|BUSINESS OVERVIEW|FINANCIAL HIGHLIGHTS|'
    r'KEY PERFORMANCE|CORPORATE GOVERNANCE|DIRECTORS\' REPORT|AUDITOR|'
    r'NOTES TO|BALANCE SHEET|PROFIT AND LOSS|CASH FLOW|STATEMENT OF|'
    r'RELATED PARTY|SEGMENT|CONTINGENT|CAPITAL STRUCTURE|SUMMARY OF)',
]

# Topic classification keywords
TOPIC_KEYWORDS = {
    'financial_performance': [
        'revenue', 'profit', 'loss', 'ebitda', 'margin', 'income', 'expense',
        'earnings', 'growth', 'sales', 'turnover', 'operating', 'net worth',
        'cash flow', 'fiscal', 'quarter', 'annual', 'yoy', 'qoq', 'cagr'
    ],
    'risk_factors': [
        'risk', 'threat', 'challenge', 'uncertainty', 'adverse', 'liability',
        'exposure', 'volatility', 'contingent', 'litigation', 'lawsuit', 'claim',
        'cybersecurity', 'fraud', 'default', 'impairment'
    ],
    'business_operations': [
        'operations', 'business', 'segment', 'product', 'service', 'market',
        'customer', 'supplier', 'vendor', 'logistics', 'delivery', 'order',
        'inventory', 'warehouse', 'fulfillment', 'platform'
    ],
    'governance': [
        'board', 'director', 'committee', 'governance', 'compliance', 'audit',
        'independent', 'chairman', 'ceo', 'cfo', 'management', 'remuneration',
        'nomination', 'stakeholder'
    ],
    'strategy': [
        'strategy', 'plan', 'initiative', 'expansion', 'growth', 'investment',
        'opportunity', 'vision', 'mission', 'objective', 'target', 'roadmap',
        'acquisition', 'merger', 'partnership', 'diversification'
    ],
    'human_resources': [
        'employee', 'workforce', 'talent', 'compensation', 'benefit', 'training',
        'attrition', 'hiring', 'headcount', 'esop', 'stock option', 'hr'
    ],
    'technology': [
        'technology', 'digital', 'platform', 'software', 'data', 'ai', 'ml',
        'automation', 'cloud', 'infrastructure', 'api', 'mobile', 'app',
        'algorithm', 'machine learning', 'analytics'
    ],
    'regulatory': [
        'regulation', 'compliance', 'law', 'government', 'policy', 'license',
        'permit', 'sebi', 'rbi', 'ministry', 'act', 'rule', 'notification',
        'statutory', 'legal'
    ],
    'sustainability': [
        'esg', 'sustainability', 'environment', 'social', 'carbon', 'emission',
        'green', 'renewable', 'climate', 'diversity', 'inclusion', 'csr'
    ],
    'related_party': [
        'related party', 'transaction', 'subsidiary', 'associate', 'joint venture',
        'holding company', 'promoter', 'affiliate', 'group company'
    ],
    'capital_structure': [
        'share', 'equity', 'debt', 'capital', 'ipo', 'offer', 'allotment',
        'shareholder', 'stake', 'dilution', 'fundraise', 'valuation'
    ],
    'key_metrics': [
        'kpi', 'metric', 'indicator', 'ratio', 'gmv', 'nmv', 'aov', 'arpu',
        'dau', 'mau', 'ltv', 'cac', 'churn', 'retention', 'conversion'
    ]
}

# Query expansion synonyms
QUERY_SYNONYMS = {
    'revenue': ['sales', 'turnover', 'income', 'top line'],
    'profit': ['earnings', 'net income', 'bottom line', 'surplus'],
    'loss': ['deficit', 'negative', 'decline'],
    'growth': ['increase', 'expansion', 'rise', 'improvement'],
    'risk': ['threat', 'challenge', 'concern', 'issue'],
    'employee': ['staff', 'workforce', 'team', 'personnel'],
    'customer': ['consumer', 'user', 'buyer', 'client'],
    'strategy': ['plan', 'approach', 'initiative', 'roadmap'],
}

# Financial metrics extraction patterns
FINANCIAL_PATTERNS = {
    'revenue': r'(?:revenue|sales|turnover)[\s:]+(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|crore|lakh)?',
    'profit': r'(?:profit|net income|earnings)[\s:]+(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|crore|lakh)?',
    'ebitda': r'(?:ebitda|adjusted ebitda)[\s:]+(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|crore|lakh)?',
    'gmv': r'(?:gmv|gross merchandise value)[\s:]+(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|crore|lakh)?',
    'margin_pct': r'(?:margin|growth)[\s:]+(\d+(?:\.\d+)?)\s*%',
    'yoy_growth': r'(?:yoy|y-o-y|year.over.year)[\s:]+(\d+(?:\.\d+)?)\s*%',
}

# Entity extraction patterns
ENTITY_PATTERNS = {
    'monetary': r'(?:₹|Rs\.?|INR|USD|\$)\s*[\d,]+(?:\.\d+)?\s*(?:million|billion|crore|lakh)?',
    'percentage': r'\d+(?:\.\d+)?%',
    'date': r'(?:March|April|September|December|January|February|May|June|July|August|October|November)\s+\d{1,2},?\s+\d{4}',
    'fiscal_year': r'(?:FY|Fiscal(?:al)?\s*(?:Year)?)\s*\'?\d{2,4}(?:-\d{2,4})?',
    'quarter': r'Q[1-4]\s*(?:FY)?\s*\'?\d{2,4}',
}

