#!/usr/bin/env python3
import subprocess
import sys


def run_command(command, description):
    print(f"\n🔍 Running {description}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    print("🚀 STARTING PRE-FLIGHT CHECKS")

    success = True

    # 1. Pre-commit Hooks (Ruff, Mypy, Formatting, etc.)
    if not run_command(["./venv/bin/pre-commit", "run", "--all-files"], "Pre-commit Hooks"):
        success = False

    # 2. Unit Tests
    if not run_command(["./venv/bin/pytest", "tests/", "-v"], "Unit Tests"):
        success = False

    if success:
        print("\n✨ ALL PRE-FLIGHT CHECKS PASSED! You are ready to push.")
        sys.exit(0)
    else:
        print("\n🛑 PRE-FLIGHT CHECKS FAILED. Please fix the issues before pushing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
