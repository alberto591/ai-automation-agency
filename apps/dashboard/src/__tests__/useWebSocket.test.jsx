import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useWebSocket } from '../hooks/useWebSocket';

// Mock WebSocket
class MockWebSocket {
    constructor(url) {
        this.url = url;
        this.readyState = MockWebSocket.CONNECTING;
        MockWebSocket.instance = this;

        // Simulate connection after a tick
        setTimeout(() => {
            this.readyState = MockWebSocket.OPEN;
            if (this.onopen) this.onopen({ type: 'open' });
        }, 0);
    }

    send = vi.fn();
    close = vi.fn(() => {
        this.readyState = MockWebSocket.CLOSED;
        if (this.onclose) this.onclose({ code: 1000, reason: 'Normal closure' });
    });

    // Static to access from tests
    static instance = null;
    static CONNECTING = 0;
    static OPEN = 1;
    static CLOSING = 2;
    static CLOSED = 3;
}

global.WebSocket = MockWebSocket;

describe('useWebSocket', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        MockWebSocket.instance = null;
    });

    afterEach(() => {
        vi.clearAllMocks();
        vi.useRealTimers();
    });

    it('connects to the provided URL on mount', async () => {
        const url = 'ws://localhost:1234';
        renderHook(() => useWebSocket(url));

        expect(MockWebSocket.instance).not.toBeNull();
        expect(MockWebSocket.instance.url).toBe(url);
    });

    it('updates isConnected state when opened', async () => {
        const { result } = renderHook(() => useWebSocket('ws://localhost:1234'));

        expect(result.current.isConnected).toBe(false);

        await act(async () => {
            vi.runAllTimers();
        });

        expect(result.current.isConnected).toBe(true);
    });

    it('calls onMessage when a message is received', async () => {
        const onMessage = vi.fn();
        renderHook(() => useWebSocket('ws://localhost:1234', { onMessage }));

        await act(async () => {
            vi.runAllTimers();
        });

        const message = { type: 'test', content: 'hello' };
        await act(async () => {
            MockWebSocket.instance.onmessage({ data: JSON.stringify(message) });
        });

        expect(onMessage).toHaveBeenCalledWith(message);
    });

    it('attempts reconnection on close if not manually disconnected', async () => {
        const { result } = renderHook(() => useWebSocket('ws://localhost:1234', { reconnectInterval: 1000 }));

        await act(async () => {
            vi.runAllTimers();
        });

        expect(result.current.isConnected).toBe(true);

        const firstInstance = MockWebSocket.instance;

        await act(async () => {
            // Simulate abnormal closure
            firstInstance.onclose({ code: 1006, reason: 'Abnormal' });
        });

        expect(result.current.isConnected).toBe(false);

        // Fast-forward to reconnect interval
        await act(async () => {
            vi.advanceTimersByTime(1000);
        });

        expect(MockWebSocket.instance).not.toBe(firstInstance);
    });

    it('does not reconnect after manual disconnect', async () => {
        const { result } = renderHook(() => useWebSocket('ws://localhost:1234'));

        await act(async () => {
            vi.runAllTimers();
        });

        const firstInstance = MockWebSocket.instance;

        await act(async () => {
            result.current.disconnect();
        });

        expect(result.current.isConnected).toBe(false);

        // Wait longer than reconnect interval
        await act(async () => {
            vi.advanceTimersByTime(5000);
        });

        // Should not have created a new instance
        expect(MockWebSocket.instance).toBe(firstInstance);
    });

    it('can send messages when connected', async () => {
        const { result } = renderHook(() => useWebSocket('ws://localhost:1234'));

        await act(async () => {
            vi.runAllTimers();
        });

        const message = { type: 'subscribe', room: 'all' };

        act(() => {
            result.current.sendMessage(message);
        });

        expect(MockWebSocket.instance.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('warns when trying to send messages while disconnected', async () => {
        const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });
        const { result } = renderHook(() => useWebSocket('ws://localhost:1234'));

        // Don't wait for connection
        act(() => {
            result.current.sendMessage({ type: 'test' });
        });

        expect(consoleSpy).toHaveBeenCalledWith('[WebSocket] Cannot send message, not connected');

        consoleSpy.mockRestore();
    });

    it('handles malformed JSON gracefully', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        const onMessage = vi.fn();

        renderHook(() => useWebSocket('ws://localhost:1234', { onMessage }));

        await act(async () => {
            vi.runAllTimers();
        });

        await act(async () => {
            MockWebSocket.instance.onmessage({ data: 'not valid json {' });
        });

        expect(onMessage).not.toHaveBeenCalled();
        expect(consoleSpy).toHaveBeenCalledWith('[WebSocket] Failed to parse message:', expect.any(Error));

        consoleSpy.mockRestore();
    });
});
