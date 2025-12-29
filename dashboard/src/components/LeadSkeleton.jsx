import React from 'react';

/**
 * Loading skeleton for lead cards in sidebar.
 * Provides visual feedback while data is loading.
 */
export default function LeadSkeleton({ count = 5 }) {
    return (
        <div className="space-y-2 p-2">
            {Array.from({ length: count }).map((_, index) => (
                <div
                    key={index}
                    className="flex items-center p-5 mx-2 rounded-3xl bg-white/30 animate-pulse"
                    style={{ animationDelay: `${index * 100}ms` }}
                >
                    {/* Avatar Skeleton */}
                    <div className="w-12 h-12 rounded-2xl bg-slate-200/80 mr-4 shrink-0" />

                    {/* Content Skeleton */}
                    <div className="flex-1 space-y-2">
                        <div className="flex justify-between items-center">
                            <div className="h-4 bg-slate-200/80 rounded-full w-32" />
                            <div className="h-3 bg-slate-200/80 rounded-full w-12" />
                        </div>
                        <div className="h-3 bg-slate-200/80 rounded-full w-48" />
                    </div>
                </div>
            ))}
        </div>
    );
}
