"""
Entry point for running the package as a module.

Usage:
    python -m qualitative_db --help
    python -m qualitative_db --add-doc report.pdf --company "Meesho" --year 2024 --type prospectus --sector technology
    python -m qualitative_db --query "What is the revenue?"
    python -m qualitative_db -i
"""

from .cli import main

if __name__ == "__main__":
    main()

