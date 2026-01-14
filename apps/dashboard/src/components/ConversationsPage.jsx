import { useState, useMemo, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import ChatWindow from './ChatWindow';
import { MessageSquare } from 'lucide-react';

export default function ConversationsPage({ session }) {
    const [conversations, setConversations] = useState([]);
    const [selectedPhone, setSelectedPhone] = useState(null);


    // Memoize WebSocket URL to prevent reconnection loops
    const wsUrl = useMemo(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
        const baseUrl = apiUrl.replace(/^https?:\/\//, '');
        return `${wsProtocol}://${baseUrl}/ws/conversations`;
    }, []);

    const handleMessage = useCallback((data) => {
        console.log('📨 Received message:', data);

        // Handle initial conversations list from backend
        if (data.type === 'conversations') {
            console.log('📋 Loading initial conversations:', data.data?.length);
            if (data.data && Array.isArray(data.data)) {
                const formattedConversations = data.data.map(lead => ({
                    phone: lead.customer_phone,
                    name: lead.customer_name || 'Unknown',
                    lastMessage: lead.ai_summary || 'No messages yet',
                    lastMessageTime: lead.updated_at,
                    status: lead.status,
                    score: lead.score || 0,
                    leadId: lead.id  // Add lead ID for fetching messages
                }));
                setConversations(formattedConversations);
                console.log('✅ Loaded', formattedConversations.length, 'conversations');
            }
        }
        // Handle individual message updates
        else if (data.type === 'message') {
            const phone = data.phone;

            // Update conversations list with new last message
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
        token: session?.access_token,
    });

    // When selecting a conversation, just set the phone - ChatWindow handles message fetching
    const handleSelectConversation = (conv) => {
        setSelectedPhone(conv.phone);
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
                            flexDirection: 'column',
                            gap: '12px'
                        }}
                    >
                        <div className="p-4 bg-indigo-50 rounded-full text-indigo-500">
                            <MessageSquare className="w-8 h-8 opacity-50" />
                        </div>
                        <div>Select a conversation to start chatting</div>
                    </div>
                ) : (
                    <ChatWindow
                        selectedLead={{
                            id: selectedConversation.leadId,
                            phone: selectedConversation.phone,
                            name: selectedConversation.name
                        }}
                    />
                )}
            </div>
        </div>
    );
}
