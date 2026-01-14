import { useState, useMemo, useRef, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

export default function ConversationsPage() {
    const [conversations, setConversations] = useState([]);
    const [selectedPhone, setSelectedPhone] = useState(null);
    // Store messages by phone number
    const messagesMapRef = useRef({});
    const [currentMessages, setCurrentMessages] = useState([]);

    // Memoize WebSocket URL to prevent reconnection loops
    const wsUrl = useMemo(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
        const baseUrl = apiUrl.replace(/^https?:\/\//, '');
        return `${wsProtocol}://${baseUrl}/ws/conversations`;
    }, []);

    const handleMessage = useCallback((data) => {
        console.log('📨 Received message:', data);

        if (data.type === 'message') {
            const phone = data.phone;

            // Store message in map
            if (!messagesMapRef.current[phone]) {
                messagesMapRef.current[phone] = [];
            }
            messagesMapRef.current[phone].push(data.message);

            // If this is the selected conversation, update displayed messages
            if (selectedPhone === phone) {
                setCurrentMessages((prev) => [...prev, data.message]);
            }

            // Update conversations list
            setConversations((prev) => {
                const existingIndex = prev.findIndex((conv) => conv.phone === phone);
                const updatedConv = {
                    phone: phone,
                    name: data.lead_name || 'Unknown',
                    lastMessage: data.message.content,
                    lastMessageTime: data.message.timestamp,
                    role: data.message.role,
                };

                if (existingIndex >= 0) {
                    const updated = [...prev];
                    updated.splice(existingIndex, 1);
                    return [updatedConv, ...updated];
                }
                return [updatedConv, ...prev];
            });
        }
    }, [selectedPhone]);

    const { isConnected } = useWebSocket(wsUrl, {
        onMessage: handleMessage,
        onOpen: () => console.log('✅ WebSocket connected'),
        onClose: () => console.log('❌ WebSocket disconnected'),
    });

    // When selecting a conversation, show its messages
    const handleSelectConversation = (conv) => {
        setSelectedPhone(conv.phone);
        // Load messages from map
        const msgs = messagesMapRef.current[conv.phone] || [];
        setCurrentMessages([...msgs]);
    };

    // Get selected conversation object
    const selectedConversation = conversations.find(c => c.phone === selectedPhone);

    return (
        <div className="conversations-page" style={{ display: 'flex', height: 'calc(100vh - 120px)', background: '#f8f9fa' }}>
            {/* Sidebar - Conversations List */}
            <div
                className="conversations-sidebar"
                style={{
                    width: '320px',
                    borderRight: '1px solid #e0e0e0',
                    background: '#fff',
                    overflow: 'auto',
                }}
            >
                <div style={{ padding: '20px', borderBottom: '1px solid #e0e0e0' }}>
                    <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Conversations</h2>
                    <div
                        style={{
                            marginTop: '10px',
                            fontSize: '0.875rem',
                            color: isConnected ? '#10b981' : '#ef4444',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                        }}
                    >
                        <span style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: isConnected ? '#10b981' : '#ef4444'
                        }} />
                        {isConnected ? 'Connected' : 'Disconnected'}
                    </div>
                </div>

                <div>
                    {conversations.length === 0 ? (
                        <div style={{ padding: '40px 20px', textAlign: 'center', color: '#9ca3af' }}>
                            No conversations yet
                        </div>
                    ) : (
                        conversations.map((conv) => (
                            <div
                                key={conv.phone}
                                onClick={() => handleSelectConversation(conv)}
                                style={{
                                    padding: '16px 20px',
                                    borderBottom: '1px solid #f3f4f6',
                                    cursor: 'pointer',
                                    background: selectedPhone === conv.phone ? '#f3f4f6' : '#fff',
                                    transition: 'background 0.2s',
                                }}
                                onMouseEnter={(e) => {
                                    if (selectedPhone !== conv.phone) {
                                        e.currentTarget.style.background = '#f9fafb';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (selectedPhone !== conv.phone) {
                                        e.currentTarget.style.background = '#fff';
                                    }
                                }}
                            >
                                <div style={{ fontWeight: 600, marginBottom: '4px' }}>{conv.name}</div>
                                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '4px' }}>
                                    {conv.phone}
                                </div>
                                <div
                                    style={{
                                        fontSize: '0.875rem',
                                        color: '#9ca3af',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                    }}
                                >
                                    {conv.lastMessage}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Main - Messages View */}
            <div className="messages-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#fff' }}>
                {!selectedConversation ? (
                    <div
                        style={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#9ca3af',
                        }}
                    >
                        Select a conversation to view messages
                    </div>
                ) : (
                    <>
                        {/* Header */}
                        <div
                            style={{
                                padding: '20px',
                                borderBottom: '1px solid #e0e0e0',
                                background: '#fff',
                            }}
                        >
                            <h3 style={{ margin: 0 }}>{selectedConversation.name}</h3>
                            <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '4px' }}>
                                {selectedConversation.phone}
                            </div>
                        </div>

                        {/* Messages */}
                        <div
                            style={{
                                flex: 1,
                                padding: '20px',
                                overflow: 'auto',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '12px',
                                background: '#f9fafb',
                            }}
                        >
                            {currentMessages.length === 0 ? (
                                <div style={{ textAlign: 'center', color: '#9ca3af', padding: '40px' }}>
                                    No messages yet - send a message to see it here!
                                </div>
                            ) : (
                                currentMessages.map((msg, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            display: 'flex',
                                            justifyContent: msg.role === 'user' ? 'flex-start' : 'flex-end',
                                        }}
                                    >
                                        <div
                                            style={{
                                                maxWidth: '70%',
                                                padding: '12px 16px',
                                                borderRadius: '12px',
                                                background: msg.role === 'user' ? '#e5e7eb' : '#3b82f6',
                                                color: msg.role === 'user' ? '#1f2937' : '#fff',
                                                whiteSpace: 'pre-wrap',
                                            }}
                                        >
                                            <div>{msg.content}</div>
                                            <div
                                                style={{
                                                    fontSize: '0.75rem',
                                                    marginTop: '6px',
                                                    opacity: 0.7,
                                                }}
                                            >
                                                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
