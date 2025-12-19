"""
Chunking strategies for parent-child retrieval.
"""

import re
from .config import CHILD_CHUNK_SIZE, CHILD_CHUNK_OVERLAP, PARENT_CHUNK_SIZE
from .extractors import detect_section_header


def assess_content_quality(text: str, is_table: bool) -> str:
    """Assess the quality of content for retrieval."""
    if len(text) < 100:
        return 'low'
    
    text_lower = text.lower()
    
    boilerplate = [
        'page intentionally left blank',
        'this page has been',
        'for more information',
        'see section',
        'as per',
        'disclaimer',
        'forward-looking statement'
    ]
    
    boilerplate_count = sum(1 for b in boilerplate if b in text_lower)
    if boilerplate_count >= 2:
        return 'low'
    
    has_numbers = bool(re.search(r'[\d,]+(?:\.\d+)?', text))
    has_entities = bool(re.search(r'(?:₹|Rs|%|\d{4})', text))
    
    if is_table:
        return 'high' if len(text) > 200 else 'medium'
    
    if has_numbers and has_entities and len(text) > 300:
        return 'high'
    elif len(text) > 200:
        return 'medium'
    else:
        return 'low'


def create_child_chunks(
    text: str,
    chunk_size: int = CHILD_CHUNK_SIZE,
    overlap: int = CHILD_CHUNK_OVERLAP
) -> list[str]:
    """Create small overlapping chunks for precise search."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if end < len(text):
            for sep in ['. ', '.\n', '? ', '! ', '\n\n']:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size // 2:
                    chunk = chunk[:last_sep + 1]
                    end = start + last_sep + 1
                    break
        
        if chunk.strip() and len(chunk.strip()) > 30:
            chunks.append(chunk.strip())
        
        start = end - overlap
    
    return chunks


def create_parent_child_chunks(content_blocks: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Create parent and child chunks with quality filtering.
    
    Returns: (parent_chunks, child_chunks)
    """
    parent_chunks = []
    child_chunks = []
    current_section = "Introduction"
    
    current_parent = {
        'text': '',
        'pages': set(),
        'section': current_section,
        'is_table': False
    }
    
    for block in content_blocks:
        # Tables are their own parent chunks
        if block['is_table']:
            if current_parent['text'].strip() and len(current_parent['text']) > 100:
                quality = assess_content_quality(current_parent['text'], False)
                if quality != 'low':
                    current_parent['pages'] = sorted(current_parent['pages'])
                    current_parent['quality'] = quality
                    parent_chunks.append(current_parent.copy())
            
            current_parent = {
                'text': '',
                'pages': set(),
                'section': current_section,
                'is_table': False
            }
            
            table_quality = assess_content_quality(block['text'], True)
            if table_quality != 'low':
                parent_chunks.append({
                    'text': block['text'],
                    'pages': [block['page_num']],
                    'section': block['section'],
                    'is_table': True,
                    'quality': table_quality
                })
            continue
        
        text = block['text']
        page_num = block['page_num']
        
        header = detect_section_header(text)
        if header:
            if current_parent['text'].strip() and len(current_parent['text']) > 100:
                quality = assess_content_quality(current_parent['text'], False)
                if quality != 'low':
                    current_parent['pages'] = sorted(current_parent['pages'])
                    current_parent['quality'] = quality
                    parent_chunks.append(current_parent.copy())
            
            current_section = header
            current_parent = {
                'text': text + '\n\n',
                'pages': {page_num},
                'section': header,
                'is_table': False
            }
        else:
            if len(current_parent['text']) + len(text) > PARENT_CHUNK_SIZE:
                if current_parent['text'].strip() and len(current_parent['text']) > 100:
                    quality = assess_content_quality(current_parent['text'], False)
                    if quality != 'low':
                        current_parent['pages'] = sorted(current_parent['pages'])
                        current_parent['quality'] = quality
                        parent_chunks.append(current_parent.copy())
                
                current_parent = {
                    'text': text + '\n\n',
                    'pages': {page_num},
                    'section': current_section,
                    'is_table': False
                }
            else:
                current_parent['text'] += text + '\n\n'
                current_parent['pages'].add(page_num)
    
    # Last parent
    if current_parent['text'].strip() and len(current_parent['text']) > 100:
        quality = assess_content_quality(current_parent['text'], False)
        if quality != 'low':
            current_parent['pages'] = sorted(current_parent['pages'])
            current_parent['quality'] = quality
            parent_chunks.append(current_parent)
    
    # Create child chunks from parents
    for parent_idx, parent in enumerate(parent_chunks):
        parent['id'] = f"parent_{parent_idx}"
        
        if parent['is_table']:
            child_chunks.append({
                'text': parent['text'],
                'parent_id': parent['id'],
                'parent_idx': parent_idx,
                'section': parent['section'],
                'pages': parent['pages'],
                'is_table': True
            })
        else:
            children = create_child_chunks(parent['text'])
            for child_text in children:
                child_chunks.append({
                    'text': child_text,
                    'parent_id': parent['id'],
                    'parent_idx': parent_idx,
                    'section': parent['section'],
                    'pages': parent['pages'],
                    'is_table': False
                })
    
    return parent_chunks, child_chunks

