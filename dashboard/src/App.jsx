import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'

function App() {
  const [selectedLead, setSelectedLead] = useState(null)

  return (
    <div className="flex h-screen bg-slate-50/50 p-0 md:p-4 gap-4 overflow-hidden">
      {/* Sidebar: 30% on large screens, hidden on mobile if chat open */}
      <div className={`w-full md:w-[350px] lg:w-[400px] h-full glass-panel rounded-none md:rounded-3xl overflow-hidden transition-all duration-500 ${selectedLead ? 'hidden md:block' : 'block'}`}>
        <Sidebar selectedLead={selectedLead} setSelectedLead={setSelectedLead} />
      </div>

      {/* Chat Window: rest of space */}
      <div className={`flex-1 h-full glass-panel rounded-none md:rounded-3xl overflow-hidden transition-all duration-500 ${selectedLead ? 'block' : 'hidden md:block'}`}>
        <ChatWindow selectedLead={selectedLead} />
      </div>
    </div>
  )
}

export default App
