#!/usr/bin/env node
/**
 * Generate config.js from environment variables for landing page
 * This script should be run during build/deployment in Vercel
 */

const fs = require('fs');
const path = require('path');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;

// Check if required environment variables are set
if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set');
    console.error('Set these in Vercel Environment Variables');
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

// Generate for apps/landing-page
const landingPagePath = path.join(__dirname, '..', 'apps', 'landing-page', 'config.js');
fs.writeFileSync(landingPagePath, configContent);
console.log('✅ Generated apps/landing-page/config.js');

// Generate for dist if it exists
const distPath = path.join(__dirname, '..', 'dist', 'config.js');
const distDir = path.dirname(distPath);
if (fs.existsSync(distDir)) {
    fs.writeFileSync(distPath, configContent);
    console.log('✅ Generated dist/config.js');
}

console.log('✅ Config generation complete!');
