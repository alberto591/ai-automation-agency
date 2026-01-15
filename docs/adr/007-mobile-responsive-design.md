# ADR-007: Mobile-First Responsive Design

**Status:** Accepted  
**Date:** 2026-01-16  
**Decision Makers:** Development Team

## Context

The dashboard was initially designed for desktop use only. With real estate agents increasingly working on-the-go, mobile support became critical for timely lead response and deal management.

## Decision

Implement a mobile-first responsive design using:
1. **Tailwind CSS responsive utilities** (`md:`, `lg:` prefixes)
2. **Custom useMediaQuery hook** for JavaScript-controlled responsiveness
3. **Stack layout pattern** on mobile (conversation list OR chat, not both)
4. **Full-screen modals** on mobile (LeadDrawer)

## Rationale

### Why Stack Layout?
- **Screen real estate**: Mobile screens (375px-428px) can't fit sidebar + chat
- **Familiar pattern**: WhatsApp, Telegram use this pattern
- **Better UX**: Users focus on one thing at a time

### Why Custom Hook?
- **Conditional rendering**: Show/hide components based on viewport
- **JavaScript logic**: Not everything can be done with CSS
- **Type safety**: Better than window.matchMedia directly

### Breakpoints Chosen
- **Mobile**: <768px
- **Desktop**: ≥768px
- Rationale: Standard iPad Mini breakpoint, matches Tailwind defaults

## Implementation

```javascript
// useMediaQuery.js
export function useIsMobile() {
  return useMediaQuery('(max-width: 767px)');
}

// ConversationsPage.jsx
const showList = !isMobile || !selectedPhone;
const showChat = !isMobile || selectedPhone;
```

### Key Changes
1. **ConversationsPage**: Conditional rendering with `showList`/`showChat`
2. **ChatWindow**: Added `onBack` prop for mobile navigation
3. **LeadDrawer**: Changed from `absolute` to `fixed` positioning for full-screen
4. **Touch targets**: Minimum 44px for better mobile UX

## Consequences

### Positive
- ✅ Agents can manage leads from phones
- ✅ Faster response times (mobile notifications)
- ✅ Familiar UX pattern (WhatsApp-style)
- ✅ No horizontal scrolling

### Negative
- ⚠️ Can't see list and chat simultaneously on mobile
- ⚠️ Extra back button navigation required
- ⚠️ Increased code complexity (conditional rendering)

### Neutral
- 📝 Need to maintain two layout patterns
- 📝 More test coverage required

## Alternatives Considered

### Option 1: Collapsible Sidebar
- **Pro**: Can see both list and chat
- **Con**: Very cramped on small screens
- **Rejected**: Poor UX on phones

### Option 2: Separate Mobile App
- **Pro**: Native performance and UX
- **Con**: High development cost
- **Rejected**: PWA approach sufficient for now

### Option 3: Desktop Only
- **Pro**: Simplest implementation
- **Con**: Agents can't work remotely
- **Rejected**: Business requirement for mobile

## Compliance

- ✅ **WCAG 2.1 AA**: Touch targets ≥44px
- ✅ **Mobile Performance**: No layout shifts, fast loading
- ✅ **Cross-browser**: Works on iOS Safari, Chrome, Firefox

## Related Decisions

- ADR-001: Tailwind CSS for styling
- ADR-008: Real-time Notifications (mobile alerts)
- ADR-009: Dark Mode (mobile-friendly)

## References

- [Tailwind Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Mobile UX Patterns](https://mobbin.com)
- User feedback: "Need mobile access for weekend showings"
