import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, MapPin, Wallet, Calendar, Check, Edit2, ShieldCheck, Sparkles, Zap } from 'lucide-react';
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
        }
    }, [lead, isOpen]);

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
                                    <div className="text-[9px] text-[hsl(var(--zen-text-muted))] font-bold uppercase tracking-widest mb-1">Sentiment</div>
                                    <div className="text-sm font-bold text-[hsl(var(--zen-text-main))] capitalize">
                                        {lead.metadata?.sentiment?.sentiment?.toLowerCase() || "Neutrale"}
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
