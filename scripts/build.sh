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

# Build Fifi (Appraisal Tool)
cd ../fifi
npm install
npm run build
mkdir -p ../../dist/appraisal
cp -r dist/* ../../dist/appraisal/

# Build Landing Page
cd ../landing-page
npm install
npm run build
cp -r dist/* ../../dist/

echo "✅ All apps built successfully"
