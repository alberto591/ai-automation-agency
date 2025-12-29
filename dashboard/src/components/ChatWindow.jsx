import React, { useEffect, useRef, useState } from 'react';
import { Send, Phone, MoreVertical, Info, Bot, User } from 'lucide-react';
import { useMessages } from '../hooks/useMessages';

import LeadDrawer from './LeadDrawer';
import EmptyState from './EmptyState';
import Tooltip from './Tooltip';

export default function ChatWindow({ selectedLead }) {
    const { messages, setMessages, status, setStatus, loading } = useMessages(selectedLead?.id);
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

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

        const newMessage = {
            role: 'assistant',
            content: inputText,
            metadata: { by: 'human_agent' },
            created_at: new Date().toISOString()
        };

        // Optimistic Update
        setMessages(prev => [...prev, newMessage]);
        setInputText(""); // Clear input immediately

        try {
            const response = await fetch('/api/leads/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: selectedLead.phone,
                    message: inputText
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                // Revert on failure (optional, or just alert)
                throw new Error("Failed to send");
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                alert("Errore: Il server non risponde (Timeout).");
            } else {
                alert("Errore nell'invio: " + error.message);
            }
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
            const response = await fetch(endpoint, {
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
            <div className="flex-1 flex items-center justify-center bg-white/20">
                <div className="text-center space-y-6 max-w-md p-10 animate-fade-in">
                    <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-[2rem] flex items-center justify-center mx-auto shadow-xl shadow-indigo-500/20 animate-float">
                        <Bot className="w-12 h-12 text-white" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-bold text-slate-800 tracking-tight">Benvenuto</h2>
                        <p className="text-slate-500 text-sm mt-3 leading-relaxed">Seleziona un lead dalla lista per gestire le conversazioni e le trattative in corso.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white relative overflow-hidden">
            {/* Header */}
            <div className="px-6 py-5 bg-white/20 backdrop-blur-xl flex justify-between items-center z-10 transition-all duration-300">
                <div className="flex items-center cursor-pointer group" onClick={() => setDrawerOpen(!drawerOpen)}>
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center text-slate-800 font-bold mr-4 shadow-sm border border-white group-hover:border-indigo-500/30 transition-all duration-300 group-hover:scale-105">
                        {selectedLead.name[0]?.toUpperCase()}
                    </div>
                    <div>
                        <div className="font-bold text-slate-800 text-xl tracking-tight">{selectedLead.name}</div>
                        <div className="flex items-center text-[10px] font-bold uppercase tracking-widest text-slate-400">
                            {status === 'human_mode' ? (
                                <>
                                    <span className="w-2 h-2 rounded-full bg-orange-500 mr-2 shadow-sm shadow-orange-500/40"></span>
                                    <span>Presa in carico</span>
                                </>
                            ) : (
                                <>
                                    <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2 shadow-sm shadow-indigo-500/40 animate-pulse"></span>
                                    <span>AI Attiva</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    {/* Premium Toggle Switch */}
                    <Tooltip content={status === 'human_mode' ? "Riattiva AI Agent" : "Passa a Modalità Manuale"} position="bottom">
                        <div
                            onClick={toggleAiMode}
                            className={`relative w-24 h-9 flex items-center rounded-full p-1 cursor-pointer transition-all duration-300 shadow-inner hover:scale-105 active:scale-95 ${status === 'human_mode' ? 'bg-slate-200' : 'bg-indigo-100'
                                }`}
                        >
                            <div className={`absolute text-[9px] font-black uppercase tracking-tighter transition-all duration-300 ${status === 'human_mode' ? 'right-3 text-slate-400' : 'left-8 text-indigo-700'}`}>
                                {status === 'human_mode' ? 'Manual' : 'Auto'}
                            </div>
                            <div className={`w-7 h-7 bg-white rounded-full shadow-md transform transition-transform duration-500 flex items-center justify-center ${status === 'human_mode' ? 'translate-x-0' : 'translate-x-15'
                                }`}>
                                {status === 'human_mode' ? <User className="w-3.5 h-3.5 text-slate-400" /> : <Bot className="w-3.5 h-3.5 text-indigo-600" />}
                            </div>
                        </div>
                    </Tooltip>

                    <Tooltip content="Dettagli Lead" position="bottom">
                        <button
                            onClick={() => setDrawerOpen(!drawerOpen)}
                            className={`p-2.5 rounded-xl transition-all duration-300 hover:scale-110 active:scale-95 ${drawerOpen
                                ? 'bg-green-50 text-[hsl(var(--zen-accent))] shadow-inner'
                                : 'hover:bg-gray-50 text-[hsl(var(--zen-text-muted))]'
                                }`}
                        >
                            <Info className="w-5.5 h-5.5" />
                        </button>
                    </Tooltip>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden relative bg-[hsl(var(--zen-bg))]/50">

                {/* Messages Area */}
                <div className="flex-1 flex flex-col min-w-0">
                    <div className="flex-1 p-6 md:p-10 overflow-y-auto space-y-6 custom-scrollbar scroll-smooth">
                        {loading && (
                            <div className="flex justify-center p-8 animate-fade-in">
                                <div className="flex items-center space-x-2 text-indigo-600 bg-white/50 px-4 py-2 rounded-full shadow-sm">
                                    <div className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    <span className="text-xs font-bold uppercase tracking-widest ml-2">Syncing</span>
                                </div>
                            </div>
                        )}

                        {!loading && messages.length === 0 && (
                            <EmptyState variant="no-messages" />
                        )}

                        {messages.map((msg, index) => (
                            <MessageBubble
                                key={msg.id || index}
                                isAi={msg.role === 'assistant'}
                                text={msg.content}
                                isHuman={msg.metadata?.by === 'human_agent'}
                                status={msg.status}
                                mediaUrl={msg.media_url}
                                channel={msg.channel}
                                time={new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                index={index}
                            />
                        ))}
                        <div ref={bottomRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-6 bg-white/10 backdrop-blur-md flex items-center space-x-4">
                        <Tooltip content="Opzioni (in arrivo)" position="top">
                            <div className="p-3 text-slate-400 hover:bg-white/50 rounded-2xl cursor-not-allowed transition-all hover:scale-110">
                                <MoreVertical className="w-5 h-5" />
                            </div>
                        </Tooltip>

                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && !sending && sendMessage()}
                            placeholder="Scrivi un messaggio..."
                            className="flex-1 p-4 bg-white/50 rounded-2xl border border-transparent focus:outline-none focus:bg-white focus:border-indigo-500/30 transition-all text-sm font-medium shadow-inner hover:bg-white/70"
                            disabled={sending}
                        />

                        <Tooltip content="Invia messaggio" position="top">
                            <button
                                onClick={sendMessage}
                                disabled={sending || !inputText.trim()}
                                className={`p-4 rounded-2xl transition-all duration-300 flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 ${sending
                                    ? 'bg-slate-100 text-slate-300'
                                    : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-indigo-500/30 hover:-translate-y-0.5 active:translate-y-0'
                                    }`}
                            >
                                <Send className={`w-5 h-5 ${sending ? 'animate-pulse' : ''}`} />
                            </button>
                        </Tooltip>
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

import { Check, CheckCheck, Clock, AlertCircle, FileText, Image as ImageIcon, MessageSquare } from 'lucide-react';

function MessageBubble({ isAi, text, time, isHuman, status, mediaUrl, channel, index }) {
    const renderStatus = () => {
        if (!isAi) return null;
        switch (status) {
            case 'queued':
            case 'sending':
                return <Clock className="w-3 h-3 text-slate-400" />;
            case 'sent':
                return <Check className="w-3 h-3 text-slate-400" />;
            case 'delivered':
                return <CheckCheck className="w-3 h-3 text-slate-400" />;
            case 'read':
                return <CheckCheck className="w-3 h-3 text-indigo-500" />;
            case 'failed':
                return <AlertCircle className="w-3 h-3 text-red-500" />;
            default:
                return null;
        }
    };

    const isImage = (url) => {
        if (!url) return false;
        return /\.(jpg|jpeg|png|webp|gif)$/i.test(url) || url.includes('image');
    };

    const renderMedia = () => {
        if (!mediaUrl) return null;
        if (isImage(mediaUrl)) {
            return (
                <div className="mb-2 rounded-lg overflow-hidden border border-white/20 shadow-sm max-w-full">
                    <img src={mediaUrl} alt="Media" className="max-h-64 object-cover w-full hover:scale-105 transition-transform duration-500 cursor-pointer" />
                </div>
            )
        }
        return (
            <a href={mediaUrl} target="_blank" rel="noreferrer" className="flex items-center space-x-2 p-2 mb-2 bg-black/5 rounded-lg border border-white/10 hover:bg-black/10 transition-colors">
                <FileText className="w-5 h-5" />
                <span className="text-xs font-bold truncate">Visualizza Documento</span>
            </a>
        )
    };

    const renderChannel = () => {
        if (channel === 'voice') return <Phone className="w-2.5 h-2.5 opacity-50" />;
        if (channel === 'email') return <FileText className="w-2.5 h-2.5 opacity-50" />;
        return <MessageSquare className="w-2.5 h-2.5 opacity-50" />;
    };

    return (
        <div
            className={`flex ${isAi ? 'justify-end' : 'justify-start'} animate-scale-in origin-${isAi ? 'bottom-right' : 'bottom-left'}`}
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <div
                className={`max-w-[85%] md:max-w-[70%] p-4 shadow-sm text-sm relative leading-relaxed transition-all hover:shadow-md duration-300 ${isAi
                    ? (isHuman
                        ? 'bg-orange-50 text-orange-900 rounded-2xl rounded-tr-none border border-orange-100 hover:bg-orange-100'
                        : 'bubble-ai hover:brightness-110')
                    : 'bubble-user hover:bg-white'
                    }`}
            >
                {renderMedia()}
                {text && <div className="whitespace-pre-wrap font-medium">{text}</div>}
                <div className={`text-[9px] font-bold uppercase tracking-tight flex items-center justify-end gap-1.5 mt-2 ${isAi && !isHuman ? 'text-white/60' : 'text-gray-400'
                    }`}>
                    {renderChannel()}
                    {time}
                    <span className="mx-0.5">•</span>
                    {isHuman ? <User className="w-3 h-3" /> : (isAi ? <Bot className="w-3 h-3" /> : null)}
                    {renderStatus()}
                </div>
            </div>
        </div>
    )
}
