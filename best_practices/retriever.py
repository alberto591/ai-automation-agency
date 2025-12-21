import sys
import json
from best_practices import CODE_PATTERNS

def list_patterns():
    """Output all patterns as JSON."""
    print(json.dumps(CODE_PATTERNS, indent=2))

if __name__ == "__main__":
    list_patterns()
