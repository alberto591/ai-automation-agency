import { renderHook, waitFor } from '@testing-library/react';
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
import { useLeads } from '../hooks/useLeads';
import { supabase } from '../lib/supabase';

describe('useLeads', () => {
    let mockSelect, mockNeq, mockOrder;
    let mockChannel, mockOn, mockSubscribe;

    beforeEach(() => {
        vi.clearAllMocks();

        // Mock query chain
        mockOrder = vi.fn().mockResolvedValue({
            data: [
                {
                    id: 1,
                    customer_phone: '+393401234567',
                    customer_name: 'Test Lead',
                    status: 'active',
                    updated_at: new Date().toISOString(),
                    created_at: new Date().toISOString(),
                    messages: [
                        {
                            id: 1,
                            content: 'Hello',
                            created_at: new Date().toISOString(),
                            role: 'user'
                        }
                    ]
                }
            ],
            error: null
        });

        mockNeq = vi.fn().mockReturnValue({ order: mockOrder });
        mockSelect = vi.fn().mockReturnValue({ neq: mockNeq });
        supabase.from.mockReturnValue({ select: mockSelect });

        // Mock realtime subscription
        mockSubscribe = vi.fn();
        mockOn = vi.fn().mockReturnValue({ subscribe: mockSubscribe });
        mockChannel = vi.fn().mockReturnValue({ on: mockOn });
        supabase.channel.mockImplementation(mockChannel);
    });

    it('fetches leads on mount', async () => {
        const { result } = renderHook(() => useLeads());

        expect(result.current.loading).toBe(true);

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(supabase.from).toHaveBeenCalledWith('leads');
        expect(mockSelect).toHaveBeenCalledWith('*, messages(*)');
        expect(result.current.leads).toHaveLength(1);
        expect(result.current.leads[0].name).toBe('Test Lead');
    });

    it('subscribes to realtime updates', async () => {
        renderHook(() => useLeads());

        await waitFor(() => {
            expect(supabase.channel).toHaveBeenCalledWith('public:leads');
        });

        expect(mockOn).toHaveBeenCalledWith(
            'postgres_changes',
            expect.objectContaining({
                event: '*',
                schema: 'public',
                table: 'leads'
            }),
            expect.any(Function)
        );

        expect(mockSubscribe).toHaveBeenCalled();
    });

    it('formats lead data correctly', async () => {
        const { result } = renderHook(() => useLeads());

        await waitFor(() => {
            expect(result.current.leads).toHaveLength(1);
        });

        const lead = result.current.leads[0];
        expect(lead).toHaveProperty('id');
        expect(lead).toHaveProperty('phone');
        expect(lead).toHaveProperty('name');
        expect(lead).toHaveProperty('lastMsg');
        expect(lead).toHaveProperty('time');
        expect(lead).toHaveProperty('status');
        expect(lead.lastMsg).toBe('Hello');
    });

    it('handles fetch errors gracefully', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

        mockOrder.mockResolvedValue({
            data: null,
            error: new Error('Database error')
        });

        const { result } = renderHook(() => useLeads());

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        // Should not crash, should log error
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching leads:', expect.any(Error));

        consoleSpy.mockRestore();
    });

    it('uses fallback message text when no messages exist', async () => {
        mockOrder.mockResolvedValue({
            data: [
                {
                    id: 2,
                    customer_phone: '+393409999999',
                    customer_name: 'No Messages Lead',
                    status: 'new',
                    updated_at: new Date().toISOString(),
                    created_at: new Date().toISOString(),
                    messages: []
                }
            ],
            error: null
        });

        const { result } = renderHook(() => useLeads());

        await waitFor(() => {
            expect(result.current.leads).toHaveLength(1);
        });

        expect(result.current.leads[0].lastMsg).toBe('Nuova conversazione');
    });
});
