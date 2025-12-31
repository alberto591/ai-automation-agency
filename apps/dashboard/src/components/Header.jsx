import { LogOut } from 'lucide-react'
import { supabase } from '../lib/supabase'

function Header() {

    const handleLogout = async () => {
        await supabase.auth.signOut()
    }

    return (
        <header className="w-full glass-panel border-b border-white/10 px-4 md:px-6 py-3 md:py-4">
            <div className="flex items-center justify-between max-w-screen-2xl mx-auto">
                {/* Logo/Brand */}
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <svg
                            className="w-6 h-6 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                            />
                        </svg>
                    </div>
                    <div className="hidden md:block">
                        <h1 className="text-lg font-semibold text-slate-800">Anzevino AI</h1>
                        <p className="text-xs text-slate-500">Real Estate CRM</p>
                    </div>
                </div>

                {/* Right Actions */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors text-sm font-medium"
                        title="Sign Out"
                    >
                        <LogOut className="w-4 h-4" />
                        <span className="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </header>
    )
}

export default Header
