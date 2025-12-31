import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, MapPin, Wallet, Calendar, Check, Edit2, ShieldCheck, Sparkles, Zap, TrendingUp, AlertTriangle, HelpingHand } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function LeadDrawer({ lead, isOpen, onClose }) {
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        budget_max: '',
        preferred_zones: ''
    });
    const [isSaving, setIsSaving] = useState(false);
    const [marketData, setMarketData] = useState(null);
    const [appraisalData, setAppraisalData] = useState(null);
    const [isAppraising, setIsAppraising] = useState(false);
    const [appraisalParams, setAppraisalParams] = useState({ sqm: '100', type: 'apartment' });

    // Sync state with lead prop
    useEffect(() => {
        if (lead) {
            setFormData({
                name: lead.name || '',
                email: lead.email || '',
                budget_max: lead.budget_max || '',
                preferred_zones: Array.isArray(lead.preferred_zones) ? lead.preferred_zones.join(', ') : (lead.preferred_zones || '')
            });
            setIsEditing(false);

            // Try fetch market data for the first zone
            const zones = Array.isArray(lead.preferred_zones) ? lead.preferred_zones : (lead.preferred_zones?.split(',') || []);
            if (zones.length > 0 && typeof zones[0] === 'string' && zones[0].trim().length > 2) {
                fetchMarketData(zones[0].trim());
            } else {
                setMarketData(null);
            }
        }
    }, [lead, isOpen]);

    async function fetchMarketData(zone) {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            const token = session?.access_token;
            if (!token) return;

            const response = await fetch(`/api/market/valuation?zone=${encodeURIComponent(zone)}&city=Milano`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const res = await response.json();
                if (res.status === 'success') {
                    setMarketData(res.data);
                }
            }
        } catch (e) {
            console.error("Market data fetch failed", e);
        }
    }

    async function handleAppraisal() {
        if (!lead || !formData.preferred_zones) {
            alert("Specifica una zona tra le preferenze per avviare la stima.");
            return;
        }
        setIsAppraising(true);
        try {
            const { data: { session } } = await supabase.auth.getSession();
            const token = session?.access_token;

            const zoneRaw = formData.preferred_zones.split(',')[0].trim();

            const payload = {
                city: "Milano",
                zone: zoneRaw,
                property_type: appraisalParams.type,
                surface_sqm: parseInt(appraisalParams.sqm) || 100,
                condition: "good"
            };

            const response = await fetch('/api/appraisals/estimate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const res = await response.json();
                setAppraisalData(res);
            } else {
                const err = await response.text();
                alert("Errore stima: " + err);
            }
        } catch (e) {
            console.error("Appraisal failed", e);
            alert("Errore di connessione.");
        } finally {
            setIsAppraising(false);
        }
    }

    if (!isOpen || !lead) return null;

    const budget = lead.budget_max || "N/A";
    const zone = lead.preferred_zones || "Analisi in corso...";
    const email = lead.email || "Non disponibile";
    const created = lead.created_at ? new Date(lead.created_at).toLocaleDateString() : "N/A";

    async function handleArchive() {
        if (!window.confirm("Sei sicuro di voler archiviare questa conversazione?")) return;

        setIsSaving(true);
        try {
            const { error } = await supabase
                .from('leads')
                .update({ status: 'archived' })
                .eq('id', lead.id);

            if (error) throw error;
            onClose();
        } catch (error) {
            alert("Errore durante l'archiviazione: " + error.message);
        } finally {
            setIsSaving(false);
        }
    }

    async function handleSave() {
        setIsSaving(true);
        try {
            const zonesArray = formData.preferred_zones.split(',').map(s => s.trim()).filter(Boolean);

            const updatePayload = {
                customer_name: formData.name,
                budget_max: formData.budget_max ? parseInt(formData.budget_max) : null,
                preferred_zones: zonesArray,
                email: formData.email
            };

            const { error } = await supabase
                .from('leads')
                .update(updatePayload)
                .eq('id', lead.id);

            if (error) throw error;
            setIsEditing(false);
        } catch (error) {
            console.error("Save error:", error);
            alert("Errore durante il salvataggio: " + error.message);
        } finally {
            setIsSaving(false);
        }
    }

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

                {/* Handoff Alert Banner */}
                {(lead.status === 'review_required' || lead.metadata?.handoff_reason) && (
                    <div className="bg-red-50 border border-red-200 rounded-3xl p-6 shadow-sm animate-in fade-in slide-in-from-top-4 duration-500">
                        <div className="flex items-start gap-4">
                            <div className="bg-red-100 p-3 rounded-2xl">
                                <AlertTriangle className="w-6 h-6 text-red-600" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold text-red-900 mb-1">Richiesta Intervento Umano</h3>
                                <div className="text-sm text-red-700 font-medium mb-3">
                                    L'AI ha disattivato la modalità automatica per questo lead.
                                </div>

                                <div className="grid grid-cols-2 gap-3 mb-4">
                                    <div className="bg-white/60 p-3 rounded-xl border border-red-100">
                                        <div className="text-[10px] uppercase font-bold text-red-400 tracking-wider mb-1">Motivo</div>
                                        <div className="text-sm font-bold text-red-900">
                                            {lead.metadata?.handoff_reason || "NON SPECIFICATO"}
                                        </div>
                                    </div>
                                    <div className="bg-white/60 p-3 rounded-xl border border-red-100">
                                        <div className="text-[10px] uppercase font-bold text-red-400 tracking-wider mb-1">Analisi AI</div>
                                        <div className="text-xs font-medium text-red-800 leading-tight">
                                            {lead.metadata?.ai_analysis || "Nessun dettaglio aggiuntivo disponibile."}
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={() => {/* TODO: Implement server-side status update to 'human_mode' or 'active' */ }}
                                    className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold shadow-lg shadow-red-200 transition-all flex items-center justify-center gap-2"
                                >
                                    <HelpingHand className="w-4 h-4" />
                                    Prendi in Carico
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Profile Picture & Identity */}
                <div className="flex flex-col items-center animate-in fade-in slide-in-from-top-4 duration-500">
                    <div className="relative group">
                        <div className="w-28 h-28 rounded-[2.5rem] bg-gradient-to-br from-gray-50 to-white flex items-center justify-center text-4xl text-[hsl(var(--zen-text-main))] font-black mb-4 shadow-xl border-4 border-white">
                            {formData.name ? formData.name[0].toUpperCase() : "?"}
                        </div>
                    </div>

                    {isEditing ? (
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="text-xl font-bold text-[hsl(var(--zen-text-main))] text-center tracking-tight border-b-2 border-[hsl(var(--zen-accent))] focus:outline-none bg-transparent w-full"
                            placeholder="Nome Lead"
                        />
                    ) : (
                        <h3 className="text-2xl font-bold text-[hsl(var(--zen-text-main))] text-center tracking-tight">{lead.name}</h3>
                    )}

                    <div className="mt-2 px-3 py-1 bg-white rounded-full border border-[hsl(var(--zen-border))] text-[10px] font-bold text-[hsl(var(--zen-text-muted))] uppercase tracking-widest flex items-center">
                        <Phone className="w-3 h-3 mr-2" />
                        {lead.phone}
                    </div>
                </div>

                {/* AI Profiling Cards */}
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
                    <h4 className="text-[10px] uppercase font-black text-[hsl(var(--zen-text-muted))] tracking-[0.2em] ml-1">AI Intelligence</h4>

                    <div className="grid grid-cols-1 gap-3">
                        <div className="grid grid-cols-2 gap-3">
                            <div className="bg-white p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-16 h-16 bg-green-50 rounded-full -mr-4 -mt-4 opacity-50"></div>
                                <div className="relative">
                                    <Wallet className="w-5 h-5 mb-2 text-[hsl(var(--zen-accent))]" />
                                    <div className="text-[9px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Budget</div>
                                    {isEditing ? (
                                        <input
                                            type="number"
                                            value={formData.budget_max}
                                            onChange={(e) => setFormData({ ...formData, budget_max: e.target.value })}
                                            className="text-lg font-black text-[hsl(var(--zen-text-main))] bg-transparent focus:outline-none border-b border-gray-100 w-full"
                                        />
                                    ) : (
                                        <div className="text-lg font-black text-[hsl(var(--zen-text-main))]">
                                            {budget !== "N/A" ? `${budget.toLocaleString()}€` : "Analisi..."}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="bg-white p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-16 h-16 bg-purple-50 rounded-full -mr-4 -mt-4 opacity-50"></div>
                                <div className="relative">
                                    <Sparkles className="w-5 h-5 mb-2 text-purple-500" />
                                    <div className="text-[9px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Qualificazione</div>
                                    <div className="flex items-baseline gap-1">
                                        <div className="text-lg font-black text-[hsl(var(--zen-text-main))]">
                                            {lead.qualification_score ? `${lead.qualification_score}/10` : "N/A"}
                                        </div>
                                        {lead.qualification_status === 'HOT' && <span className="text-xs text-orange-500 font-bold">HOT 🔥</span>}
                                    </div>
                                    <div className="text-[10px] text-[hsl(var(--zen-text-muted))] capitalize blur-none">
                                        {lead.qualification_status?.toLowerCase().replace('_', ' ') || "In Attesa"}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-sm hover:shadow-md transition-all group overflow-hidden relative">
                            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 opacity-50"></div>
                            <div className="relative">
                                <MapPin className="w-5 h-5 mb-2 text-blue-500" />
                                <div className="text-[10px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Zone di Interesse</div>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={formData.preferred_zones}
                                        onChange={(e) => setFormData({ ...formData, preferred_zones: e.target.value })}
                                        className="text-sm font-bold text-[hsl(var(--zen-text-main))] bg-transparent focus:outline-none border-b border-gray-100 w-full"
                                        placeholder="Milano, Brera, ..."
                                    />
                                ) : (
                                    <div className="text-sm font-bold text-[hsl(var(--zen-text-main))] leading-relaxed italic">
                                        {Array.isArray(zone) ? zone.join(" • ") : zone}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Market Valuation Card (New) */}
                        {marketData && (
                            <div className="bg-slate-900 p-5 rounded-3xl border border-[hsl(var(--zen-border))] shadow-md hover:shadow-lg transition-all group overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-8 -mt-8"></div>
                                <div className="relative">
                                    <TrendingUp className="w-5 h-5 mb-2 text-emerald-400" />
                                    <div className="text-[9px] text-white/60 font-bold uppercase tracking-widest mb-1">Valutazione Mercato ({marketData.zone})</div>
                                    <div className="flex items-end justify-between">
                                        <div>
                                            <div className="text-2xl font-black text-white">
                                                {marketData.average_price_sqm}€<span className="text-sm text-white/50 font-medium">/mq</span>
                                            </div>
                                            <div className="text-[10px] text-emerald-400 font-bold mt-1 bg-emerald-400/10 inline-block px-2 py-0.5 rounded-md">
                                                {marketData.trend === 'UP' ? '↗ In rialzo' : (marketData.trend === 'DOWN' ? '↘ In calo' : '→ Stabile')}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Appraisal Card (Beta) */}
                        <div className="bg-gradient-to-br from-indigo-900 to-indigo-800 p-5 rounded-3xl border border-indigo-700 shadow-md hover:shadow-lg transition-all group overflow-hidden relative">
                            <div className="relative">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <TrendingUp className="w-5 h-5 mb-1 text-indigo-300" />
                                        <div className="text-[9px] text-indigo-200 font-bold uppercase tracking-widest">Stima Immobile (Beta)</div>
                                    </div>
                                    <div className="text-[10px] bg-indigo-500/30 px-2 py-1 rounded text-white">AI Real-time</div>
                                </div>

                                {!appraisalData ? (
                                    <div className="mt-3">
                                        <div className="flex gap-2 items-center mb-3">
                                            <input
                                                type="number"
                                                value={appraisalParams.sqm}
                                                onChange={(e) => setAppraisalParams({ ...appraisalParams, sqm: e.target.value })}
                                                className="w-20 bg-black/20 text-white rounded px-2 py-1 text-sm border border-indigo-500/30 focus:border-indigo-400 outline-none"
                                                placeholder="MQ"
                                            />
                                            <span className="text-white/60 text-sm font-medium">mq a {formData.preferred_zones?.split(',')[0]}</span>
                                        </div>
                                        <button
                                            onClick={handleAppraisal}
                                            disabled={isAppraising}
                                            className="w-full py-2 bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50"
                                        >
                                            {isAppraising ? "Analisi Perplexity in corso..." : "Genera Stima"}
                                        </button>
                                    </div>
                                ) : (
                                    <div className="mt-2 animate-in fade-in">
                                        <div className="text-3xl font-black text-white mb-1">
                                            €{appraisalData.estimated_value.toLocaleString()}
                                        </div>
                                        <div className="text-xs text-indigo-200 mb-2 font-medium">
                                            Range: €{appraisalData.estimated_range_min.toLocaleString()} - €{appraisalData.estimated_range_max.toLocaleString()}
                                        </div>
                                        <div className="text-[10px] text-indigo-100/80 leading-relaxed border-t border-indigo-500/30 pt-2">
                                            {appraisalData.reasoning}
                                        </div>
                                        <button
                                            onClick={() => setAppraisalData(null)}
                                            className="mt-3 text-[10px] text-indigo-300 hover:text-white underline"
                                        >
                                            Nuova stima
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div className="bg-gray-50/50 p-4 rounded-3xl border border-[hsl(var(--zen-border))] group relative overflow-hidden">
                                <div className="relative">
                                    <ShieldCheck className="w-4 h-4 mb-2 text-emerald-500" />
                                    <div className="text-[9px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Origine</div>
                                    <div className="text-[11px] font-black text-[hsl(var(--zen-text-main))] truncate">
                                        {lead.metadata?.source?.replace('_', ' ') || "WhatsApp"}
                                    </div>
                                </div>
                            </div>
                            <div className="bg-gray-50/50 p-4 rounded-3xl border border-[hsl(var(--zen-border))] group relative overflow-hidden">
                                <div className="relative">
                                    <Zap className="w-4 h-4 mb-2 text-amber-500" />
                                    <div className="text-[9px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Intento</div>
                                    <div className="text-[11px] font-black text-[hsl(var(--zen-text-main))] truncate capitalize">
                                        {lead.metadata?.last_intent?.toLowerCase().replace('_', ' ') || "Ingaggio"}
                                    </div>
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
                            {isEditing ? (
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="text-sm font-semibold truncate bg-transparent focus:outline-none w-full"
                                    placeholder="Email"
                                />
                            ) : (
                                <span className="text-sm font-semibold truncate">{email}</span>
                            )}
                        </div>
                        <div className="flex items-center text-[hsl(var(--zen-text-main))] bg-white p-4 rounded-2xl shadow-sm border border-[hsl(var(--zen-border))]">
                            <Calendar className="w-5 h-5 mr-3 text-gray-400" />
                            <span className="text-sm font-semibold">Attivato il {created}</span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="pt-6 grid grid-cols-1 gap-3 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-450">
                    {isEditing ? (
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={handleSave}
                                disabled={isSaving}
                                className="py-4 bg-[hsl(var(--zen-accent))] text-white rounded-2xl text-sm font-bold shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center justify-center"
                            >
                                <Check className="w-4 h-4 mr-2" /> Salva
                            </button>
                            <button
                                onClick={() => setIsEditing(false)}
                                className="py-4 bg-gray-100 text-[hsl(var(--zen-text-main))] rounded-2xl text-sm font-bold hover:bg-gray-200 transition-all"
                            >
                                Annulla
                            </button>
                        </div>
                    ) : (
                        <>
                            <button
                                onClick={() => setIsEditing(true)}
                                className="w-full py-4 bg-[hsl(var(--zen-text-main))] text-white rounded-2xl text-sm font-bold shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center justify-center"
                            >
                                <Edit2 className="w-4 h-4 mr-2" /> Modifica Profilo
                            </button>
                            <button
                                onClick={handleArchive}
                                disabled={isSaving}
                                className="w-full py-4 bg-white border border-red-100 text-red-500 rounded-2xl text-sm font-bold hover:bg-red-50 transition-all"
                            >
                                Archivia Conversazione
                            </button>
                        </>
                    )}
                </div>

            </div>
        </div>
    );
}
