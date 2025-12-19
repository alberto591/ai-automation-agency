import React, { useEffect, useRef, useState } from 'react';
import { Send, Phone, MoreVertical, Info, Bot, User } from 'lucide-react';
import { useMessages } from '../hooks/useMessages';

import LeadDrawer from './LeadDrawer';

export default function ChatWindow({ selectedLead }) {
    const { messages, status, setStatus, loading } = useMessages(selectedLead?.id);
    const bottomRef = useRef(null);
    const [inputText, setInputText] = useState("");
    const [sending, setSending] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);

    // Auto-scroll to bottom
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Close drawer when lead changes
    useEffect(() => {
        setDrawerOpen(false);
    }, [selectedLead]);

    async function sendMessage() {
        if (!inputText.trim() || !selectedLead) return;
        setSending(true);

        try {
            const response = await fetch('http://localhost:8000/api/leads/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: selectedLead.phone,
                    message: inputText
                })
            });

            if (!response.ok) throw new Error("Failed to send");

            setInputText(""); // Clear input on success
        } catch (error) {
            alert("Errore nell'invio: " + error.message);
        } finally {
            setSending(false);
        }
    }

    async function toggleAiMode() {
        if (!selectedLead) return;

        const isAiActive = status !== 'human_mode';
        const newStatus = isAiActive ? 'human_mode' : 'active';

        // 1. Optimistic Update (Instant feedback)
        setStatus(newStatus);

        const endpoint = isAiActive ? '/api/leads/takeover' : '/api/leads/resume';

        try {
            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: selectedLead.phone })
            });

            if (!response.ok) throw new Error("Failed to toggle AI");

            // Success! No need to do anything, optimistic update was correct.
        } catch (error) {
            // 2. Revert on Error
            setStatus(isAiActive ? 'active' : 'human_mode');
            alert("Errore cambio modalità: " + error.message);
        }
    }

    if (!selectedLead) {
        return (
            <div className="flex-1 flex items-center justify-center bg-[#f0f2f5] border-l border-gray-300">
                <div className="text-center text-gray-500">
                    <h2 className="text-xl font-light mb-2">Agenzia AI Dashboard</h2>
                    <p className="text-sm">Seleziona una chat per iniziare</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-[#efeae2] relative overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 bg-[#f0f2f5] flex justify-between items-center border-b border-gray-300 shadow-sm z-10">
                <div className="flex items-center cursor-pointer" onClick={() => setDrawerOpen(!drawerOpen)}>
                    <div className="w-10 h-10 rounded-full bg-gray-400 flex items-center justify-center text-white font-bold mr-3">
                        {selectedLead.name[0]?.toUpperCase()}
                    </div>
                    <div>
                        <div className="font-semibold text-gray-800">{selectedLead.name}</div>
                        <div className="text-xs text-gray-500">{status === 'human_mode' ? '🛑 AI Stopped' : '✅ AI Active'}</div>
                    </div>
                </div>

                <div className="flex items-center space-x-4 text-gray-600">
                    <div
                        onClick={toggleAiMode}
                        className={`flex items-center px-3 py-1 rounded-full border cursor-pointer shadow-sm transition-all ${status === 'human_mode'
                            ? 'bg-gray-100 border-gray-300 hover:bg-gray-200'
                            : 'bg-white border-green-200 hover:bg-green-50'
                            }`}
                    >
                        <span className={`w-2 h-2 rounded-full mr-2 ${status === 'human_mode' ? 'bg-gray-400' : 'bg-green-500'}`}></span>
                        <span className={`text-xs font-bold ${status === 'human_mode' ? 'text-gray-600' : 'text-green-700'}`}>
                            {status === 'human_mode' ? 'AI OFF' : 'AI ON'}
                        </span>
                    </div>
                    <button onClick={() => setDrawerOpen(!drawerOpen)} className="p-2 hover:bg-gray-200 rounded-full">
                        <Info className={`w-5 h-5 ${drawerOpen ? 'text-green-600' : 'text-gray-600'}`} />
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden relative">

                {/* Messages Area */}
                <div className="flex-1 flex flex-col min-w-0">
                    <div className="flex-1 p-8 overflow-y-auto space-y-4">
                        {loading && <div className="text-center text-xs text-gray-500">Loading history...</div>}

                        {messages.map((msg, index) => (
                            <MessageBubble
                                key={index}
                                isAi={msg.role === 'assistant'}
                                text={msg.content}
                                isHuman={msg.metadata?.by === 'human_agent'}
                                time=""
                            />
                        ))}
                        <div ref={bottomRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-3 bg-[#f0f2f5] flex items-center space-x-2">
                        <div className="p-2 text-gray-500 hover:bg-gray-200 rounded-full cursor-not-allowed">
                            <MoreVertical className="w-5 h-5" />
                        </div>
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Scrivi un messaggio..."
                            className="flex-1 p-3 rounded-lg border-none focus:outline-none focus:ring-1 focus:ring-green-500"
                            disabled={sending}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={sending || !inputText.trim()}
                            className={`p-3 text-white rounded-full ${sending ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'}`}
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Sliding Info Drawer */}
                <LeadDrawer
                    lead={{ ...selectedLead, status }} // Pass updated status
                    isOpen={drawerOpen}
                    onClose={() => setDrawerOpen(false)}
                />

            </div>
        </div>
    );
}

function MessageBubble({ isAi, text, time, isHuman }) {
    return (
        <div className={`flex ${isAi ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[70%] p-3 rounded-lg shadow-sm text-sm relative leading-relaxed ${isAi ? (isHuman ? 'bg-[#fff5c4] rounded-tr-none' : 'bg-[#d9fdd3] rounded-tr-none') : 'bg-white rounded-tl-none'
                    }`}
            >
                <div className="mb-1 whitespace-pre-wrap">{text}</div>
                <div className="text-[10px] text-gray-500 text-right flex items-center justify-end gap-1 mt-1">
                    {time}
                    {isAi && (isHuman ? <User className="w-3 h-3 text-orange-600" /> : <Bot className="w-3 h-3 text-green-600" />)}
                </div>
            </div>
        </div>
    )
}
