#!/usr/bin/env python3
"""
Documentation Creation Helper Script

Creates documentation files following the manifest rules.
Usage: python scripts/docs/create_doc.py --type <doc_type> --title "Document Title"
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_manifest() -> dict:
    """Load the doc_manifest.json file."""
    manifest_path = Path(__file__).parent.parent.parent / "docs" / "doc_manifest.json"
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return slug.strip("-")


def create_doc(doc_type: str, title: str, number: str | None = None) -> None:
    """Create a new document following manifest rules."""
    manifest = load_manifest()

    if doc_type not in manifest["doc_types"]:
        print(f"Error: Unknown doc_type '{doc_type}'")
        print(f"Available types: {list(manifest['doc_types'].keys())}")
        sys.exit(1)

    config = manifest["doc_types"][doc_type]
    directory = Path(__file__).parent.parent.parent / config["directory"]
    template = config["template"]

    # Build filename
    slug = slugify(title)
    filename = template.format(
        slug=slug, number=number or "000", date=datetime.now().strftime("%Y-%m-%d")
    )

    # Create directory if needed
    directory.mkdir(parents=True, exist_ok=True)

    # Create file
    filepath = directory / filename
    if filepath.exists():
        print(f"Error: File already exists: {filepath}")
        sys.exit(1)

    # Write template content
    content = f"# {title}\n\n<!-- {config.get('description', doc_type)} -->\n\n"

    if doc_type == "adr":
        content = f"""# ADR-{number}: {title}

**Status**: Proposed
**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Deciders**: [List of decision makers]

## Context

[What is the issue we're addressing?]

## Decision

[What decision did we make?]

## Consequences

**Positive**:
- [List benefits]

**Negative**:
- [List drawbacks]

## Alternatives Considered

[What else was considered?]
"""

    filepath.write_text(content)
    print(f"Created: {filepath}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create documentation files")
    parser.add_argument("--type", required=True, help="Document type (e.g., guide, adr, roadmap)")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--number", help="ADR number (for ADR type only)")

    args = parser.parse_args()
    create_doc(args.type, args.title, args.number)


if __name__ == "__main__":
    main()
