#!/bin/bash
# Quick Run: Fifi Database Setup
# Executes migration and mock data upload

set -e  # Exit on error

echo "🏠 Fifi Database Setup - Quick Run"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

# Load Supabase credentials
source .env

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ Error: SUPABASE_URL or SUPABASE_KEY not set in .env"
    exit 1
fi

echo "📋 Step 1: Foundation Migration"
echo "--------------------------------"

# Extract project ref from URL (e.g., https://abc123.supabase.co -> abc123)
PROJECT_REF=$(echo $SUPABASE_URL | sed -E 's/https:\/\/([^.]+).*/\1/')

echo "Project: $PROJECT_REF"
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo ""
echo "1. Open: https://app.supabase.com/project/$PROJECT_REF/sql"
echo "2. Copy contents of: scripts/migrations/20251230_fifi_avm_foundation.sql"
echo "3. Paste and execute in SQL Editor"
echo ""
read -p "Press ENTER when foundation migration is complete..."

echo ""
echo "📊 Step 2: Mock Data Upload"
echo "----------------------------"
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo ""
echo "1. In the same SQL Editor tab"
echo "2. Copy contents of: scripts/migrations/mock_data_insert.sql"
echo "3. Paste and execute (500 INSERT statements)"
echo ""
read -p "Press ENTER when data upload is complete..."

echo ""
echo "✅ Step 3: Verification"
echo "----------------------"

# Run verification
echo ""
python3 ./venv/bin/python scripts/verify_fifi_setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 For detailed instructions, see: docs/guides/fifi-database-setup.md"
