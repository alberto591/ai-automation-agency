import React, { useEffect, useState } from 'react';
import { User, Settings, LogOut, Building, Phone, Mail } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function ProfileDropdown({ isOpen, onClose }) {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!isOpen) return;

        setLoading(true);

        async function fetchProfile() {
            try {
                const { data: { user } } = await supabase.auth.getUser();
                if (!user) return;

                const { data, error } = await supabase
                    .from('user_profiles')
                    .select('*')
                    .eq('id', user.id)
                    .single();

                if (error) {
                    console.error("Failed to fetch profile:", error);
                } else {
                    setProfile({
                        ...data,
                        name: user.email.split('@')[0], // Fallback name
                        email: user.email
                    });
                }
            } catch (error) {
                console.error("Error fetching profile", error);
            } finally {
                setLoading(false);
            }
        }

        fetchProfile();
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 z-40 bg-transparent"
                onClick={onClose}
            />

            {/* Dropdown Menu */}
            <div className="absolute top-14 left-0 w-80 glass-panel rounded-3xl z-[60] overflow-hidden animate-in fade-in zoom-in duration-300 origin-top-left">
                <div className="p-6 bg-white/50">
                    {loading ? (
                        <div className="flex items-center space-x-4 animate-pulse">
                            <div className="w-14 h-14 bg-slate-200 rounded-2xl" />
                            <div className="space-y-2">
                                <div className="h-4 w-28 bg-slate-200 rounded" />
                                <div className="h-3 w-36 bg-slate-200 rounded" />
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center space-x-5">
                            <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-2xl shadow-lg shadow-indigo-500/20">
                                {profile?.name?.[0]?.toUpperCase() || 'A'}
                            </div>
                            <div className="min-w-0">
                                <div className="font-bold text-slate-800 text-lg truncate tracking-tight py-1">
                                    {profile?.name || "Agency Owner"}
                                </div>
                                <div className="text-[11px] font-bold text-slate-400 flex items-center uppercase tracking-wider">
                                    <Building className="w-3.5 h-3.5 mr-1.5 text-indigo-500/60" />
                                    {profile?.agency_name || "Anzevino AI"}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Info Content */}
                {!loading && profile && (
                    <div className="p-4 space-y-1 bg-white/30 backdrop-blur-md">
                        <div className="px-3 py-2 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Contatti</div>
                        <div className="flex items-center px-4 py-3 text-sm text-slate-600 rounded-2xl hover:bg-white/50 transition-colors">
                            <Mail className="w-4 h-4 mr-3 text-indigo-500/50" />
                            <span className="truncate font-medium">{profile.email}</span>
                        </div>
                        <div className="flex items-center px-4 py-3 text-sm text-slate-600 rounded-2xl hover:bg-white/50 transition-colors">
                            <Phone className="w-4 h-4 mr-3 text-indigo-500/50" />
                            <span className="font-medium">{profile.phone}</span>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}
