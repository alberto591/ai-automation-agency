import { useState, useEffect } from 'react';

/**
 * Custom hook to detect media query breakpoints
 * @param {string} query - CSS media query (e.g., '(max-width: 768px)')
 * @returns {boolean} - Whether the media query matches
 */
export function useMediaQuery(query) {
    const [matches, setMatches] = useState(false);

    useEffect(() => {
        const media = window.matchMedia(query);

        // Set initial value
        setMatches(media.matches);

        // Create event listener
        const listener = (e) => setMatches(e.matches);

        // Add listener (use deprecated method for broader compatibility)
        if (media.addEventListener) {
            media.addEventListener('change', listener);
        } else {
            media.addListener(listener);
        }

        // Cleanup
        return () => {
            if (media.removeEventListener) {
                media.removeEventListener('change', listener);
            } else {
                media.removeListener(listener);
            }
        };
    }, [query]);

    return matches;
}

/**
 * Predefined breakpoint hooks for common screen sizes
 */
export function useIsMobile() {
    return useMediaQuery('(max-width: 767px)');
}

export function useIsTablet() {
    return useMediaQuery('(min-width: 768px) and (max-width: 1023px)');
}

export function useIsDesktop() {
    return useMediaQuery('(min-width: 1024px)');
}
