import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, mkdirSync } from 'fs'
import { resolve } from 'path'

//https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-appraisal',
      writeBundle() {
        // Copy appraisal folder to dist after build
        const srcDir = resolve(__dirname, 'appraisal')
        const destDir = resolve(__dirname, 'dist/appraisal')

        // Create destination directory
        mkdirSync(destDir, { recursive: true })
        mkdirSync(resolve(destDir, 'dist'), { recursive: true })
        mkdirSync(resolve(destDir, 'modules'), { recursive: true })

        // Copy required files
        const filesToCopy = [
          'script.js',
          'helpers.js',
          'styles.css',
          'mobile-styles.css',
          'loading-styles.css',
          'sw.js',
          'sw-register.js',
          'dist/bundle.min.js',
          'dist/bundle.min.js.map',
          'dist/modules.min.js',
          'dist/modules.min.js.map',
          'dist/styles.min.css'
        ]

        filesToCopy.forEach(file => {
          try {
            const src = resolve(srcDir, file)
            const dest = resolve(destDir, file)
            copyFileSync(src, dest)
            console.log(`Copied: ${file}`)
          } catch (err) {
            console.warn(`Could not copy ${file}:`, err.message)
          }
        })

        // Copy modules folder
        const modulesFiles = ['cache.js', 'formatters.js', 'loading.js', 'validators.js']
        modulesFiles.forEach(file => {
          try {
            const src = resolve(srcDir, 'modules', file)
            const dest = resolve(destDir, 'modules', file)
            copyFileSync(src, dest)
            console.log(`Copied: modules/${file}`)
          } catch (err) {
            console.warn(`Could not copy modules/${file}:`, err.message)
          }
        })
      }
    }
  ],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  }
})
