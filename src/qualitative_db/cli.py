"""
Command-line interface for the vector database.
"""

import argparse

from .config import TOPIC_KEYWORDS
from .database import QualitativeDataVectorDB
from .formatting import get_context_for_llm, print_query_results


def interactive_query(db: QualitativeDataVectorDB):
    """Run an interactive query session."""
    print("\n" + "="*60)
    print("🔍 Interactive Query Mode")
    print("   Commands:")
    print("     'stats' - Show database statistics")
    print("     'metrics <query>' - Search financial metrics")
    print("     'tables <query>' - Search tables only")
    print("     'companies' - List companies")
    print("     'quit' - Exit")
    print("="*60 + "\n")
    
    while True:
        try:
            query = input("\n💬 Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if query.lower() == 'stats':
            stats = db.get_collection_stats()
            print(f"\n📊 Database Statistics:")
            print(f"   Parents: {stats['total_parents']} | Children: {stats['total_children']}")
            print(f"   Metrics: {stats['total_metrics']} | Tables: {stats['table_count']}")
            print(f"   High-quality: {stats['high_quality_count']}")
            print(f"\n   Quality: {stats['quality']}")
            continue
        
        if query.lower() == 'companies':
            companies = db.get_companies()
            print(f"\n🏢 Companies: {', '.join(companies) if companies else 'None'}")
            continue
        
        if query.lower().startswith('metrics '):
            metric_query = query[8:]
            results = db.query_metrics(metric_query, n_results=5)
            print(f"\n💰 Financial Metrics for: '{metric_query}'")
            for r in results:
                m = r['metadata']
                print(f"   {m.get('metric_type', '?')}: {m.get('value', '?')} ({r['relevance_score']:.0%})")
                print(f"      {m.get('context', '')[:80]}...")
            continue
        
        if query.lower().startswith('tables '):
            table_query = query[7:]
            results = db.query_tables(table_query, n_results=2)
            print(f"\n📊 Tables for: '{table_query}'")
            print_query_results(results, max_text_len=500)
            continue
        
        if not query:
            continue
        
        results = db.query(query, n_results=3, high_quality_only=True)
        print(f"\n📊 Results (searched {db.child_collection.count()} chunks):\n")
        print_query_results(results)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Company Qualitative Data Vector Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a document
  python -m qualitative_db --add-doc report.pdf --company "Meesho" --year 2024 --type prospectus --sector technology

  # Query
  python -m qualitative_db --query "What is the revenue growth?"

  # Interactive mode
  python -m qualitative_db -i
        """
    )
    
    # Actions
    parser.add_argument("--add-doc", type=str, metavar="PDF", help="PDF file to add")
    parser.add_argument("--query", "-q", type=str, help="Search query")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--companies", action="store_true", help="List companies")
    parser.add_argument("--clear", action="store_true", help="Clear all data")
    parser.add_argument("--delete-company", type=str, help="Delete company data")
    parser.add_argument("--llm-context", type=str, help="Get LLM-ready context")
    parser.add_argument("--metrics", type=str, help="Query financial metrics")
    
    # Document metadata
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--year", type=int, help="Document year")
    parser.add_argument("--quarter", type=str, choices=['Q1', 'Q2', 'Q3', 'Q4'])
    parser.add_argument("--type", type=str,
                       choices=['report', 'concall', 'prospectus', 'presentation', 'filing', 'other'])
    parser.add_argument("--sector", type=str, help="Company sector")
    
    # Query options
    parser.add_argument("--tables-only", action="store_true")
    parser.add_argument("--high-quality", action="store_true")
    parser.add_argument("--topic", type=str, choices=list(TOPIC_KEYWORDS.keys()))
    parser.add_argument("-n", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    db = QualitativeDataVectorDB()
    
    if args.clear:
        db.clear_collection()
        return
    
    if args.delete_company:
        db.delete_company(args.delete_company)
        return
    
    if args.stats:
        stats = db.get_collection_stats()
        print(f"\n📊 Database Statistics:")
        print(f"   Parents: {stats['total_parents']} (LLM context)")
        print(f"   Children: {stats['total_children']} (search)")
        print(f"   Metrics: {stats['total_metrics']}")
        print(f"   Tables: {stats['table_count']}")
        print(f"   High-quality: {stats['high_quality_count']}")
        print(f"\n   Companies: {list(stats['companies'].keys())}")
        print(f"   Quality: {stats['quality']}")
        print(f"\n   Topics:")
        for topic, count in sorted(stats['topics'].items(), key=lambda x: -x[1]):
            print(f"      {topic}: {count}")
        return
    
    if args.companies:
        companies = db.get_companies()
        print(f"\n🏢 Companies: {', '.join(companies) if companies else 'None'}")
        return
    
    if args.add_doc:
        if not all([args.company, args.year, args.type, args.sector]):
            parser.error("--add-doc requires --company, --year, --type, and --sector")
        
        db.add_document(
            pdf_path=args.add_doc,
            company_name=args.company,
            doc_year=args.year,
            doc_type=args.type,
            company_sector=args.sector,
            doc_quarter=args.quarter
        )
        return
    
    if args.metrics:
        results = db.query_metrics(args.metrics, n_results=args.n, company_name=args.company)
        print(f"\n💰 Financial Metrics for: '{args.metrics}'")
        for r in results:
            m = r['metadata']
            print(f"\n   {m.get('metric_type', '?')}: {m.get('value', '?')}")
            print(f"   Section: {m.get('section', '?')}")
            print(f"   Context: {m.get('context', '')[:100]}...")
        return
    
    if args.llm_context:
        context = get_context_for_llm(
            db, args.llm_context, n_results=args.n,
            company_name=args.company,
            doc_type=args.type,
            doc_year=args.year,
            topic=args.topic,
            tables_only=args.tables_only
        )
        print(context)
        return
    
    if args.query:
        results = db.query(
            args.query,
            n_results=args.n,
            company_name=args.company,
            doc_type=args.type,
            doc_year=args.year,
            topic=args.topic,
            tables_only=args.tables_only,
            high_quality_only=args.high_quality
        )
        
        print(f"\n📊 Results for: '{args.query}'")
        print(f"   (searched {db.child_collection.count()} chunks)\n")
        print_query_results(results)
        return
    
    if args.interactive:
        interactive_query(db)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()

