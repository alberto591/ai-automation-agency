import { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

export default function ConversationsPage() {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [messages, setMessages] = useState([]);

    // Determine WebSocket URL based on environment
    const getWebSocketUrl = () => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
        const baseUrl = apiUrl.replace(/^https?:\/\//, '');
        return `${wsProtocol}://${baseUrl}/ws/conversations`;
    };

    const { isConnected, lastMessage } = useWebSocket(getWebSocketUrl(), {
        onMessage: (data) => {
            console.log('📨 Received message:', data);

            if (data.type === 'message') {
                // Update conversations list
                setConversations((prev) => {
                    const existingIndex = prev.findIndex((conv) => conv.phone === data.phone);
                    const updatedConv = {
                        phone: data.phone,
                        name: data.lead_name,
                        lastMessage: data.message.content,
                        lastMessageTime: data.message.timestamp,
                        role: data.message.role,
                    };

                    if (existingIndex >= 0) {
                        const updated = [...prev];
                        updated[existingIndex] = updatedConv;
                        // Move to top
                        updated.unshift(updated.splice(existingIndex, 1)[0]);
                        return updated;
                    }
                    return [updatedConv, ...prev];
                });

                // Update messages if this conversation is selected
                if (selectedConversation?.phone === data.phone) {
                    setMessages((prev) => [...prev, data.message]);
                }
            }
        },
        onOpen: () => {
            console.log('✅ WebSocket connected');
        },
        onClose: () => {
            console.log('❌ WebSocket disconnected');
        },
    });

    // Fetch initial conversations and messages
    useEffect(() => {
        const fetchConversations = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${apiUrl}/api/leads`);
                if (response.ok) {
                    const data = await response.json();
                    // Transform to conversation format
                    const convs = data.map((lead) => ({
                        phone: lead.phone,
                        name: lead.name || 'Unknown',
                        lastMessage: lead.last_message || 'No messages yet',
                        lastMessageTime: lead.updated_at,
                        role: 'system',
                    }));
                    setConversations(convs);
                }
            } catch (error) {
                console.error('Failed to fetch conversations:', error);
            }
        };

        fetchConversations();
    }, []);

    // Fetch messages for selected conversation
    useEffect(() => {
        if (!selectedConversation) return;

        const fetchMessages = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${apiUrl}/api/leads/${selectedConversation.phone}/messages`);
                if (response.ok) {
                    const data = await response.json();
                    setMessages(data);
                }
            } catch (error) {
                console.error('Failed to fetch messages:', error);
            }
        };

        fetchMessages();
    }, [selectedConversation]);

    return (
        <div className=\"conversations-page\" style={{ display: 'flex', height: '100vh', background: '#f8f9fa' }}>
    {/* Sidebar - Conversations List */ }
    <div
        className=\"conversations-sidebar\"
    style = {{
        width: '320px',
            borderRight: '1px solid #e0e0e0',
                background: '#fff',
                    overflow: 'auto',
        }
}
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
                onClick={() => setSelectedConversation(conv)}
                style={{
                  padding: '16px 20px',
                  borderBottom: '1px solid #f3f4f6',
                  cursor: 'pointer',
                  background: selectedConversation?.phone === conv.phone ? '#f3f4f6' : '#fff',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (selectedConversation?.phone !== conv.phone) {
                    e.currentTarget.style.background = '#f9fafb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedConversation?.phone !== conv.phone) {
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
      </div >

    {/* Main - Messages View */ }
    < div className =\"messages-panel\" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
{
    !selectedConversation ? (
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
                }}
            >
                {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#9ca3af', padding: '40px' }}>
                        No messages yet
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <div
                            key={idx}
                            style={{
                                display: 'flex',
                                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                            }}
                        >
                            <div
                                style={{
                                    maxWidth: '70%',
                                    padding: '12px 16px',
                                    borderRadius: '12px',
                                    background: msg.role === 'user' ? '#3b82f6' : '#f3f4f6',
                                    color: msg.role === 'user' ? '#fff' : '#1f2937',
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
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </>
    )
}
      </div >
    </div >
  );
}
