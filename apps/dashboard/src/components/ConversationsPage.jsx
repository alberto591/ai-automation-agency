import { useState, useMemo, useCallback, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import ChatWindow from './ChatWindow';
import { MessageSquare } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useIsMobile } from '../hooks/useMediaQuery';
import { useNotifications } from '../contexts/NotificationContext';

export default function ConversationsPage({ session }) {
    const { t } = useLanguage();
    const isMobile = useIsMobile();
    const { notify, requestBrowserPermission } = useNotifications();
    const [conversations, setConversations] = useState([]);
    const [selectedPhone, setSelectedPhone] = useState(null);


    // Memoize WebSocket URL to prevent reconnection loops
    const wsUrl = useMemo(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
        const baseUrl = apiUrl.replace(/^https?:\/\//, '');
        return `${wsProtocol}://${baseUrl}/ws/conversations`;
    }, []);

    // Request browser notification permission on mount
    useEffect(() => {
        requestBrowserPermission();
    }, [requestBrowserPermission]);

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

            // Show notification for new message
            const isNewConv = !conversations.find(c => c.phone === phone);
            const isBackground = selectedPhone !== phone;

            if (isBackground || isNewConv) {
                notify({
                    message: `${data.lead_name || 'New message'}: ${data.message.content}`,
                    priority: 'low'
                });
            }

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

    const { isConnected, lastMessage } = useWebSocket(wsUrl, {
        onMessage: handleMessage,
        onOpen: () => console.log('✅ WebSocket connected'),
        onClose: () => console.log('❌ WebSocket disconnected'),
        token: session?.access_token,
        reconnectAttempts: 10,
        reconnectInterval: 3000
    });

    // When selecting a conversation, just set the phone - ChatWindow handles message fetching
    const handleSelectConversation = (conv) => {
        setSelectedPhone(conv.phone);
    };

    // Back to list on mobile
    const handleBackToList = () => {
        setSelectedPhone(null);
    };


    // Get selected conversation object
    const selectedConversation = conversations.find(c => c.phone === selectedPhone);

    // Mobile: Show list OR chat (not both)
    // Desktop: Show both side-by-side
    const showList = !isMobile || !selectedPhone;
    const showChat = !isMobile || selectedPhone;

    return (
        <div className="conversations-page flex h-[calc(100vh-120px)] bg-gray-50">
            {/* Sidebar - Conversations List */}
            {showList && (
                <div
                    className={`
                        conversations-sidebar
                        ${isMobile ? 'w-full' : 'w-80'}
                        border-r border-gray-200 bg-white overflow-auto
                    `}
                >
                    <div className="p-4 md:p-5 border-b border-gray-200">
                        <h2 className="text-xl md:text-2xl font-bold m-0">{t('conversations.title')}</h2>
                        <div className="mt-2 md:mt-3 text-sm flex items-center gap-2"
                            style={{ color: isConnected ? '#10b981' : '#ef4444' }}
                        >
                            <span
                                className="w-2 h-2 rounded-full"
                                style={{ background: isConnected ? '#10b981' : '#ef4444' }}
                            />
                            {isConnected ? t('conversations.connected') : t('conversations.disconnected')}
                        </div>
                    </div>

                    <div>
                        {conversations.length === 0 ? (
                            <div className="p-8 md:p-10 text-center text-gray-400">
                                {t('conversations.empty.title')}
                            </div>
                        ) : (
                            conversations.map((conv) => (
                                <div
                                    key={conv.phone}
                                    onClick={() => handleSelectConversation(conv)}
                                    className={`
                                        p-4 border-b border-gray-100 cursor-pointer
                                        transition-colors
                                        ${selectedPhone === conv.phone ? 'bg-gray-100' : 'bg-white hover:bg-gray-50'}
                                        active:bg-gray-200
                                    `}
                                >
                                    <div className="font-semibold mb-1">{conv.name}</div>
                                    <div className="text-sm text-gray-600 mb-1">{conv.phone}</div>
                                    <div className="text-sm text-gray-400 truncate">{conv.lastMessage}</div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Main - Messages View */}
            {showChat && (
                <div className="messages-panel flex-1 flex flex-col bg-white">
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
                            <div>{t('conversations.selectChat')}</div>
                        </div>
                    ) : (
                        <ChatWindow
                            selectedLead={{
                                id: selectedConversation.leadId,
                                phone: selectedConversation.phone,
                                name: selectedConversation.name
                            }}
                            onBack={isMobile ? handleBackToList : undefined}
                            realtimeMessage={lastMessage}
                        />
                    )}
                </div>
            )}
        </div>
    );
}
