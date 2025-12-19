import React, { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';
import { MessageSquare, User, Clock, CheckCircle, Shield, ShieldOff, Zap, Send, Phone } from 'lucide-react';
import './App.css';

function App() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchLeads = async () => {
      const { data } = await supabase.from('lead_conversations').select('*').order('updated_at', { ascending: false });
      setLeads(data || []);
      // Auto-select first lead if none selected
      if (!selectedLead && data?.length > 0) {
        setSelectedLead(data[0]);
      } else if (selectedLead) {
        // Keep selected lead updated
        const updated = data.find(l => l.id === selectedLead.id);
        if (updated) setSelectedLead(updated);
      }
    };

    fetchLeads();

    const subscription = supabase.channel('leads')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'lead_conversations' }, fetchLeads)
      .subscribe();

    return () => supabase.removeChannel(subscription);
  }, [selectedLead?.id]);

  const toggleTakeover = async (lead) => {
    const newStatus = lead.status === 'TAKEOVER' ? 'Active' : 'TAKEOVER';
    try {
      await supabase.from('lead_conversations')
        .update({ status: newStatus })
        .eq('id', lead.id);

      // Optionally call the backend resume/takeover endpoint for immediate effect
      const endpoint = newStatus === 'TAKEOVER' ? '/api/leads/takeover' : '/api/leads/resume';
      await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: lead.customer_phone })
      });
    } catch (err) {
      console.error("Failed to toggle AI mode:", err);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo-container">
            <Zap size={24} color="#0084ff" fill="#0084ff" />
            <h1>Anzevino AI</h1>
          </div>
          <div className="stats-mini">
            <span>{leads.length} LEADS</span>
          </div>
        </div>

        <div className="search-bar">
          <input type="text" placeholder="Cerca conversazione..." />
        </div>

        <div className="lead-list">
          {leads.map(lead => (
            <div
              key={lead.id}
              onClick={() => setSelectedLead(lead)}
              className={`lead-item ${selectedLead?.id === lead.id ? 'active' : ''} ${lead.status === 'TAKEOVER' ? 'takeover-active' : ''}`}
            >
              <div className="lead-avatar">
                {lead.customer_name.substring(0, 2).toUpperCase()}
              </div>
              <div className="lead-info">
                <div className="lead-top">
                  <span className="lead-name">{lead.customer_name}</span>
                  <span className="lead-time">
                    {new Date(lead.updated_at || lead.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="lead-preview">
                  {lead.status === 'TAKEOVER' && <Shield size={12} className="takeover-icon" />}
                  {lead.last_message || "Nessun messaggio"}
                </div>
              </div>
              {lead.status === 'HOT' && <div className="hot-indicator"></div>}
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        {selectedLead ? (
          <>
            <div className="chat-header">
              <div className="user-details">
                <div className="lead-avatar header-avatar">
                  {selectedLead.customer_name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h3>{selectedLead.customer_name}</h3>
                  <span className="status-text">
                    {selectedLead.status === 'TAKEOVER' ? '🤖 AI in pausa - Sei in controllo' : '✨ AI Attiva'}
                  </span>
                </div>
              </div>

              <div className="header-actions">
                <button
                  className={`action-btn ${selectedLead.status === 'TAKEOVER' ? 'resume' : 'takeover'}`}
                  onClick={() => toggleTakeover(selectedLead)}
                >
                  {selectedLead.status === 'TAKEOVER' ? <ShieldOff size={18} /> : <Shield size={18} />}
                  {selectedLead.status === 'TAKEOVER' ? 'Riattiva AI' : 'Metti in Pausa AI'}
                </button>
                <button className="icon-btn"><Phone size={20} /></button>
              </div>
            </div>

            <div className="chat-body">
              {/* If no history array yet, fallback to last message */}
              {(!selectedLead.messages || selectedLead.messages.length === 0) ? (
                <div className="msg-bubble system">Inizio della conversazione</div>
              ) : (
                selectedLead.messages.map((msg, idx) => (
                  <React.Fragment key={idx}>
                    <div className="msg-bubble user">
                      <p>{msg.user}</p>
                      <span className="time">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <div className="msg-bubble ai">
                      <p>{msg.ai}</p>
                      <span className="time">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </React.Fragment>
                ))
              )}
            </div>

            <div className="chat-footer">
              <input type="text" placeholder="Scrivi un messaggio manualmente..." />
              <button className="send-btn"><Send size={20} /></button>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <Zap size={64} color="#e1e1e1" />
            <p>Seleziona un lead per iniziare</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
