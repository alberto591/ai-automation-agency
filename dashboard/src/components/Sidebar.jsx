import React from 'react';
import { Search, CircleUserRound } from 'lucide-react';
import { useLeads } from '../hooks/useLeads';

export default function Sidebar({ selectedLead, setSelectedLead }) {
    const { leads, loading } = useLeads();

    return (
        <div className="flex flex-col h-full bg-white border-r border-gray-200">
            {/* Header */}
            <div className="p-4 bg-[#f0f2f5] flex justify-between items-center border-b">
                <div className="font-bold text-gray-700 text-lg">Inbox</div>
                <CircleUserRound className="text-gray-500" />
            </div>

            {/* Search */}
            <div className="p-2 bg-white">
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 text-gray-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Cerca o inizia una chat"
                        className="w-full pl-9 pr-4 py-2 bg-[#f0f2f5] rounded-lg text-sm focus:outline-none"
                    />
                </div>
            </div>

            {/* Lead List */}
            <div className="flex-1 overflow-y-auto">
                {loading && <div className="p-4 text-center text-gray-500">Caricamento...</div>}

                {!loading && leads.length === 0 && (
                    <div className="p-4 text-center text-gray-500">Nessuna chat trovata.</div>
                )}

                {leads.map((lead) => (
                    <div
                        key={lead.id}
                        onClick={() => setSelectedLead(lead)}
                        className={`flex items-center p-3 cursor-pointer hover:bg-gray-50 ${selectedLead?.id === lead.id ? 'bg-[#f0f2f5]' : ''}`}
                    >
                        <div className="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center text-white font-bold text-xl mr-3 shrink-0">
                            {lead.name[0]?.toUpperCase()}
                        </div>
                        <div className="flex-1 border-b border-gray-100 pb-3 min-w-0">
                            <div className="flex justify-between items-center mb-1">
                                <span className="font-semibold text-gray-900 truncate">{lead.name}</span>
                                <span className="text-xs text-gray-500 shrink-0 ml-2">{lead.time}</span>
                            </div>
                            <div className="text-sm text-gray-600 truncate flex items-center">
                                {lead.status === 'human_mode' && <span className="w-2 h-2 rounded-full bg-red-500 mr-2 shrink-0"></span>}
                                <span className="truncate block">{lead.lastMsg}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
