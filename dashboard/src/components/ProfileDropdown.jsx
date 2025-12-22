import React, { useEffect, useState } from 'react';
import { User, Settings, LogOut, Building, Phone, Mail } from 'lucide-react';

export default function ProfileDropdown({ isOpen, onClose }) {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchProfile();
        }
    }, [isOpen]);

    const fetchProfile = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const data = await response.json();
                setProfile(data);
            }
        } catch (error) {
            console.error("Failed to fetch profile:", error);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 z-40 bg-transparent"
                onClick={onClose}
            />

            {/* Dropdown Menu */}
            <div className="absolute top-12 left-0 w-72 bg-white rounded-2xl shadow-2xl border border-[hsl(var(--zen-border))] z-[60] overflow-hidden animate-in fade-in zoom-in duration-200 origin-top-left">
                {/* Header */}
                <div className="p-5 bg-gradient-to-br from-gray-50 to-white border-b border-[hsl(var(--zen-border))]">
                    {loading ? (
                        <div className="flex items-center space-x-3 animate-pulse">
                            <div className="w-12 h-12 bg-gray-200 rounded-full" />
                            <div className="space-y-2">
                                <div className="h-4 w-24 bg-gray-200 rounded" />
                                <div className="h-3 w-32 bg-gray-200 rounded" />
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 rounded-2xl bg-[hsl(var(--zen-accent))] text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-[hsl(var(--zen-accent))/20]">
                                {profile?.name?.[0]?.toUpperCase() || 'A'}
                            </div>
                            <div className="min-w-0">
                                <div className="font-bold text-[hsl(var(--zen-text-main))] truncate tracking-tight">
                                    {profile?.name || "Agency Owner"}
                                </div>
                                <div className="text-xs text-[hsl(var(--zen-text-muted))] flex items-center mt-0.5">
                                    <Building className="w-3 h-3 mr-1" />
                                    {profile?.agency_name || "Anzevino AI"}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Info Content */}
                {!loading && profile && (
                    <div className="p-2 space-y-1">
                        <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Contatti</div>
                        <div className="flex items-center px-4 py-2.5 text-sm text-gray-600 rounded-xl hover:bg-gray-50 transition-colors">
                            <Mail className="w-4 h-4 mr-3 text-gray-400" />
                            <span className="truncate">{profile.email}</span>
                        </div>
                        <div className="flex items-center px-4 py-2.5 text-sm text-gray-600 rounded-xl hover:bg-gray-50 transition-colors">
                            <Phone className="w-4 h-4 mr-3 text-gray-400" />
                            <span>{profile.phone}</span>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}
