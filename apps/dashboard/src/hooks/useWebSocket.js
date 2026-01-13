import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Custom hook for managing WebSocket connection to the backend
 * @param url - WebSocket URL (e.g., ws://localhost:8000/ws/conversations)
 * @param options - Configuration options
 * @returns WebSocket state and functions
 */
export function useWebSocket(url, options = {}) {
    const {
        onMessage = () => { },
        onOpen = () => { },
        onClose = () => { },
        onError = () => { },
        reconnectInterval = 3000,
        maxReconnectAttempts = 5,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const [reconnectCount, setReconnectCount] = useState(0);

    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const shouldReconnectRef = useRef(true);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return; // Already connected
        }

        try {
            console.log('[WebSocket] Connecting to:', url);
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = (event) => {
                console.log('[WebSocket] Connected');
                setIsConnected(true);
                setReconnectCount(0);
                onOpen(event);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[WebSocket] Message received:', data);
                    setLastMessage(data);
                    onMessage(data);
                } catch (error) {
                    console.error('[WebSocket] Failed to parse message:', error);
                }
            };

            ws.onclose = (event) => {
                console.log('[WebSocket] Disconnected:', event.code, event.reason);
                setIsConnected(false);
                wsRef.current = null;
                onClose(event);

                // Attempt reconnection if not manually closed
                if (shouldReconnectRef.current && reconnectCount < maxReconnectAttempts) {
                    const nextAttempt = reconnectCount + 1;
                    console.log(`[WebSocket] Reconnecting... (attempt ${nextAttempt}/${maxReconnectAttempts})`);
                    setReconnectCount(nextAttempt);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                }
            };

            ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                onError(error);
            };
        } catch (error) {
            console.error('[WebSocket] Connection failed:', error);
        }
    }, [url, onMessage, onOpen, onClose, onError, reconnectInterval, maxReconnectAttempts, reconnectCount]);

    const disconnect = useCallback(() => {
        shouldReconnectRef.current = false;
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    }, []);

    const sendMessage = useCallback((message) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            const payload = typeof message === 'string' ? message : JSON.stringify(message);
            wsRef.current.send(payload);
            console.log('[WebSocket] Sent:', payload);
        } else {
            console.warn('[WebSocket] Cannot send message, not connected');
        }
    }, []);

    const subscribe = useCallback((room) => {
        sendMessage({ type: 'subscribe', room });
    }, [sendMessage]);

    const unsubscribe = useCallback((room) => {
        sendMessage({ type: 'unsubscribe', room });
    }, [sendMessage]);

    // Auto-connect on mount
    useEffect(() => {
        shouldReconnectRef.current = true;
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    // Heartbeat to keep connection alive
    useEffect(() => {
        if (!isConnected) return;

        const pingInterval = setInterval(() => {
            sendMessage({ type: 'ping' });
        }, 30000); // Ping every 30 seconds

        return () => clearInterval(pingInterval);
    }, [isConnected, sendMessage]);

    return {
        isConnected,
        lastMessage,
        sendMessage,
        subscribe,
        unsubscribe,
        reconnect: connect,
        disconnect,
    };
}
