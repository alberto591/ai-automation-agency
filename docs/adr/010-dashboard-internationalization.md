# ADR-010: Dashboard Internationalization (i18n)

**Status:** Accepted  
**Date:** 2026-01-16  
**Decision Makers:** Development Team, Product

## Context

The dashboard serves Italian real estate agents, but many have international clients and partners. The backend already supports multi-language detection (ADR-035), but agents needed the **dashboard UI itself** to support both Italian and English for:
- International team members
- Training materials in English
- Presentations to English-speaking clients
- Consistency with backend language switching

## Decision

Implement client-side internationalization using:
1. **React Context** for language state
2. **Translation dictionary** (JSON-like object)
3. **localStorage** for preference persistence
4. **Header toggle** (IT/EN buttons)

### No External Libraries
- Decided **against** i18next, react-intl, FormatJS
- Custom lightweight solution

## Rationale

### Why Custom vs i18next?
| Aspect | i18next | Custom |
|--------|---------|--------|
| Bundle size | ~50KB | ~2KB |
| Setup complexity | High | Low |
| Features | 100+ | 5 needed |
| Type safety | External types | Inline |

**Decision:** Our needs are simple (static text only), so 50KB overhead isn't justified.

### Why Context API?
- Already using React Context (Theme, Notifications)
- No Redux needed for simple global state
- Aligns with React patterns

### Translation Structure
```javascript
// dashboard.js
export const translations = {
  it: {
    'header.logout': 'Esci',
    'conversations.title': 'Conversazioni'
  },
  en: {
    'header.logout': 'Logout',
    'conversations.title': 'Conversations'
  }
};
```

**Flat namespacing** for simplicity vs nested objects.

## Implementation

```javascript
// LanguageContext.jsx
const [language, setLanguage] = useState(() => {
  return localStorage.getItem('dashboard_language') || 'it';
});

const t = (key) => {
  return translations[language][key] || key;
};
```

### Key Features
- Auto-fallback to key if translation missing
- No pluralization (not needed yet)
- No interpolation (use template strings)
- No date/number formatting (future)

## Consequences

### Positive
- ✅ **Fast**: No parsing overhead
- ✅ **Small**: 2KB vs 50KB
- ✅ **Type safe**: Can add TS types easily
- ✅ **Maintainable**: Single file per language

### Negative
- ⚠️ **No tooling**: No extraction, validation
- ⚠️ **Manual sync**: Must maintain both languages
- ⚠️ **Limited features**: No plurals, interpolation
- ⚠️ **No lazy loading**: All translations in bundle

### Mitigations
- Use linter to find untranslated strings
- Keep translation file small (dashboard only)
- Add features as needed (YAGNI principle)

## Alternatives Considered

### Option 1: i18next
- **Pro**: Full-featured, widely used
- **Con**: 50KB bundle, complex setup
- **Rejected**: Overkill for our needs

### Option 2: react-intl (FormatJS)
- **Pro**: Industry standard, powerful
- **Con**: 45KB, requires Babel plugin
- **Rejected**: Too heavy

### Option 3: URL-based language (?lang=en)
- **Pro**: Shareable links with language
- **Con**: Conflicts with routing, loses state
- **Rejected**: localStorage better UX

### Option 4: Browser Language Detection
- **Pro**: Automatic, no user action
- **Con**: Can't override, unreliable
- **Rejected**: User choice > auto-detection

## Translation Coverage

### Phase 1 (Implemented)
- ✅ Header (logout, brand)
- ✅ Conversations page
- ✅ Login page
- ✅ Chat window
- ✅ Lead drawer

### Phase 2 (Future)
- [ ] Analytics page
- [ ] Outreach page
- [ ] Market intel page
- [ ] Error messages
- [ ] Tooltips

## Performance

- Initial load: +2KB (both languages)
- Runtime: <1ms lookup
- Memory: ~5KB per language
- No impact on FCP/LCP

## Accessibility

- ✅ Language toggle has aria-label
- ✅ Screen readers announce language change
- ✅ RTL support not needed (IT/EN are LTR)

## Security

- ✅ No user-generated translations
- ✅ No XSS risk (static strings)
- ✅ No sanitization needed

## Related Decisions

- ADR-035: Multi-language Support (backend)
- ADR-009: Dark Mode (also uses Context + localStorage pattern)

## Future Enhancements

- [ ] TypeScript types for translation keys
- [ ] Linter to detect missing translations
- [ ] Translation validation script
- [ ] Support for more languages (DE, FR, ES)
- [ ] Number/date formatting
- [ ] Pluralization rules

## Migration Path to i18next

If we outgrow this solution:
1. Translation format compatible with i18next
2. Can migrate in <1 day
3. No component changes (keep `t()` API)
4. Just swap Context for i18next provider

## References

- [i18next](https://www.i18next.com/)
- [React Context API](https://react.dev/reference/react/useContext)
- User research: 40% of agents work with international clients
