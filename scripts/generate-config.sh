#!/bin/sh
# Generate config.js from environment variables for landing page
# This script should be run during build/deployment

set -e

# Check if required environment variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set"
    echo "Usage: SUPABASE_URL=<url> SUPABASE_ANON_KEY=<key> $0"
    exit 1
fi

# Generate config.js for landing page
cat > apps/landing-page/config.js << EOF
/**
 * Environment Configuration
 * Auto-generated at build time - DO NOT EDIT
 */
window.ENV = {
    SUPABASE_URL: '${SUPABASE_URL}',
    SUPABASE_ANON_KEY: '${SUPABASE_ANON_KEY}'
};
EOF

echo "✅ Generated apps/landing-page/config.js"

# Also generate for dist if it exists
if [ -d "dist" ]; then
    cp apps/landing-page/config.js dist/config.js
    echo "✅ Copied to dist/config.js"
fi
