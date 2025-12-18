import React, { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';
import { MessageSquare, User, Clock, CheckCircle } from 'lucide-react';

function App() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);

  useEffect(() => {
    const fetchLeads = async () => {
      const { data } = await supabase.from('lead_conversations').select('*').order('created_at', { ascending: false });
      setLeads(data || []);
    };
    fetchLeads();
    
    // Real-time update: Refresh when a new lead comes in
    const subscription = supabase.channel('leads').on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'lead_conversations' }, fetchLeads).subscribe();
    return () => supabase.removeChannel(subscription);
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f0f2f5' }}>
      {/* List Panel */}
      <div style={{ width: '400px', backgroundColor: 'white', borderRight: '1px solid #ddd', overflowY: 'auto' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #eee' }}>
          <h2>Messaggi Recenti</h2>
        </div>
        {leads.map(lead => (
          <div 
            key={lead.id} 
            onClick={() => setSelectedLead(lead)}
            style={{ padding: '15px', cursor: 'pointer', borderBottom: '1px solid #fafafa', backgroundColor: selectedLead?.id === lead.id ? '#e7f3ff' : 'transparent' }}
          >
            <div style={{ fontWeight: 'bold' }}>{lead.customer_name}</div>
            <div style={{ fontSize: '0.8em', color: '#65676b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {lead.last_message}
            </div>
          </div>
        ))}
      </div>

      {/* Detail Panel */}
      <div style={{ flex: 1, padding: '40px', backgroundColor: 'white' }}>
        {selectedLead ? (
          <div>
            <h3>Dettagli di {selectedLead.customer_name}</h3>
            <div style={{ padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '10px' }}>
              <p><strong>Status:</strong> {selectedLead.status}</p>
              <p><strong>Note dell'IA:</strong> {selectedLead.ai_summary}</p>
              <hr />
              <p><strong>Ultimo Messaggio Inviato:</strong></p>
              <div style={{ backgroundColor: '#0084ff', color: 'white', padding: '10px', borderRadius: '10px', maxWidth: '80%' }}>
                {selectedLead.last_message}
              </div>
            </div>
            <button style={{ marginTop: '20px', padding: '10px 20px', backgroundColor: '#25D366', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
              Prendi il controllo (WhatsApp)
            </button>
          </div>
        ) : (
          <div style={{ textAlign: 'center', marginTop: '100px', color: '#888' }}>
            Seleziona un lead per vedere la conversazione
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
