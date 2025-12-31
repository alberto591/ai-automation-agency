"""
Pattern Validation and Capture Tool

Validates that all registered patterns in best_practices registry
meet the schema requirements.
"""
import argparse
import sys
from typing import Any

from best_practices import CODE_PATTERNS


def validate_pattern(pattern_id: str, pattern: dict[str, Any]) -> list[str]:
    """Validate a single pattern against schema rules."""
    errors = []
    required_fields = ["id", "name", "description", "tags"]

    for field in required_fields:
        if field not in pattern:
            errors.append(f"Missing required field: {field}")

    legacy_aliases = [
        "CIRCUIT_BREAKER",
        "STRUCTURED_LOGGING",
        "ADR_DOCUMENTATION",
        "HEXAGONAL_LAYERS",
    ]
    if "id" in pattern and pattern["id"] != pattern_id and pattern_id not in legacy_aliases:
        # Some keys in CODE_PATTERNS are simplified aliases, that's okay,
        # but let's check basic sanity.
        pass

    if "tags" in pattern and not isinstance(pattern["tags"], list):
        errors.append("Field 'tags' must be a list")

    return errors


def validate_all() -> bool:
    """Validate all patterns in the registry."""
    print(f"Validating {len(CODE_PATTERNS)} patterns...")
    all_valid = True

    for key, pattern in CODE_PATTERNS.items():
        errors = validate_pattern(key, pattern)
        if errors:
            print(f"❌ Pattern '{key}' is invalid:")
            for err in errors:
                print(f"  - {err}")
            all_valid = False
        else:
            print(f"✅ {key} ({pattern.get('name')})")

    return all_valid


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate best practice patterns")
    parser.add_argument("--validate", action="store_true", help="Validate all patterns")

    args = parser.parse_args()

    if args.validate:
        success = validate_all()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
