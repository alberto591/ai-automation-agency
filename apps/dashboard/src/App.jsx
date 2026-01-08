import { useState, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import AnalyticsPage from './components/AnalyticsPage'
import MarketIntelPage from './components/MarketIntelPage'
import OutreachPage from './components/OutreachPage'
import LoginPage from './components/LoginPage'
import { supabase } from './lib/supabase'
import { BarChart3, MessageSquare, Globe, Users } from 'lucide-react'

function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedLead, setSelectedLead] = useState(null)
  const [currentView, setCurrentView] = useState('inbox') // 'inbox' or 'analytics'

  useEffect(() => {
    // 1. Get initial session
    if (!supabase) {
      setLoading(false);
      return;
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    // 2. Listen for changes (login, logout, auto-refresh)
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!session) {
    // Redirect to landing page login if not authenticated
    window.location.href = '/login.html';
    return null;
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50/50">
      {/* Header with AI Appraisal CTA */}
      <Header />

      {/* Tab Navigation */}
      <div className="px-4 md:px-6 pt-4">
        <div className="flex gap-2 border-b border-slate-200">
          <button
            onClick={() => setCurrentView('inbox')}
            className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors border-b-2 -mb-px ${currentView === 'inbox'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
          >
            <MessageSquare className="w-4 h-4" />
            Inbox
          </button>
          <button
            onClick={() => setCurrentView('analytics')}
            className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors border-b-2 -mb-px ${currentView === 'analytics'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
          >
            <BarChart3 className="w-4 h-4" />
            Analytics
          </button>
          <button
            onClick={() => setCurrentView('market')}
            className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors border-b-2 -mb-px ${currentView === 'market'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
          >
            <Globe className="w-4 h-4" />
            Market Intel
          </button>
          <button
            onClick={() => setCurrentView('outreach')}
            className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors border-b-2 -mb-px ${currentView === 'outreach'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
          >
            <Users className="w-4 h-4" />
            Outreach
          </button>
        </div>
      </div>

      {/* Main Content */}
      {currentView === 'inbox' ? (
        <div className="flex flex-1 p-0 md:p-4 gap-4 overflow-hidden">
          {/* Sidebar: 30% on large screens, hidden on mobile if chat open */}
          <div className={`w-full md:w-[350px] lg:w-[400px] h-full glass-panel rounded-none md:rounded-3xl overflow-hidden transition-all duration-500 ${selectedLead ? 'hidden md:block' : 'block'}`}>
            <Sidebar selectedLead={selectedLead} setSelectedLead={setSelectedLead} />
          </div>

          {/* Chat Window: rest of space */}
          <div className={`flex-1 h-full glass-panel rounded-none md:rounded-3xl overflow-hidden transition-all duration-500 ${selectedLead ? 'block' : 'hidden md:block'}`}>
            <ChatWindow selectedLead={selectedLead} />
          </div>
        </div>
      ) : currentView === 'analytics' ? (
        <div className="flex-1 overflow-hidden p-0 md:p-4">
          <div className="h-full glass-panel rounded-none md:rounded-3xl overflow-hidden">
            <AnalyticsPage />
          </div>
        </div>
      ) : currentView === 'market' ? (
        <div className="flex-1 overflow-hidden p-0 md:p-4">
          <div className="h-full glass-panel rounded-none md:rounded-3xl overflow-hidden">
            <MarketIntelPage />
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden p-0 md:p-4">
          <div className="h-full glass-panel rounded-none md:rounded-3xl overflow-hidden">
            <OutreachPage />
          </div>
        </div>
      )}
    </div>
  )
}

export default App
