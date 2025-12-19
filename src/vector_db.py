#!/usr/bin/env python3
"""
Vector Database CLI - wrapper for qualitative_db package.

This file provides backward compatibility. 
The actual implementation is in the qualitative_db/ package.

Usage:
    python vector_db.py --help
    python vector_db.py --add-doc report.pdf --company "Meesho" --year 2024 --type prospectus --sector technology
    python vector_db.py --query "What is the revenue?"
    python vector_db.py -i
"""

from qualitative_db.cli import main

if __name__ == "__main__":
    main()
