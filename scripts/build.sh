#!/bin/bash
# Vercel Build Script for Multi-App Frontend

set -e

mkdir -p dist

# Build Dashboard
cd apps/dashboard
npm install
npm run build
mkdir -p ../../dist/dashboard
cp -r dist/* ../../dist/dashboard/
rm -rf node_modules
cd ../..

# Build Fifi (Appraisal Tool)
cd apps/fifi
npm install
npm run build
mkdir -p ../../dist/appraisal
cp -r dist/* ../../dist/appraisal/
rm -rf node_modules
cd ../..

# Build Landing Page
cd apps/landing-page
npm install
npm run build
cp -r dist/* ../../dist/
rm -rf node_modules
cd ../..

echo "✅ All apps built successfully"
