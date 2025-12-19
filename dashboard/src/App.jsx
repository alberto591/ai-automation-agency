import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'

function App() {
  const [selectedLead, setSelectedLead] = useState(null)

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar: 30% on large screens, hidden on mobile if chat open */}
      <div className={`w-full md:w-[30%] h-full border-r ${selectedLead ? 'hidden md:block' : 'block'}`}>
        <Sidebar selectedLead={selectedLead} setSelectedLead={setSelectedLead} />
      </div>

      {/* Chat Window: 70% on large screens, full on mobile if chat open */}
      <div className={`w-full md:w-[70%] h-full ${selectedLead ? 'block' : 'hidden md:block'}`}>
        <ChatWindow selectedLead={selectedLead} />
      </div>
    </div>
  )
}

export default App
