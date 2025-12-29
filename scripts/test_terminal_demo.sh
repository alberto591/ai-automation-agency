#!/bin/bash
# Test script for terminal_demo.py
# Simulates a conversation to verify functionality

echo "Testing terminal demo with automated input..."

# Create test input
cat << 'EOF' | ./venv/bin/python scripts/terminal_demo.py
Ciao, cerco una casa in Toscana con budget 500k
quit
EOF

echo ""
echo "Test completed. Check output above for errors."
