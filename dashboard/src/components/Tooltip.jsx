import React, { useState } from 'react';

/**
 * Tooltip component for contextual help.
 * Shows helpful information on hover.
 */
export default function Tooltip({ children, content, position = 'top' }) {
    const [isVisible, setIsVisible] = useState(false);

    const positionClasses = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    };

    const arrowClasses = {
        top: 'top-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-slate-800',
        bottom: 'bottom-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-slate-800',
        left: 'left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-slate-800',
        right: 'right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-slate-800',
    };

    if (!content) return children;

    return (
        <div
            className="relative inline-block"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children}

            {isVisible && (
                <div
                    className={`absolute z-50 ${positionClasses[position]} animate-in fade-in zoom-in duration-200`}
                >
                    <div className="bg-slate-800 text-white text-xs font-medium px-3 py-2 rounded-lg shadow-xl whitespace-nowrap max-w-xs">
                        {content}
                        <div className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`} />
                    </div>
                </div>
            )}
        </div>
    );
}
