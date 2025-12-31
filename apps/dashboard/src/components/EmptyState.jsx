import React from 'react';
import { MessageSquare, Sparkles, Search } from 'lucide-react';

/**
 * Empty state component with different variants.
 * Shows helpful messages when there's no data to display.
 */
export default function EmptyState({ variant = 'no-leads', searchQuery = '' }) {
    const variants = {
        'no-leads': {
            icon: MessageSquare,
            title: 'Nessuna conversazione',
            description: 'Le tue conversazioni con i lead appariranno qui. Inizia creando un nuovo lead.',
            gradient: 'from-indigo-500 to-purple-600',
        },
        'no-results': {
            icon: Search,
            title: 'Nessun risultato',
            description: `Nessun lead trovato per "${searchQuery}". Prova con un altro termine di ricerca.`,
            gradient: 'from-slate-500 to-slate-600',
        },
        'no-messages': {
            icon: Sparkles,
            title: 'Inizia la conversazione',
            description: 'Invia il primo messaggio per iniziare la conversazione con questo lead.',
            gradient: 'from-emerald-500 to-teal-600',
        },
    };

    const config = variants[variant] || variants['no-leads'];
    const Icon = config.icon;

    return (
        <div className="flex items-center justify-center h-full p-8">
            <div className="text-center space-y-6 max-w-sm animate-in fade-in zoom-in duration-700">
                {/* Icon */}
                <div className={`w-20 h-20 bg-gradient-to-br ${config.gradient} rounded-3xl flex items-center justify-center mx-auto shadow-xl shadow-${config.gradient.split(' ')[1]}/20 animate-float`}>
                    <Icon className="w-10 h-10 text-white" />
                </div>

                {/* Text */}
                <div className="space-y-3">
                    <h3 className="text-2xl font-bold text-slate-800 tracking-tight">
                        {config.title}
                    </h3>
                    <p className="text-slate-500 text-sm leading-relaxed">
                        {config.description}
                    </p>
                </div>

                {/* Optional Action */}
                {variant === 'no-leads' && (
                    <button className="mt-4 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold text-sm shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300">
                        Crea Nuovo Lead
                    </button>
                )}
            </div>
        </div>
    );
}
