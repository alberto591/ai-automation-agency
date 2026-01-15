import React from 'react';
import { X, Info, CheckCircle, AlertTriangle, AlertCircle as ErrorIcon } from 'lucide-react';

const Toast = ({ id, message, priority = 'low', onDismiss }) => {
    // Auto-dismiss after 5 seconds
    React.useEffect(() => {
        const timer = setTimeout(() => {
            onDismiss(id);
        }, 5000);

        return () => clearTimeout(timer);
    }, [id, onDismiss]);

    // Priority-based styling
    const priorityStyles = {
        low: {
            bg: 'bg-gray-50',
            border: 'border-gray-200',
            text: 'text-gray-800',
            icon: Info,
            iconColor: 'text-gray-500'
        },
        medium: {
            bg: 'bg-blue-50',
            border: 'border-blue-200',
            text: 'text-blue-900',
            icon: CheckCircle,
            iconColor: 'text-blue-500'
        },
        high: {
            bg: 'bg-orange-50',
            border: 'border-orange-200',
            text: 'text-orange-900',
            icon: AlertTriangle,
            iconColor: 'text-orange-500'
        },
        urgent: {
            bg: 'bg-red-50',
            border: 'border-red-200',
            text: 'text-red-900',
            icon: ErrorIcon,
            iconColor: 'text-red-500'
        }
    };

    const style = priorityStyles[priority] || priorityStyles.low;
    const Icon = style.icon;

    return (
        <div
            className={`
        ${style.bg} ${style.border} ${style.text}
        border rounded-2xl shadow-lg
        p-4 pr-12 mb-3
        min-w-[320px] max-w-md
        animate-in slide-in-from-right duration-300
        relative
      `}
        >
            <div className="flex items-start gap-3">
                <Icon className={`w-5 h-5 ${style.iconColor} flex-shrink-0 mt-0.5`} />
                <p className="text-sm font-medium leading-relaxed flex-1">{message}</p>
            </div>

            <button
                onClick={() => onDismiss(id)}
                className="absolute top-3 right-3 p-1 hover:bg-black/5 rounded-lg transition-colors"
                aria-label="Dismiss notification"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    );
};

export default Toast;
