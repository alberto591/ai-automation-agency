/**
 * Tests for ThemeContext (Dark Mode)
 * 
 * These tests verify:
 * - Theme initialization
 * - Theme toggling
 * - localStorage persistence
 * - System preference detection
 * - HTML class application
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => { store[key] = value.toString(); },
        clear: () => { store = {}; },
        removeItem: (key) => { delete store[key]; }
    };
})();

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
});

// Mock matchMedia
const mockMatchMedia = (matches) => {
    return vi.fn().mockReturnValue({
        matches,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
    });
};

describe('ThemeContext', () => {
    let documentElement;

    beforeEach(() => {
        localStorageMock.clear();
        documentElement = window.document.documentElement;
        documentElement.classList.remove('dark');
        window.matchMedia = mockMatchMedia(false);
    });

    it('should initialize with light mode by default', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(false);
    });

    it('should initialize from localStorage if available', () => {
        localStorageMock.setItem('theme', 'dark');

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(true);
    });

    it('should initialize from system preference if no localStorage', () => {
        window.matchMedia = mockMatchMedia(true); // prefers dark

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(true);
    });

    it('should toggle theme', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(false);

        act(() => {
            result.current.toggleTheme();
        });

        expect(result.current.isDark).toBe(true);
    });

    it('should save theme to localStorage when toggled', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        act(() => {
            result.current.toggleTheme();
        });

        expect(localStorageMock.getItem('theme')).toBe('dark');

        act(() => {
            result.current.toggleTheme();
        });

        expect(localStorageMock.getItem('theme')).toBe('light');
    });

    it('should add dark class to html element when dark mode enabled', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        act(() => {
            result.current.toggleTheme();
        });

        expect(documentElement.classList.contains('dark')).toBe(true);
    });

    it('should remove dark class from html element when light mode enabled', () => {
        localStorageMock.setItem('theme', 'dark');

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(documentElement.classList.contains('dark')).toBe(true);

        act(() => {
            result.current.toggleTheme();
        });

        expect(documentElement.classList.contains('dark')).toBe(false);
    });

    it('should persist theme across multiple toggles', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        // Toggle 3 times
        act(() => {
            result.current.toggleTheme(); // dark
            result.current.toggleTheme(); // light
            result.current.toggleTheme(); // dark
        });

        expect(result.current.isDark).toBe(true);
        expect(localStorageMock.getItem('theme')).toBe('dark');
    });

    it('should prioritize localStorage over system preference', () => {
        window.matchMedia = mockMatchMedia(true); // System prefers dark
        localStorageMock.setItem('theme', 'light'); // User chose light

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(false);
    });

    it('should throw error when useTheme used outside provider', () => {
        // Suppress console.error for this test
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => { });

        expect(() => {
            renderHook(() => useTheme());
        }).toThrow('useTheme must be used within ThemeProvider');

        consoleError.mockRestore();
    });
});

describe('Theme HTML Class Management', () => {
    beforeEach(() => {
        localStorageMock.clear();
        document.documentElement.classList.remove('dark');
    });

    it('should not have dark class initially in light mode', () => {
        renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('should have dark class initially when localStorage has dark', () => {
        localStorageMock.setItem('theme', 'dark');

        renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
});

describe('Theme Context Edge Cases', () => {
    it('should handle undefined localStorage gracefully', () => {
        // Mock localStorage to return undefined
        localStorageMock.getItem = vi.fn(() => undefined);
        window.matchMedia = mockMatchMedia(false);

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        expect(result.current.isDark).toBe(false);
    });

    it('should handle invalid localStorage value', () => {
        localStorageMock.setItem('theme', 'invalid-value');

        const { result } = renderHook(() => useTheme(), {
            wrapper: ThemeProvider
        });

        // Should default to light mode for invalid values
        expect(result.current.isDark).toBe(false);
    });
});
