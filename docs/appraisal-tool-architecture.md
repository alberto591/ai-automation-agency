# 🏗️ AI Appraisal Tool Architecture

The appraisal tool is designed for high performance, visual impact (glassmorphism), and full bilingual support. It is a standalone product for property acquisition.

## 🌍 Translation System

The page uses a custom `data-translate` attribute system to toggle between Italian (IT) and English (EN) without page reloads.

### How it Works
1. **HTML Hooks**: Elements are tagged with `data-translate="key-name"`.
2. **JavaScript Dictionary**: The `translations` object in `script.js` contains the content for both IT and EN.
3. **Switch Logic**: The `switchLanguage(lang)` function iterates through all tagged elements and updates their `textContent` or `placeholder`.

### Adding New Content
To add a new translatable element:
1. Add the hook: `<p data-translate="my-new-text">Original text</p>`.
2. Update [script.js](file:///Users/lycanbeats/Desktop/agenzia-ai/landing_page/script.js):
   - Add the key to the `it` object.
   - Add the key to the `en` object.

## ⚡ Performance & UI
- **Pure CSS/JS**: No heavy frameworks used for the frontend to ensure instant loading.
- **Scroll Animations**: Uses `IntersectionObserver` for smooth element reveals.
- **Form Handling**: Integrated with the FastAPI backend and provides an instant success state with a link to Calendly.
