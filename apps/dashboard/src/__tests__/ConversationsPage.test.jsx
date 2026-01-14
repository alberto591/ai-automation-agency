import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ConversationsPage from '../components/ConversationsPage';

// Mock our custom hook
const mockUseWebSocket = vi.fn();
vi.mock('../hooks/useWebSocket', () => ({
    useWebSocket: (...args) => mockUseWebSocket(...args)
}));

// Mock fetch for initial data
global.fetch = vi.fn();

describe('ConversationsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockUseWebSocket.mockReturnValue({
            isConnected: true,
            lastMessage: null,
            sendMessage: vi.fn(),
            subscribe: vi.fn(),
            unsubscribe: vi.fn(),
        });

        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => [
                { id: 1, phone: '+393400000000', name: 'Existing Lead', last_message: 'Hi', updated_at: new Date().toISOString() }
            ]
        });
    });

    it('renders "Connected" status when WebSocket is connected', async () => {
        await act(async () => {
            render(<ConversationsPage />);
        });

        expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    it('updates sidebar when an incoming message is received via WebSocket', async () => {
        let onMessageCallback;
        mockUseWebSocket.mockImplementation((url, options) => {
            onMessageCallback = options.onMessage;
            return { isConnected: true };
        });

        await act(async () => {
            render(<ConversationsPage />);
        });

        const newMessage = {
            type: 'message',
            phone: '+393401112223',
            lead_name: 'New Lead',
            message: {
                role: 'user',
                content: 'I am interested in a flat',
                timestamp: new Date().toISOString()
            }
        };

        await act(async () => {
            onMessageCallback(newMessage);
        });

        expect(screen.getByText('New Lead')).toBeInTheDocument();
        expect(screen.getByText('I am interested in a flat')).toBeInTheDocument();
    });

    it('shows messages in the main panel when a conversation is clicked', async () => {
        let onMessageCallback;
        mockUseWebSocket.mockImplementation((url, options) => {
            onMessageCallback = options.onMessage;
            return { isConnected: true };
        });

        await act(async () => {
            render(<ConversationsPage />);
        });

        const newMessage = {
            type: 'message',
            phone: '+393409998887',
            lead_name: 'Click Lead',
            message: {
                role: 'user',
                content: 'Hello World',
                timestamp: new Date().toISOString()
            }
        };

        await act(async () => {
            onMessageCallback(newMessage);
        });

        // Click the sidebar item
        fireEvent.click(screen.getByText('Click Lead'));

        // Check main panel
        expect(screen.getByText('Hello World', { selector: '.messages-panel *' })).toBeInTheDocument();
        expect(screen.getByText('+393409998887', { selector: '.messages-panel *' })).toBeInTheDocument();
    });
});
