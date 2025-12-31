import json

from best_practices import CODE_PATTERNS


def list_patterns(format_type: str = "json") -> None:
    """Output all patterns."""
    if format_type == "json":
        print(json.dumps(CODE_PATTERNS, indent=2))
    elif format_type == "markdown":
        print("# Best Practices Catalog\n")
        for key, p in CODE_PATTERNS.items():
            print(f"## {p['name']} (`{key}`)")
            print(f"**ID**: {p.get('id')}")
            print(f"**Tags**: {', '.join(p.get('tags', []))}")
            print(f"\n{p['description']}\n")
            if "snippet" in p:
                print(f"```python\n{p['snippet']}\n```\n")
            print("---\n")


if __name__ == "__main__":
    import sys

    fmt = "json"
    if len(sys.argv) > 1 and sys.argv[1] == "--md":
        fmt = "markdown"
    list_patterns(fmt)
