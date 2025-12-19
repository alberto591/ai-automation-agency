import React from 'react';
import { X, Mail, Phone, MapPin, Wallet, Calendar } from 'lucide-react';

export default function LeadDrawer({ lead, isOpen, onClose }) {
    if (!isOpen || !lead) return null;

    // Data extraction with correct schema fields
    const budget = lead.budget_max || "N/A";
    const zone = lead.preferred_zones || "Analisi in corso...";
    const email = lead.email || "Non disponibile";
    const created = lead.created_at ? new Date(lead.created_at).toLocaleDateString() : "N/A";

    return (
        <div className={`absolute top-0 right-0 h-full w-full md:w-96 bg-white shadow-2xl border-l border-[hsl(var(--zen-border))] transform transition-transform duration-500 ease-in-out z-30 flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>

            {/* Header */}
            <div className="bg-white p-6 flex justify-between items-center border-b border-[hsl(var(--zen-border))]">
                <h2 className="font-bold text-[hsl(var(--zen-text-main))] text-xl tracking-tight">Dettaglio Lead</h2>
                <button onClick={onClose} className="p-2 hover:bg-gray-50 rounded-2xl transition-all">
                    <X className="w-5 h-5 text-[hsl(var(--zen-text-muted))]" />
                </button>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar bg-[hsl(var(--zen-bg))]/30">

                {/* Profile Picture & Identity */}
                <div className="flex flex-col items-center animate-in fade-in slide-in-from-top-4 duration-500">
                    <div className="w-28 h-28 rounded-[2.5rem] bg-gradient-to-br from-gray-50 to-white flex items-center justify-center text-4xl text-[hsl(var(--zen-text-main))] font-black mb-4 shadow-xl border-4 border-white">
                        {lead.name ? lead.name[0].toUpperCase() : "?"}
                    </div>
                    <h3 className="text-2xl font-bold text-[hsl(var(--zen-text-main))] text-center tracking-tight">{lead.name}</h3>
                    <div className="mt-2 px-3 py-1 bg-white rounded-full border border-[hsl(var(--zen-border))] text-[10px] font-bold text-[hsl(var(--zen-text-muted))] uppercase tracking-widest flex items-center">
                        <Phone className="w-3 h-3 mr-2" />
                        {lead.phone}
                    </div>
                </div>

                {/* AI Profiling Cards */}
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
                    <h4 className="text-[10px] uppercase font-black text-[hsl(var(--zen-text-muted))] tracking-[0.2em] ml-1">AI Intelligence</h4>

                    <div className="grid grid-cols-1 gap-3">
                        <div className="bg-white p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
                            <div className="absolute top-0 right-0 w-24 h-24 bg-green-50 rounded-full -mr-8 -mt-8 opacity-50 group-hover:scale-110 transition-transform"></div>
                            <div className="relative">
                                <Wallet className="w-6 h-6 mb-3 text-[hsl(var(--zen-accent))]" />
                                <div className="text-[10px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Budget Stimato</div>
                                <div className="text-xl font-black text-[hsl(var(--zen-text-main))]">{budget !== "N/A" ? `${budget}€` : "Analisi in corso..."}</div>
                            </div>
                        </div>

                        <div className="bg-white p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
                            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 opacity-50 group-hover:scale-110 transition-transform"></div>
                            <div className="relative">
                                <MapPin className="w-6 h-6 mb-3 text-blue-500" />
                                <div className="text-[10px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Zone di Interesse</div>
                                <div className="text-sm font-bold text-[hsl(var(--zen-text-main))] leading-relaxed italic">
                                    {Array.isArray(zone) ? zone.join(" • ") : zone}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* CRM Details */}
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
                    <h4 className="text-[10px] uppercase font-black text-[hsl(var(--zen-text-muted))] tracking-[0.2em] ml-1">Anagrafica CRM</h4>

                    <div className="space-y-3 bg-white/50 p-2 rounded-[2rem] border border-[hsl(var(--zen-border))]">
                        <div className="flex items-center text-[hsl(var(--zen-text-main))] bg-white p-4 rounded-2xl shadow-sm border border-[hsl(var(--zen-border))]">
                            <Mail className="w-5 h-5 mr-3 text-gray-400" />
                            <span className="text-sm font-semibold truncate">{email}</span>
                        </div>
                        <div className="flex items-center text-[hsl(var(--zen-text-main))] bg-white p-4 rounded-2xl shadow-sm border border-[hsl(var(--zen-border))]">
                            <Calendar className="w-5 h-5 mr-3 text-gray-400" />
                            <span className="text-sm font-semibold">Attivato il {created}</span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="pt-6 grid grid-cols-1 gap-3 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-450">
                    <button
                        onClick={() => alert("Funzionalità in arrivo!")}
                        className="w-full py-4 bg-[hsl(var(--zen-text-main))] text-white rounded-2xl text-sm font-bold shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition-all"
                    >
                        Modifica Profilo
                    </button>
                    <button
                        onClick={() => alert("Lead Archiviato")}
                        className="w-full py-4 bg-white border border-red-100 text-red-500 rounded-2xl text-sm font-bold hover:bg-red-50 transition-all"
                    >
                        Archivia Conversazione
                    </button>
                </div>

            </div>
        </div>
    );
}
