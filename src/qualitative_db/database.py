"""
ChromaDB vector database wrapper.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

from .config import CHROMA_PERSIST_DIR, COLLECTION_NAME
from .extractors import extract_content_from_pdf, extract_entities, extract_financial_metrics
from .chunking import create_parent_child_chunks
from .classification import classify_topics, expand_query


class QualitativeDataVectorDB:
    """Vector database with parent-child chunking strategy."""
    
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIR):
        """Initialize ChromaDB client and collections."""
        self.persist_directory = persist_directory
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Child collection for search
        self.child_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_children",
            embedding_function=self.embedding_function,
            metadata={"description": "Small chunks for precise semantic search"}
        )
        
        # Parent collection for context
        self.parent_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_parents",
            embedding_function=self.embedding_function,
            metadata={"description": "Large chunks for LLM context"}
        )
        
        # Metrics collection for structured financial data
        self.metrics_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_metrics",
            embedding_function=self.embedding_function,
            metadata={"description": "Structured financial metrics"}
        )
    
    def add_document(
        self,
        pdf_path: str,
        company_name: str,
        doc_year: int,
        doc_type: str,
        company_sector: str,
        doc_quarter: Optional[str] = None,
    ) -> dict:
        """Process a PDF with improved chunking and quality filtering."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        print(f"📄 Processing: {pdf_path.name}")
        print(f"   Company: {company_name} | Year: {doc_year} | Type: {doc_type}")
        
        # Extract content
        print("   Extracting text and tables...")
        content_blocks = extract_content_from_pdf(str(pdf_path))
        
        table_count = sum(1 for b in content_blocks if b['is_table'])
        text_blocks = sum(1 for b in content_blocks if not b['is_table'])
        print(f"   Found {text_blocks} text blocks and {table_count} quality tables")
        
        # Create chunks with quality filtering
        print("   Creating parent-child chunks...")
        parent_chunks, child_chunks = create_parent_child_chunks(content_blocks)
        print(f"   Created {len(parent_chunks)} parents, {len(child_chunks)} children")
        
        creation_date = datetime.now().isoformat()
        doc_prefix = f"{company_name}_{doc_year}_{doc_type}"
        
        # Extract and store financial metrics
        print("   Extracting financial metrics...")
        all_metrics = []
        for parent in parent_chunks:
            metrics = extract_financial_metrics(parent['text'])
            for m in metrics:
                m['parent_id'] = parent['id']
                m['section'] = parent['section']
                all_metrics.append(m)
        
        if all_metrics:
            self._add_metrics(all_metrics, doc_prefix, company_name, doc_year)
            print(f"   Stored {len(all_metrics)} financial metrics")
        
        # Add parent chunks
        print("   Adding parent chunks...")
        self._add_parents(parent_chunks, doc_prefix, company_name, doc_year,
                         doc_quarter, doc_type, company_sector, pdf_path.name, creation_date)
        print(f"      Added {len(parent_chunks)} parents")
        
        # Add child chunks
        print("   Adding child chunks...")
        self._add_children(child_chunks, doc_prefix, company_name, doc_year,
                          doc_quarter, doc_type, company_sector, pdf_path.name, creation_date)
        print(f"      Added {len(child_chunks)} children")
        
        print(f"✅ Successfully processed {company_name}")
        
        return self._print_summary(parent_chunks, child_chunks, all_metrics)
    
    def _add_metrics(self, metrics: list, doc_prefix: str, company_name: str, doc_year: int):
        """Add financial metrics to the metrics collection."""
        metric_ids = [f"{doc_prefix}_metric_{i}" for i in range(len(metrics))]
        metric_docs = [f"{m['type']}: {m['value']} - {m['context']}" for m in metrics]
        metric_metas = [{
            'company_name': company_name,
            'doc_year': doc_year,
            'metric_type': m['type'],
            'value': m['value'],
            'context': m['context'],
            'section': m['section']
        } for m in metrics]
        
        self.metrics_collection.add(
            ids=metric_ids,
            documents=metric_docs,
            metadatas=metric_metas
        )
    
    def _add_parents(self, parents: list, doc_prefix: str, company_name: str,
                     doc_year: int, doc_quarter: Optional[str], doc_type: str,
                     company_sector: str, source_file: str, creation_date: str):
        """Add parent chunks to the parent collection."""
        parent_ids = []
        parent_documents = []
        parent_metadatas = []
        
        for i, parent in enumerate(parents):
            parent_id = f"{doc_prefix}_parent_{i}"
            parent_ids.append(parent_id)
            parent_documents.append(parent['text'])
            
            primary_topic, secondary_topics = classify_topics(parent['text'])
            entities = extract_entities(parent['text'])
            has_financial = bool(extract_financial_metrics(parent['text']))
            
            metadata = {
                'company_name': company_name,
                'doc_year': doc_year,
                'doc_quarter': doc_quarter or "",
                'doc_type': doc_type,
                'company_sector': company_sector,
                'source_file': source_file,
                'chunk_id': i,
                'parent_id': parent_id,
                'creation_date': creation_date,
                'section': parent['section'],
                'topic': primary_topic,
                'secondary_topics': json.dumps(secondary_topics),
                'entities': json.dumps(entities),
                'page_numbers': ','.join(map(str, parent['pages'])),
                'is_table': parent['is_table'],
                'is_child': False,
                'has_financial_data': has_financial,
                'content_quality': parent.get('quality', 'medium')
            }
            parent_metadatas.append(metadata)
        
        # Batch add
        batch_size = 100
        for i in range(0, len(parent_ids), batch_size):
            end_idx = min(i + batch_size, len(parent_ids))
            self.parent_collection.add(
                ids=parent_ids[i:end_idx],
                documents=parent_documents[i:end_idx],
                metadatas=parent_metadatas[i:end_idx]
            )
    
    def _add_children(self, children: list, doc_prefix: str, company_name: str,
                      doc_year: int, doc_quarter: Optional[str], doc_type: str,
                      company_sector: str, source_file: str, creation_date: str):
        """Add child chunks to the child collection."""
        child_ids = []
        child_documents = []
        child_metadatas = []
        
        for i, child in enumerate(children):
            child_id = f"{doc_prefix}_child_{i}"
            parent_id = f"{doc_prefix}_parent_{child['parent_idx']}"
            
            child_ids.append(child_id)
            child_documents.append(child['text'])
            
            primary_topic, _ = classify_topics(child['text'])
            
            metadata = {
                'company_name': company_name,
                'doc_year': doc_year,
                'doc_quarter': doc_quarter or "",
                'doc_type': doc_type,
                'company_sector': company_sector,
                'source_file': source_file,
                'chunk_id': i,
                'parent_id': parent_id,
                'creation_date': creation_date,
                'section': child['section'],
                'topic': primary_topic,
                'page_numbers': ','.join(map(str, child['pages'])),
                'is_table': child['is_table'],
                'is_child': True
            }
            child_metadatas.append(metadata)
        
        batch_size = 100
        for i in range(0, len(child_ids), batch_size):
            end_idx = min(i + batch_size, len(child_ids))
            self.child_collection.add(
                ids=child_ids[i:end_idx],
                documents=child_documents[i:end_idx],
                metadatas=child_metadatas[i:end_idx]
            )
    
    def _print_summary(self, parents: list, children: list, metrics: list) -> dict:
        """Print and return summary statistics."""
        table_chunks = sum(1 for p in parents if p['is_table'])
        
        quality_counts = {}
        topic_counts = {}
        for p in parents:
            q = p.get('quality', 'medium')
            quality_counts[q] = quality_counts.get(q, 0) + 1
            primary, _ = classify_topics(p['text'])
            topic_counts[primary] = topic_counts.get(primary, 0) + 1
        
        print(f"\n📊 Summary:")
        print(f"   Parents: {len(parents)} | Children: {len(children)}")
        print(f"   Tables: {table_chunks} | Metrics: {len(metrics)}")
        print(f"\n   Quality: {quality_counts}")
        print(f"\n   Topics (top 5):")
        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"      {topic}: {count}")
        
        return {
            'parent_count': len(parents),
            'child_count': len(children),
            'table_count': table_chunks,
            'metrics_count': len(metrics)
        }
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        company_name: Optional[str] = None,
        doc_type: Optional[str] = None,
        doc_year: Optional[int] = None,
        topic: Optional[str] = None,
        tables_only: bool = False,
        high_quality_only: bool = False,
        expand_query_terms: bool = True,
    ) -> list[dict]:
        """Query with small-to-big retrieval."""
        search_query = expand_query(query_text) if expand_query_terms else query_text
        
        # Build filter
        where = self._build_where_clause(company_name, doc_type, doc_year, topic, tables_only)
        
        # Search child chunks
        child_results = self.child_collection.query(
            query_texts=[search_query],
            n_results=n_results * 4,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        if not child_results['ids'][0]:
            return []
        
        # Aggregate by parent
        parent_matches = self._aggregate_parent_matches(child_results)
        
        # Get parent chunks
        parent_ids = list(parent_matches.keys())[:n_results * 2]
        
        parent_results = self.parent_collection.get(
            ids=parent_ids,
            include=["documents", "metadatas"]
        )
        
        # Format and filter results
        return self._format_results(parent_results, parent_matches, n_results, high_quality_only)
    
    def _build_where_clause(self, company_name, doc_type, doc_year, topic, tables_only):
        """Build ChromaDB where clause."""
        where_clauses = []
        if company_name:
            where_clauses.append({"company_name": company_name})
        if doc_type:
            where_clauses.append({"doc_type": doc_type})
        if doc_year:
            where_clauses.append({"doc_year": doc_year})
        if topic:
            where_clauses.append({"topic": topic})
        if tables_only:
            where_clauses.append({"is_table": True})
        
        if len(where_clauses) == 0:
            return None
        elif len(where_clauses) == 1:
            return where_clauses[0]
        else:
            return {"$and": where_clauses}
    
    def _aggregate_parent_matches(self, child_results) -> dict:
        """Aggregate child matches by parent."""
        parent_matches = {}
        
        for i, child_id in enumerate(child_results['ids'][0]):
            parent_id = child_results['metadatas'][0][i]['parent_id']
            distance = child_results['distances'][0][i]
            child_text = child_results['documents'][0][i]
            
            if parent_id not in parent_matches:
                parent_matches[parent_id] = {
                    'best_distance': distance,
                    'matched_children': [],
                    'metadata': child_results['metadatas'][0][i]
                }
            
            parent_matches[parent_id]['matched_children'].append({
                'text': child_text,
                'distance': distance
            })
            
            if distance < parent_matches[parent_id]['best_distance']:
                parent_matches[parent_id]['best_distance'] = distance
        
        return parent_matches
    
    def _format_results(self, parent_results, parent_matches, n_results, high_quality_only) -> list:
        """Format query results."""
        formatted = []
        
        for i, parent_id in enumerate(parent_results['ids']):
            metadata = parent_results['metadatas'][i]
            
            if high_quality_only and metadata.get('content_quality') == 'low':
                continue
            
            match_info = parent_matches[parent_id]
            
            formatted.append({
                'id': parent_id,
                'text': parent_results['documents'][i],
                'metadata': metadata,
                'relevance_score': 1 - match_info['best_distance'],
                'distance': match_info['best_distance'],
                'matched_snippets': sorted(
                    match_info['matched_children'],
                    key=lambda x: x['distance']
                )[:3]
            })
        
        formatted.sort(key=lambda x: x['distance'])
        return formatted[:n_results]
    
    def query_metrics(
        self,
        query_text: str,
        n_results: int = 10,
        metric_type: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> list[dict]:
        """Query structured financial metrics."""
        where = self._build_where_clause(company_name, None, None, None, False)
        if metric_type:
            if where:
                where = {"$and": [where, {"metric_type": metric_type}]}
            else:
                where = {"metric_type": metric_type}
        
        results = self.metrics_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'relevance_score': 1 - results['distances'][0][i]
            })
        
        return formatted
    
    def query_tables(self, query_text: str, n_results: int = 5, **filters) -> list[dict]:
        """Query specifically for tables."""
        return self.query(query_text, n_results=n_results, tables_only=True, **filters)
    
    def get_collection_stats(self) -> dict:
        """Get comprehensive statistics."""
        parent_results = self.parent_collection.get(include=["metadatas"])
        child_results = self.child_collection.get(include=["metadatas"])
        
        try:
            metrics_results = self.metrics_collection.get(include=["metadatas"])
            metrics_count = len(metrics_results['ids'])
        except:
            metrics_count = 0
        
        stats = {
            'total_parents': len(parent_results['ids']),
            'total_children': len(child_results['ids']),
            'total_metrics': metrics_count,
            'companies': {},
            'doc_types': {},
            'topics': {},
            'quality': {},
            'table_count': 0,
            'high_quality_count': 0,
            'sectors': set()
        }
        
        for metadata in parent_results['metadatas']:
            company = metadata.get('company_name', 'Unknown')
            doc_type = metadata.get('doc_type', 'Unknown')
            topic = metadata.get('topic', 'Unknown')
            sector = metadata.get('company_sector', 'Unknown')
            quality = metadata.get('content_quality', 'medium')
            is_table = metadata.get('is_table', False)
            
            stats['companies'][company] = stats['companies'].get(company, 0) + 1
            stats['doc_types'][doc_type] = stats['doc_types'].get(doc_type, 0) + 1
            stats['topics'][topic] = stats['topics'].get(topic, 0) + 1
            stats['quality'][quality] = stats['quality'].get(quality, 0) + 1
            stats['sectors'].add(sector)
            
            if is_table:
                stats['table_count'] += 1
            if quality == 'high':
                stats['high_quality_count'] += 1
        
        stats['sectors'] = sorted(stats['sectors'])
        return stats
    
    def get_companies(self) -> list[str]:
        """Get all companies in the database."""
        results = self.parent_collection.get(include=["metadatas"])
        companies = set()
        for metadata in results['metadatas']:
            if 'company_name' in metadata:
                companies.add(metadata['company_name'])
        return sorted(companies)
    
    def delete_company(self, company_name: str) -> int:
        """Delete all data for a company."""
        total = 0
        
        for collection in [self.child_collection, self.parent_collection, self.metrics_collection]:
            try:
                results = collection.get(where={"company_name": company_name}, include=[])
                if results['ids']:
                    collection.delete(ids=results['ids'])
                    total += len(results['ids'])
            except:
                pass
        
        print(f"🗑️  Deleted {total} chunks for {company_name}")
        return total
    
    def clear_collection(self):
        """Clear all data."""
        for name in [f"{COLLECTION_NAME}_children", f"{COLLECTION_NAME}_parents", f"{COLLECTION_NAME}_metrics"]:
            try:
                self.client.delete_collection(name)
            except:
                pass
        
        self.child_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_children",
            embedding_function=self.embedding_function
        )
        self.parent_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_parents",
            embedding_function=self.embedding_function
        )
        self.metrics_collection = self.client.get_or_create_collection(
            name=f"{COLLECTION_NAME}_metrics",
            embedding_function=self.embedding_function
        )
        print("🗑️  Collections cleared")

