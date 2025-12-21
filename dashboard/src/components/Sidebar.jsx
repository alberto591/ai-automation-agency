import React, { useState } from 'react';
import { Search, CircleUserRound } from 'lucide-react';
import { useLeads } from '../hooks/useLeads';
import ProfileDropdown from './ProfileDropdown';

export default function Sidebar({ selectedLead, setSelectedLead }) {
    const { leads, loading } = useLeads();
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    const filteredLeads = leads.filter(lead =>
        (lead.name || "").toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="flex flex-col h-full bg-[hsl(var(--zen-sidebar))] border-r border-[hsl(var(--zen-border))] shadow-sm z-20">
            {/* Header */}
            <div className="p-5 flex justify-between items-center border-b border-[hsl(var(--zen-border))] bg-white/50 backdrop-blur-sm relative z-30">
                <div className="font-bold text-[hsl(var(--zen-text-main))] text-xl tracking-tight">Inbox</div>
                <div
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className={`p-2 rounded-full transition-all duration-200 cursor-pointer ${isProfileOpen ? 'bg-[hsl(var(--zen-accent))/10] text-[hsl(var(--zen-accent))]' : 'hover:bg-gray-100 text-[hsl(var(--zen-text-muted))]'}`}
                >
                    <CircleUserRound className="w-6 h-6" />
                </div>

                <ProfileDropdown
                    isOpen={isProfileOpen}
                    onClose={() => setIsProfileOpen(false)}
                />
            </div>

            {/* Search */}
            <div className="p-4 bg-white/30">
                <div className="relative group">
                    <Search className="absolute left-3 top-3 text-[hsl(var(--zen-text-muted))] w-4 h-4 transition-colors group-focus-within:text-[hsl(var(--zen-accent))] pointer-events-none" />
                    <input
                        type="text"
                        placeholder="Cerca conversazioni..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-[hsl(var(--zen-bg))] border border-transparent rounded-xl text-sm focus:outline-none focus:border-[hsl(var(--zen-accent))] focus:bg-white transition-all shadow-inner"
                    />
                </div>
            </div>

            {/* Lead List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {loading && (
                    <div className="p-8 text-center space-y-3">
                        <div className="w-8 h-8 border-2 border-[hsl(var(--zen-accent))] border-t-transparent rounded-full animate-spin mx-auto"></div>
                        <div className="text-xs font-medium text-[hsl(var(--zen-text-muted))]">Caricamento...</div>
                    </div>
                )}

                {!loading && filteredLeads.length === 0 && (
                    <div className="p-8 text-center text-[hsl(var(--zen-text-muted))] text-sm italic">
                        {leads.length === 0 ? "Nessuna chat trovata." : "Nessun risultato."}
                    </div>
                )}

                {filteredLeads.map((lead) => (
                    <div
                        key={lead.id}
                        onClick={() => setSelectedLead(lead)}
                        className={`flex items-center p-4 cursor-pointer transition-all duration-200 border-l-4 ${selectedLead?.id === lead.id
                            ? 'bg-[hsl(var(--zen-bg))] border-[hsl(var(--zen-accent))] shadow-inner'
                            : 'bg-transparent border-transparent hover:bg-gray-50/80 hover:border-gray-100'
                            }`}
                    >
                        {/* Avatar */}
                        <div className="relative mr-4 shrink-0">
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-[hsl(var(--zen-text-main))] font-bold text-lg shadow-sm">
                                {lead.name[0]?.toUpperCase()}
                            </div>
                            {lead.status === 'human_mode' && (
                                <span className="absolute -top-1 -right-1 flex h-4 w-4">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 border-2 border-white"></span>
                                </span>
                            )}
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-baseline mb-1">
                                <span className={`font-bold truncate ${selectedLead?.id === lead.id ? 'text-[hsl(var(--zen-text-main))]' : 'text-gray-700'}`}>
                                    {lead.name}
                                </span>
                                <span className="text-[10px] font-medium text-[hsl(var(--zen-text-muted))] uppercase tracking-tighter shrink-0 ml-2">
                                    {lead.time}
                                </span>
                            </div>
                            <div className="text-sm text-[hsl(var(--zen-text-muted))] truncate font-medium">
                                {lead.lastMsg}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
