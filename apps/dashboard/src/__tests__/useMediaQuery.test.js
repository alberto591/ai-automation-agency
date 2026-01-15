/**
 * Tests for useMediaQuery hook
 * 
 * These tests verify the responsive breakpoint detection:
 * - Media query matching
 * - Window resize handling
 * - Mobile/tablet/desktop helpers
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useMediaQuery, useIsMobile, useIsTablet, useIsDesktop } from '../hooks/useMediaQuery';

describe('useMediaQuery', () => {
    let matchMediaMock;

    beforeEach(() => {
        // Mock window.matchMedia
        matchMediaMock = vi.fn();
        window.matchMedia = matchMediaMock;
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it('should return true when media query matches', () => {
        const listeners = [];
        matchMediaMock.mockReturnValue({
            matches: true,
            addEventListener: (event, listener) => listeners.push(listener),
            removeEventListener: (event, listener) => {
                const index = listeners.indexOf(listener);
                if (index > -1) listeners.splice(index, 1);
            }
        });

        const { result } = renderHook(() => useMediaQuery('(max-width: 768px)'));
        expect(result.current).toBe(true);
    });

    it('should return false when media query does not match', () => {
        const listeners = [];
        matchMediaMock.mockReturnValue({
            matches: false,
            addEventListener: (event, listener) => listeners.push(listener),
            removeEventListener: (event, listener) => {
                const index = listeners.indexOf(listener);
                if (index > -1) listeners.splice(index, 1);
            }
        });

        const { result } = renderHook(() => useMediaQuery('(max-width: 768px)'));
        expect(result.current).toBe(false);
    });

    it('should update when media query changes', () => {
        const listeners = [];
        const mediaQueryList = {
            matches: false,
            addEventListener: (event, listener) => listeners.push(listener),
            removeEventListener: (event, listener) => {
                const index = listeners.indexOf(listener);
                if (index > -1) listeners.splice(index, 1);
            }
        };

        matchMediaMock.mockReturnValue(mediaQueryList);

        const { result, rerender } = renderHook(() => useMediaQuery('(max-width: 768px)'));
        expect(result.current).toBe(false);

        // Simulate media query change
        mediaQueryList.matches = true;
        listeners.forEach(listener => listener({ matches: true }));
        rerender();

        expect(result.current).toBe(true);
    });

    it('should handle legacy browsers without addEventListener', () => {
        const listeners = [];
        matchMediaMock.mockReturnValue({
            matches: true,
            addListener: (listener) => listeners.push(listener),
            removeListener: (listener) => {
                const index = listeners.indexOf(listener);
                if (index > -1) listeners.splice(index, 1);
            }
        });

        const { result } = renderHook(() => useMediaQuery('(max-width: 768px)'));
        expect(result.current).toBe(true);
    });

    it('should clean up listeners on unmount', () => {
        const listeners = [];
        const removeEventListener = vi.fn((event, listener) => {
            const index = listeners.indexOf(listener);
            if (index > -1) listeners.splice(index, 1);
        });

        matchMediaMock.mockReturnValue({
            matches: false,
            addEventListener: (event, listener) => listeners.push(listener),
            removeEventListener
        });

        const { unmount } = renderHook(() => useMediaQuery('(max-width: 768px)'));

        expect(listeners.length).toBe(1);
        unmount();
        expect(removeEventListener).toHaveBeenCalled();
    });
});

describe('useIsMobile', () => {
    it('should return true for mobile viewport', () => {
        window.matchMedia = vi.fn().mockReturnValue({
            matches: true,
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        });

        const { result } = renderHook(() => useIsMobile());
        expect(result.current).toBe(true);
        expect(window.matchMedia).toHaveBeenCalledWith('(max-width: 767px)');
    });

    it('should return false for desktop viewport', () => {
        window.matchMedia = vi.fn().mockReturnValue({
            matches: false,
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        });

        const { result } = renderHook(() => useIsMobile());
        expect(result.current).toBe(false);
    });
});

describe('useIsTablet', () => {
    it('should return true for tablet viewport', () => {
        window.matchMedia = vi.fn().mockReturnValue({
            matches: true,
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        });

        const { result } = renderHook(() => useIsTablet());
        expect(result.current).toBe(true);
        expect(window.matchMedia).toHaveBeenCalledWith('(min-width: 768px) and (max-width: 1023px)');
    });
});

describe('useIsDesktop', () => {
    it('should return true for desktop viewport', () => {
        window.matchMedia = vi.fn().mockReturnValue({
            matches: true,
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        });

        const { result } = renderHook(() => useIsDesktop());
        expect(result.current).toBe(true);
        expect(window.matchMedia).toHaveBeenCalledWith('(min-width: 1024px)');
    });
});
