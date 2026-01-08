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

    // Copy all HTML files
    const htmlFiles = [
        'index.html',
        'login.html',
        'register.html',
        'forgot-password.html',
        'reset-password.html',
        'feedback.html',
        'test_interface.html',
        'test_language_switching.html'
    ];

    htmlFiles.forEach(file => {
        try {
            console.log(`📄 Copying ${file}...`);
            copyFileSync(
                resolve(__dirname, file),
                resolve(distDir, file)
            );
        } catch (err) {
            console.log(`ℹ️  ${file} not found, skipping...`);
        }
    });

    // Copy essential JS and CSS files
    const assetFiles = ['auth-helper.js', 'styles.css', 'script.js'];
    assetFiles.forEach(file => {
        try {
            console.log(`📄 Copying ${file}...`);
            copyFileSync(
                resolve(__dirname, file),
                resolve(distDir, file)
            );
        } catch (err) {
            console.log(`ℹ️  ${file} not found, skipping...`);
        }
    });

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
