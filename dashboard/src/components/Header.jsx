import { Sparkles } from 'lucide-react'

function Header() {
    const handleAppraisalClick = () => {
        // Open appraisal tool in new tab
        window.open('/appraisal-tool/index.html', '_blank')
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

                {/* AI Appraisal CTA Button */}
                <button
                    onClick={handleAppraisalClick}
                    className="appraisal-cta-button group relative overflow-hidden px-4 md:px-6 py-2.5 md:py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                    {/* Gradient Background */}
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 animate-gradient-x"></div>

                    {/* Shine Effect */}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-shine"></div>
                    </div>

                    {/* Button Content */}
                    <div className="relative flex items-center gap-2">
                        <Sparkles className="w-4 h-4 md:w-5 md:h-5" />
                        <span className="text-sm md:text-base">Free AI Appraisal</span>
                    </div>
                </button>
            </div>
        </header>
    )
}

export default Header
