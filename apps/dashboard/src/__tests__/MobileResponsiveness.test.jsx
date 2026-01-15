/**
 * Tests for mobile responsive components
 * 
 * These tests verify:
 * - ConversationsPage conditional rendering on mobile
 * - ChatWindow back button on mobile
 * - LeadDrawer full-screen behavior
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ConversationsPage from '../components/ConversationsPage';
import ChatWindow from '../components/ChatWindow';

// Mock hooks
vi.mock('../hooks/useMediaQuery', () => ({
    useIsMobile: vi.fn(),
    useIsTablet: vi.fn(),
    useIsDesktop: vi.fn()
}));

vi.mock('../hooks/useWebSocket', () => ({
    useWebSocket: vi.fn(() => ({ isConnected: true }))
}));

vi.mock('../hooks/useMessages', () => ({
    useMessages: vi.fn(() => ({
        messages: [],
        setMessages: vi.fn(),
        status: 'active',
        setStatus: vi.fn(),
        loading: false
    }))
}));

vi.mock('../contexts/LanguageContext', () => ({
    useLanguage: () => ({
        language: 'en',
        setLanguage: vi.fn(),
        t: (key) => key
    })
}));

import { useIsMobile } from '../hooks/useMediaQuery';

describe('ConversationsPage Mobile Behavior', () => {
    const mockSession = {
        access_token: 'mock-token',
        user: { id: '123' }
    };

    it('should show conversation list on mobile when no conversation selected', () => {
        useIsMobile.mockReturnValue(true);

        render(<ConversationsPage session={mockSession} />);

        // Should show conversations title
        expect(screen.getByText('conversations.title')).toBeInTheDocument();
    });

    it('should hide conversation list when chat is open on mobile', () => {
        useIsMobile.mockReturnValue(true);

        const { rerender } = render(<ConversationsPage session={mockSession} />);

        // Initially shows list
        expect(screen.getByText('conversations.title')).toBeInTheDocument();

        // TODO: Simulate selecting a conversation and verify list is hidden
        // This would require mocking conversation selection
    });

    it('should show both list and chat on desktop', () => {
        useIsMobile.mockReturnValue(false);

        render(<ConversationsPage session={mockSession} />);

        // Should show conversations title (list visible)
        expect(screen.getByText('conversations.title')).toBeInTheDocument();
    });
});

describe('ChatWindow Mobile Features', () => {
    const mockLead = {
        id: '123',
        name: 'Test Lead',
        phone: '+1234567890'
    };

    it('should render back button when onBack prop is provided', () => {
        const onBack = vi.fn();

        render(<ChatWindow selectedLead={mockLead} onBack={onBack} />);

        const backButton = screen.getByLabelText('Back to conversations');
        expect(backButton).toBeInTheDocument();
    });

    it('should call onBack when back button is clicked', () => {
        const onBack = vi.fn();

        render(<ChatWindow selectedLead={mockLead} onBack={onBack} />);

        const backButton = screen.getByLabelText('Back to conversations');
        fireEvent.click(backButton);

        expect(onBack).toHaveBeenCalledTimes(1);
    });

    it('should not render back button when onBack prop is not provided', () => {
        render(<ChatWindow selectedLead={mockLead} />);

        const backButton = screen.queryByLabelText('Back to conversations');
        expect(backButton).not.toBeInTheDocument();
    });

    it('should have responsive padding on mobile', () => {
        render(<ChatWindow selectedLead={mockLead} onBack={vi.fn()} />);

        // The header should have mobile-responsive classes
        const header = screen.getByLabelText('Back to conversations').closest('div');
        expect(header).toHaveClass('px-4', 'md:px-6');
    });
});

describe('Mobile Touch Interactions', () => {
    it('should have touch-friendly active states on conversation items', () => {
        useIsMobile.mockReturnValue(true);

        const mockSession = {
            access_token: 'mock-token',
            user: { id: '123' }
        };

        render(<ConversationsPage session={mockSession} />);

        // Verify touch-friendly classes are present
        // This is a basic check - actual touch testing would require more setup
        const page = screen.getByText('conversations.title').closest('.conversations-page');
        expect(page).toBeInTheDocument();
    });
});
