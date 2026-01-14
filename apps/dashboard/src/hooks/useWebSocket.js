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

    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectCountRef = useRef(0);
    const shouldReconnectRef = useRef(true);
    const urlRef = useRef(url);

    // Store latest callbacks in refs to avoid stale closures
    const callbacksRef = useRef({ onMessage, onOpen, onClose, onError });

    useEffect(() => {
        callbacksRef.current = { onMessage, onOpen, onClose, onError };
    }, [onMessage, onOpen, onClose, onError]);

    // Update URL ref when it changes
    useEffect(() => {
        urlRef.current = url;
    }, [url]);

    const connectRef = useRef(null);

    const connect = useCallback(() => {
        // Prevent multiple simultaneous connections
        if (wsRef.current?.readyState === WebSocket.OPEN ||
            wsRef.current?.readyState === WebSocket.CONNECTING) {
            return;
        }

        try {
            console.log('[WebSocket] Connecting to:', urlRef.current);
            const ws = new WebSocket(urlRef.current);
            wsRef.current = ws;

            ws.onopen = (event) => {
                console.log('[WebSocket] Connected');
                setIsConnected(true);
                reconnectCountRef.current = 0;
                callbacksRef.current.onOpen(event);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[WebSocket] Message received:', data);
                    setLastMessage(data);
                    callbacksRef.current.onMessage(data);
                } catch (error) {
                    console.error('[WebSocket] Failed to parse message:', error);
                }
            };

            ws.onclose = (event) => {
                console.log('[WebSocket] Disconnected:', event.code, event.reason);
                setIsConnected(false);
                wsRef.current = null;
                callbacksRef.current.onClose(event);

                // Attempt reconnection if not manually closed
                if (shouldReconnectRef.current && reconnectCountRef.current < maxReconnectAttempts) {
                    reconnectCountRef.current += 1;
                    console.log(`[WebSocket] Reconnecting... (attempt ${reconnectCountRef.current}/${maxReconnectAttempts})`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        if (connectRef.current) connectRef.current();
                    }, reconnectInterval);
                }
            };

            ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                callbacksRef.current.onError(error);
            };
        } catch (error) {
            console.error('[WebSocket] Connection failed:', error);
        }
    }, [reconnectInterval, maxReconnectAttempts]);

    // Store connect in ref
    useEffect(() => {
        connectRef.current = connect;
    }, [connect]);

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

    // Auto-connect on mount only
    useEffect(() => {
        shouldReconnectRef.current = true;
        reconnectCountRef.current = 0;
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]); // Auto-connect on mount and handle cleanup

    // Heartbeat to keep connection alive
    useEffect(() => {
        if (!isConnected) return;

        const pingInterval = setInterval(() => {
            sendMessage({ type: 'ping' });
        }, 30000);

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
