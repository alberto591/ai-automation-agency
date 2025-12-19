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
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

            const response = await fetch(`${API_URL}/api/leads/message`, {
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

        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
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
            <div className="flex-1 flex items-center justify-center bg-[hsl(var(--zen-bg))] border-l border-[hsl(var(--zen-border))]">
                <div className="text-center space-y-4 max-w-md p-8 animate-in fade-in zoom-in duration-700">
                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto shadow-sm border border-[hsl(var(--zen-border))]">
                        <Bot className="w-10 h-10 text-[hsl(var(--zen-accent))]" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-[hsl(var(--zen-text-main))] tracking-tight">Agenzia AI Dashboard</h2>
                        <p className="text-[hsl(var(--zen-text-muted))] text-sm mt-2">Seleziona una conversazione per iniziare a gestire i tuoi lead con intelligenza.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white relative overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 bg-white/80 backdrop-blur-md flex justify-between items-center border-b border-[hsl(var(--zen-border))] z-10 shadow-sm">
                <div className="flex items-center cursor-pointer group" onClick={() => setDrawerOpen(!drawerOpen)}>
                    <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center text-[hsl(var(--zen-text-main))] font-bold mr-4 shadow-sm border border-gray-100 group-hover:border-[hsl(var(--zen-accent))] transition-all">
                        {selectedLead.name[0]?.toUpperCase()}
                    </div>
                    <div>
                        <div className="font-bold text-[hsl(var(--zen-text-main))] text-lg tracking-tight">{selectedLead.name}</div>
                        <div className="flex items-center text-[10px] font-bold uppercase tracking-widest text-[hsl(var(--zen-text-muted))]">
                            {status === 'human_mode' ? (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 mr-2"></span>
                                    <span>Presa in carico</span>
                                </>
                            ) : (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-2"></span>
                                    <span>AI Attiva</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    {/* Premium Toggle Switch */}
                    <div
                        onClick={toggleAiMode}
                        className={`relative w-24 h-9 flex items-center rounded-full p-1 cursor-pointer transition-all duration-300 shadow-inner ${status === 'human_mode' ? 'bg-gray-200' : 'bg-green-100'
                            }`}
                    >
                        <div className={`absolute text-[9px] font-black uppercase tracking-tighter transition-all duration-300 ${status === 'human_mode' ? 'right-3 text-gray-400' : 'left-8 text-green-700'}`}>
                            {status === 'human_mode' ? 'Manual' : 'Auto'}
                        </div>
                        <div className={`w-7 h-7 bg-white rounded-full shadow-md transform transition-transform duration-300 flex items-center justify-center ${status === 'human_mode' ? 'translate-x-0' : 'translate-x-15'
                            }`}>
                            {status === 'human_mode' ? <User className="w-3.5 h-3.5 text-gray-400" /> : <Bot className="w-3.5 h-3.5 text-green-600" />}
                        </div>
                    </div>

                    <button
                        onClick={() => setDrawerOpen(!drawerOpen)}
                        className={`p-2.5 rounded-xl transition-all ${drawerOpen
                                ? 'bg-green-50 text-[hsl(var(--zen-accent))] shadow-inner'
                                : 'hover:bg-gray-50 text-[hsl(var(--zen-text-muted))]'
                            }`}
                    >
                        <Info className="w-5.5 h-5.5" />
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden relative bg-[hsl(var(--zen-bg))]/50">

                {/* Messages Area */}
                <div className="flex-1 flex flex-col min-w-0">
                    <div className="flex-1 p-6 md:p-10 overflow-y-auto space-y-6 custom-scrollbar">
                        {loading && (
                            <div className="flex justify-center p-4">
                                <div className="animate-pulse text-[10px] font-bold uppercase tracking-widest text-gray-400">Syncing History...</div>
                            </div>
                        )}

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
                    <div className="p-4 bg-white/80 backdrop-blur-sm border-t border-[hsl(var(--zen-border))] flex items-center space-x-3">
                        <div className="p-3 text-[hsl(var(--zen-text-muted))] hover:bg-gray-100 rounded-2xl cursor-not-allowed transition-colors">
                            <MoreVertical className="w-5 h-5" />
                        </div>
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Scrivi un messaggio..."
                            className="flex-1 p-3.5 bg-[hsl(var(--zen-bg))] rounded-2xl border border-transparent focus:outline-none focus:bg-white focus:border-[hsl(var(--zen-accent))] transition-all text-sm font-medium"
                            disabled={sending}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={sending || !inputText.trim()}
                            className={`p-3.5 rounded-2xl transition-all flex items-center justify-center shadow-lg ${sending
                                    ? 'bg-gray-100 text-gray-300'
                                    : 'bg-[hsl(var(--zen-accent))] text-white hover:shadow-green-200 hover:-translate-y-0.5 active:translate-y-0'
                                }`}
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Sliding Info Drawer */}
                <LeadDrawer
                    lead={{ ...selectedLead, status }}
                    isOpen={drawerOpen}
                    onClose={() => setDrawerOpen(false)}
                />

            </div>
        </div>
    );
}

function MessageBubble({ isAi, text, time, isHuman }) {
    return (
        <div className={`flex ${isAi ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}>
            <div
                className={`max-w-[85%] md:max-w-[70%] p-4 shadow-sm text-sm relative leading-relaxed transition-all ${isAi
                        ? (isHuman ? 'bg-orange-50 text-orange-900 rounded-2xl rounded-tr-none border border-orange-100' : 'bubble-ai')
                        : 'bubble-user'
                    }`}
            >
                <div className="whitespace-pre-wrap font-medium">{text}</div>
                <div className={`text-[9px] font-bold uppercase tracking-tight flex items-center justify-end gap-1.5 mt-2 ${isAi && !isHuman ? 'text-white/60' : 'text-gray-400'
                    }`}>
                    {time}
                    {isAi && (isHuman ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />)}
                </div>
            </div>
        </div>
    )
}
