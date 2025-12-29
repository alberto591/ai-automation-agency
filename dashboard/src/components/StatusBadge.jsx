import React from 'react';
import { Circle, CheckCircle2, Clock, Calendar, XCircle } from 'lucide-react';

/**
 * Status badge component for lead statuses.
 * Shows visual indicators for different lead states.
 */
export default function StatusBadge({ status, size = 'md' }) {
    const statusConfig = {
        new: {
            label: 'Nuovo',
            icon: Circle,
            color: 'bg-blue-100 text-blue-700 border-blue-200',
            dotColor: 'bg-blue-500',
        },
        active: {
            label: 'Attivo',
            icon: Circle,
            color: 'bg-green-100 text-green-700 border-green-200',
            dotColor: 'bg-green-500',
            pulse: true,
        },
        qualified: {
            label: 'Qualificato',
            icon: CheckCircle2,
            color: 'bg-emerald-100 text-emerald-700 border-emerald-200',
            dotColor: 'bg-emerald-500',
        },
        scheduled: {
            label: 'Appuntamento',
            icon: Calendar,
            color: 'bg-purple-100 text-purple-700 border-purple-200',
            dotColor: 'bg-purple-500',
        },
        human_mode: {
            label: 'Manuale',
            icon: Circle,
            color: 'bg-orange-100 text-orange-700 border-orange-200',
            dotColor: 'bg-orange-500',
            pulse: true,
        },
        closed: {
            label: 'Chiuso',
            icon: XCircle,
            color: 'bg-slate-100 text-slate-700 border-slate-200',
            dotColor: 'bg-slate-500',
        },
    };

    const config = statusConfig[status] || statusConfig.new;
    const Icon = config.icon;

    const sizeClasses = {
        sm: 'text-[10px] px-2 py-1 gap-1',
        md: 'text-xs px-3 py-1.5 gap-1.5',
        lg: 'text-sm px-4 py-2 gap-2',
    };

    return (
        <div
            className={`inline-flex items-center rounded-full font-semibold uppercase tracking-wide border ${config.color} ${sizeClasses[size]} transition-all duration-300 hover:scale-105`}
        >
            <span className="relative flex h-2 w-2">
                {config.pulse && (
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.dotColor} opacity-75`} />
                )}
                <span className={`relative inline-flex rounded-full h-2 w-2 ${config.dotColor}`} />
            </span>
            <span>{config.label}</span>
        </div>
    );
}
