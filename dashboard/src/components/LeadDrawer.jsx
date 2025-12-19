import React from 'react';
import { X, Mail, Phone, MapPin, Wallet, Calendar } from 'lucide-react';

export default function LeadDrawer({ lead, isOpen, onClose }) {
    if (!isOpen || !lead) return null;

    // Safe extraction of nested data
    // Assuming lead_data is a JSON object in the DB row
    const data = lead.lead_data || {};

    // Fallback defaults
    const budget = data.budget || lead.budget_max || "N/A";
    const zone = data.zones || data.zone || lead.preferred_zones || "N/A";
    const email = lead.email || "Non disponibile";
    const created = lead.created_at ? new Date(lead.created_at).toLocaleDateString() : "N/A";

    return (
        <div className="absolute top-0 right-0 h-full w-80 bg-white shadow-2xl border-l border-gray-200 transform transition-transform duration-300 ease-in-out z-20 flex flex-col">

            {/* Header */}
            <div className="bg-[#f0f2f5] p-4 flex justify-between items-center border-b">
                <h2 className="font-semibold text-gray-700">Info Contatto</h2>
                <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded-full">
                    <X className="w-5 h-5 text-gray-500" />
                </button>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">

                {/* Profile Picture */}
                <div className="flex flex-col items-center">
                    <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-4xl text-gray-500 font-bold mb-3 shadow-inner">
                        {lead.name ? lead.name[0].toUpperCase() : "?"}
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 text-center">{lead.name}</h3>
                    <span className="text-sm text-gray-500">{lead.phone}</span>
                </div>

                {/* Smart Tags (Extracted by AI) */}
                <div className="space-y-4">
                    <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider">AI Profiling</h4>

                    <div className="bg-green-50 p-4 rounded-xl border border-green-100 space-y-3">
                        <div className="flex items-center text-gray-700">
                            <Wallet className="w-5 h-5 mr-3 text-green-600" />
                            <div>
                                <div className="text-[10px] text-green-600 font-bold uppercase">Budget</div>
                                <div className="font-medium">{budget} €</div>
                            </div>
                        </div>

                        <div className="flex items-center text-gray-700">
                            <MapPin className="w-5 h-5 mr-3 text-green-600" />
                            <div>
                                <div className="text-[10px] text-green-600 font-bold uppercase">Zona</div>
                                <div className="font-medium">{Array.isArray(zone) ? zone.join(", ") : zone}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contact Details */}
                <div className="space-y-4">
                    <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider">Dettagli CRM</h4>

                    <div className="space-y-3">
                        <div className="flex items-center text-gray-600 bg-gray-50 p-3 rounded-lg">
                            <Mail className="w-4 h-4 mr-3" />
                            <span className="text-sm truncate">{email}</span>
                        </div>
                        <div className="flex items-center text-gray-600 bg-gray-50 p-3 rounded-lg">
                            <Calendar className="w-4 h-4 mr-3" />
                            <span className="text-sm">Creato il {created}</span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="pt-4 space-y-2">
                    <button
                        onClick={() => alert("Funzionalità in arrivo!")}
                        className="w-full py-2 bg-gray-800 text-white rounded-lg text-sm font-medium hover:bg-gray-900"
                    >
                        Modifica Note
                    </button>
                    <button
                        onClick={() => alert("Archiviato!")}
                        className="w-full py-2 bg-white border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50"
                    >
                        Archivia Lead
                    </button>
                </div>

            </div>
        </div>
    );
}
