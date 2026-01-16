#!/usr/bin/env node
/**
 * Generate config.js from environment variables for landing page
 * This script should be run during build/deployment in Vercel
 */

const fs = require('fs');
const path = require('path');

// Debug: Show what env vars we can see
console.log('🔍 Checking environment variables...');
console.log('Environment variable names present:', Object.keys(process.env).sort());

// Flexible mapping: Support both naming conventions
const SUPABASE_URL = (process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '').replace(/^['"]|['"]$/g, '');
const SUPABASE_ANON_KEY = (process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '').replace(/^['"]|['"]$/g, '');

console.log('SUPABASE_URL exists:', !!SUPABASE_URL);
console.log('SUPABASE_ANON_KEY exists:', !!SUPABASE_ANON_KEY);

// Check if required environment variables are set
if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set');
    // Debug: Show which one is missing
    if (!SUPABASE_URL) console.error('Missing: SUPABASE_URL (searched for SUPABASE_URL, NEXT_PUBLIC_SUPABASE_URL)');
    if (!SUPABASE_ANON_KEY) console.error('Missing: SUPABASE_ANON_KEY (searched for SUPABASE_ANON_KEY, SUPABASE_KEY, NEXT_PUBLIC_SUPABASE_ANON_KEY)');
    console.error('Available env vars starting with SUPA:', Object.keys(process.env).filter(k => k.toUpperCase().startsWith('SUPA')).join(', ') || 'none');
    process.exit(1);
}

const configContent = `/**
 * Environment Configuration
 * Auto-generated at build time - DO NOT EDIT
 */
window.ENV = {
    SUPABASE_URL: '${SUPABASE_URL}',
    SUPABASE_ANON_KEY: '${SUPABASE_ANON_KEY}'
};
`;

// 1. Always generate for dist (this is what Vercel serves)
const distPath = path.join(__dirname, '..', 'dist', 'config.js');
const distDir = path.dirname(distPath);

if (!fs.existsSync(distDir)) {
    console.log('📁 Creating dist directory...');
    fs.mkdirSync(distDir, { recursive: true });
}

fs.writeFileSync(distPath, configContent);
console.log('✅ Generated dist/config.js');

// 2. Also generate for apps/landing-page if it exists (for local/other builds)
const landingPageDir = path.join(__dirname, '..', 'apps', 'landing-page');
if (fs.existsSync(landingPageDir)) {
    const landingPagePath = path.join(landingPageDir, 'config.js');
    fs.writeFileSync(landingPagePath, configContent);
    console.log('✅ Generated apps/landing-page/config.js');
} else {
    console.log('ℹ️ apps/landing-page not found, skipping source config generation (normal in Vercel)');
}

console.log('✅ Config generation complete!');
