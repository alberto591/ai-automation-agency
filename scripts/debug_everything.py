#!/usr/bin/env python3
"""
Debug Everything Protocol Script
Run this to validate system health and catch common issues.
"""
import os
import re
import sys
import subprocess
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

APP_ROOT = Path(__file__).parent.parent

def check_env_vars():
    """Verify essential environment variables are set."""
    print(f"\n{GREEN}[+] Checking Environment Variables...{RESET}")
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "MISTRAL_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
    ]
    missing = []
    # Load .env if present
    env_path = APP_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"{RED}[FAIL] Missing variables: {', '.join(missing)}{RESET}")
        return False
    print(f"{GREEN}[PASS] All required variables present.{RESET}")
    return True

def static_analysis_checks():
    """Run grep checks for dangerous patterns."""
    print(f"\n{GREEN}[+] Running Static Analysis...{RESET}")
    patterns = [
        (r"password\s*=", "Hardcoded password assignment"),
        (r"api_key\s*=", "Hardcoded API key assignment"),
        (r"print\(", "Leftover print statements (use logger)"),
        (r"except.*:\s*pass", "Bare except pass"),
    ]
    
    issues_found = False
    for root, _, files in os.walk(APP_ROOT):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            if not file.endswith(".py"):
                continue
            path = Path(root) / file
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern, desc in patterns:
                        if re.search(pattern, content):
                            print(f"{RED}[WARN] {desc} found in {path.relative_to(APP_ROOT)}{RESET}")
                            issues_found = True
            except:
                pass
                
    if not issues_found:
        print(f"{GREEN}[PASS] No critical static patterns found.{RESET}")
    else:
        print(f"{RED}[WARN] Issues found. Please review above.{RESET}")

def run_tests():
    """Run unit tests using pytest."""
    print(f"\n{GREEN}[+] Running Unit Tests...{RESET}")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/unit"], check=True)
        print(f"{GREEN}[PASS] Unit tests passed.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}[FAIL] Unit tests failed.{RESET}")

if __name__ == "__main__":
    print(f"{GREEN}=== ANZEVINO AI DEBUG PROTOCOL ==={RESET}")
    check_env_vars()
    static_analysis_checks()
    # verify_db_connection() # TODO: Add connectivity check
    # run_tests() # Optional: Uncomment to run tests on every debug
    print(f"\n{GREEN}=== DEBUG COMPLETE ==={RESET}")
