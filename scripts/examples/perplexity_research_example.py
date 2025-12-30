#!/usr/bin/env python3
"""
Example usage of Perplexity Labs integration for real-time research.

Usage:
    PERPLEXITY_API_KEY=pplx-xxx PYTHONPATH=. python scripts/examples/perplexity_research_example.py
"""

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def example_legal_compliance_check():
    """Example 1: Check for recent legal/regulation updates."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Legal Compliance Check")
    print("=" * 80)

    query = """
    Check Gazzetta Ufficiale and official Italian government sources
    for any changes to 'Bonus Ristrutturazioni' or 'Superbonus'
    regulations in the last 7 days. Summarize in Italian.
    """

    print(f"\nQuery: {query.strip()}")
    print("\nSearching...\n")

    result = container.research.search(query)
    print(f"Result:\n{result}\n")


def example_market_comparables():
    """Example 2: Find live market comparables without scraping."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Live Market Comparables")
    print("=" * 80)

    query = """
    Find 3 currently active real estate listings for 2-bedroom
    apartments in Brera, Milan with prices above €500,000.
    Include: price, size (m²), and listing source (if available).
    """

    print(f"\nQuery: {query.strip()}")
    print("\nSearching...\n")

    result = container.research.search(query)
    print(f"Result:\n{result}\n")


def example_entity_vetting():
    """Example 3: Background check on construction company."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Entity Vetting")
    print("=" * 80)

    # Using a well-known construction company for demo
    query = """
    Research 'Webuild' (formerly Salini Impregilo) construction company in Italy.
    Find: current status, recent major projects, and reputation.
    Provide a brief summary in English.
    """

    print(f"\nQuery: {query.strip()}")
    print("\nSearching...\n")

    result = container.research.search(query)
    print(f"Result:\n{result}\n")


def example_with_context():
    """Example 4: Research with context for better results."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Research with Context")
    print("=" * 80)

    context = "I'm an Italian real estate agent looking to advise a client."
    query = "What are the key features and amenities in the Porta Nuova district of Milan?"

    print(f"\nContext: {context}")
    print(f"Query: {query}")
    print("\nSearching...\n")

    result = container.research.search(query, context=context)
    print(f"Result:\n{result}\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PERPLEXITY LABS INTEGRATION - USAGE EXAMPLES")
    print("=" * 80)

    # Run all examples
    try:
        example_legal_compliance_check()
        example_market_comparables()
        example_entity_vetting()
        example_with_context()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error("EXAMPLE_FAILED", context={"error": str(e)})
        print(f"\n❌ Error: {e}")
        print("\nMake sure PERPLEXITY_API_KEY is set in your .env file")
