import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Supabase BEFORE importing the hook
vi.mock('../lib/supabase', () => ({
    supabase: {
        from: vi.fn(),
        channel: vi.fn(),
        removeChannel: vi.fn(),
    }
}));

// Import after mock is set up
import { useMessages } from '../hooks/useMessages';
import { supabase } from '../lib/supabase';

describe('useMessages', () => {
    let mockSelect, mockEq, mockOrder, mockSingle;
    let mockChannel, mockOn, mockSubscribe;

    beforeEach(() => {
        vi.clearAllMocks();

        // Mock messages query
        mockOrder = vi.fn().mockResolvedValue({
            data: [
                {
                    id: 1,
                    lead_id: 123,
                    role: 'user',
                    content: 'Hello',
                    created_at: new Date().toISOString()
                },
                {
                    id: 2,
                    lead_id: 123,
                    role: 'assistant',
                    content: 'Hi there!',
                    created_at: new Date().toISOString()
                }
            ],
            error: null
        });

        mockEq = vi.fn().mockReturnValue({ order: mockOrder });
        mockSelect = vi.fn().mockReturnValue({ eq: mockEq });

        // For lead status query
        mockSingle = vi.fn().mockResolvedValue({
            data: { status: 'active' },
            error: null
        });

        supabase.from.mockImplementation((table) => {
            if (table === 'messages') {
                return { select: mockSelect };
            }
            if (table === 'leads') {
                return {
                    select: vi.fn().mockReturnValue({
                        eq: vi.fn().mockReturnValue({ single: mockSingle })
                    })
                };
            }
        });

        // Mock realtime subscription
        mockSubscribe = vi.fn();
        mockOn = vi.fn().mockReturnThis();
        mockChannel = vi.fn().mockReturnValue({
            on: mockOn,
            subscribe: mockSubscribe
        });
        supabase.channel.mockImplementation(mockChannel);
    });

    it('fetches messages and status on mount', async () => {
        const { result } = renderHook(() => useMessages(123));

        expect(result.current.loading).toBe(true);

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(supabase.from).toHaveBeenCalledWith('messages');
        expect(result.current.messages).toHaveLength(2);
        expect(result.current.status).toBe('active');
    });

    it('subscribes to message insert events', async () => {
        renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(supabase.channel).toHaveBeenCalledWith(
                'public:messages:lead_id=eq.123'
            );
        });

        expect(mockOn).toHaveBeenCalledWith(
            'postgres_changes',
            expect.objectContaining({
                event: 'INSERT',
                schema: 'public',
                table: 'messages',
                filter: 'lead_id=eq.123'
            }),
            expect.any(Function)
        );
    });

    it('subscribes to lead status updates', async () => {
        renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(supabase.channel).toHaveBeenCalledWith(
                'public:leads:id=eq.123'
            );
        });

        expect(mockOn).toHaveBeenCalledWith(
            'postgres_changes',
            expect.objectContaining({
                event: 'UPDATE',
                schema: 'public',
                table: 'leads',
                filter: 'id=eq.123'
            }),
            expect.any(Function)
        );
    });

    it('adds new messages via realtime subscription', async () => {
        let insertCallback;
        mockOn.mockImplementation((event, config, callback) => {
            if (config.event === 'INSERT') {
                insertCallback = callback;
            }
            return { on: mockOn, subscribe: mockSubscribe };
        });

        const { result } = renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(result.current.messages).toHaveLength(2);
        });

        // Simulate new message from realtime
        act(() => {
            insertCallback({
                new: {
                    id: 3,
                    lead_id: 123,
                    role: 'user',
                    content: 'New message',
                    created_at: new Date().toISOString()
                }
            });
        });

        expect(result.current.messages).toHaveLength(3);
        expect(result.current.messages[2].content).toBe('New message');
    });

    it('updates status via realtime subscription', async () => {
        let statusCallback;
        mockOn.mockImplementation((event, config, callback) => {
            if (config.table === 'leads') {
                statusCallback = callback;
            }
            return { on: mockOn, subscribe: mockSubscribe };
        });

        const { result } = renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(result.current.status).toBe('active');
        });

        // Simulate status change
        act(() => {
            statusCallback({
                new: {
                    id: 123,
                    status: 'human_mode'
                }
            });
        });

        expect(result.current.status).toBe('human_mode');
    });

    it('handles missing leadId gracefully', async () => {
        const { result } = renderHook(() => useMessages(null));

        expect(result.current.loading).toBe(false);
        expect(result.current.messages).toEqual([]);
    });

    it('handles fetch errors gracefully', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

        mockOrder.mockResolvedValue({
            data: null,
            error: new Error('Database error')
        });

        const { result } = renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(consoleSpy).toHaveBeenCalledWith('Error fetching messages:', expect.any(Error));

        consoleSpy.mockRestore();
    });

    it('exposes setMessages and setStatus for manual updates', async () => {
        const { result } = renderHook(() => useMessages(123));

        await waitFor(() => {
            expect(result.current.messages).toHaveLength(2);
        });

        act(() => {
            result.current.setMessages([{ id: 99, content: 'Manual' }]);
            result.current.setStatus('human_mode');
        });

        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0].id).toBe(99);
        expect(result.current.status).toBe('human_mode');
    });
});
