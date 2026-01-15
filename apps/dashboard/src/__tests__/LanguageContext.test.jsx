/**
 * Tests for LanguageContext
 * 
 * These tests verify the language toggle functionality:
 * - Context provider initialization
 * - Translation function (t())
 * - Language switching
 * - localStorage persistence
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { LanguageProvider, useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/dashboard';

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

// Test component that uses the language context
function TestComponent() {
    const { language, setLanguage, t } = useLanguage();

    return (
        <div>
            <div data-testid="current-language">{language}</div>
            <div data-testid="translated-text">{t('header.logout')}</div>
            <button onClick={() => setLanguage('it')} data-testid="btn-italian">IT</button>
            <button onClick={() => setLanguage('en')} data-testid="btn-english">EN</button>
        </div>
    );
}

describe('LanguageContext', () => {
    beforeEach(() => {
        localStorageMock.clear();
    });

    it('should initialize with Italian as default language', () => {
        render(
            <LanguageProvider>
                <TestComponent />
            </LanguageProvider>
        );

        expect(screen.getByTestId('current-language').textContent).toBe('it');
        expect(screen.getByTestId('translated-text').textContent).toBe('Esci');
    });

    it('should switch language when setLanguage is called', () => {
        render(
            <LanguageProvider>
                <TestComponent />
            </LanguageProvider>
        );

        const englishButton = screen.getByTestId('btn-english');

        act(() => {
            englishButton.click();
        });

        expect(screen.getByTestId('current-language').textContent).toBe('en');
        expect(screen.getByTestId('translated-text').textContent).toBe('Logout');
    });

    it('should persist language preference to localStorage', () => {
        render(
            <LanguageProvider>
                <TestComponent />
            </LanguageProvider>
        );

        const englishButton = screen.getByTestId('btn-english');

        act(() => {
            englishButton.click();
        });

        expect(localStorageMock.getItem('dashboard_language')).toBe('en');
    });

    it('should load language preference from localStorage on mount', () => {
        localStorageMock.setItem('dashboard_language', 'en');

        render(
            <LanguageProvider>
                <TestComponent />
            </LanguageProvider>
        );

        expect(screen.getByTestId('current-language').textContent).toBe('en');
        expect(screen.getByTestId('translated-text').textContent).toBe('Logout');
    });

    it('should handle translation keys that do not exist', () => {
        render(
            <LanguageProvider>
                <TestComponent />
            </LanguageProvider>
        );

        const { t } = useLanguage();
        expect(t('nonexistent.key')).toBe('nonexistent.key');
    });

    it('should translate all header keys correctly', () => {
        const headerKeys = ['header.logout', 'header.brand', 'header.subtitle'];

        headerKeys.forEach(key => {
            expect(translations.it[key]).toBeDefined();
            expect(translations.en[key]).toBeDefined();
            expect(translations.it[key]).not.toBe(translations.en[key] || key === 'header.brand'); // Brand is same in both
        });
    });

    it('should translate all conversation keys correctly', () => {
        const conversationKeys = [
            'conversations.title',
            'conversations.connected',
            'conversations.disconnected',
            'conversations.selectChat'
        ];

        conversationKeys.forEach(key => {
            expect(translations.it[key]).toBeDefined();
            expect(translations.en[key]).toBeDefined();
        });
    });
});
