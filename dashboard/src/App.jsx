import { useState, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import LoginPage from './components/LoginPage'
import { supabase } from './lib/supabase'

function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedLead, setSelectedLead] = useState(null)

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
    return <LoginPage />
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50/50">
      {/* Header with AI Appraisal CTA */}
      <Header />

      {/* Main Content */}
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
    </div>
  )
}

export default App
