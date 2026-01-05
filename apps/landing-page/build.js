import { copyFileSync, mkdirSync, readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Simple build script that copies files without transformation
function build() {
    const distDir = resolve(__dirname, 'dist');

    console.log('🚀 Building landing page...');

    // Create dist directory
    mkdirSync(distDir, { recursive: true });

    // Copy index.html as-is (no transformation!)
    console.log('📄 Copying index.html...');
    copyFileSync(
        resolve(__dirname, 'index.html'),
        resolve(distDir, 'index.html')
    );

    // Copy feedback.html if it exists
    try {
        console.log('📄 Copying feedback.html...');
        copyFileSync(
            resolve(__dirname, 'feedback.html'),
            resolve(distDir, 'feedback.html')
        );
    } catch (err) {
        console.log('ℹ️  feedback.html not found, skipping...');
    }

    // Copy appraisal folder recursively
    console.log('📁 Copying appraisal folder...');
    copyDirectory(
        resolve(__dirname, 'appraisal'),
        resolve(distDir, 'appraisal')
    );

    console.log('✅ Build complete!');
    console.log(`📦 Output: ${distDir}`);
}

function copyDirectory(src, dest) {
    mkdirSync(dest, { recursive: true });

    const entries = readdirSync(src);

    for (const entry of entries) {
        const srcPath = join(src, entry);
        const destPath = join(dest, entry);

        if (statSync(srcPath).isDirectory()) {
            copyDirectory(srcPath, destPath);
        } else {
            copyFileSync(srcPath, destPath);
            console.log(`  ✓ ${entry}`);
        }
    }
}

build();
