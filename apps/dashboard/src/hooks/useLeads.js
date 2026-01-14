import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function useLeads() {
    const [leads, setLeads] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        console.log('🔍 useLeads hook mounted')
        console.log('🔍 Supabase client exists:', !!supabase)

        // Check if supabase is initialized
        if (!supabase) {
            console.error("❌ Supabase client not initialized. Check Env Vars.")
            setLoading(false)
            return
        }

        console.log('✅ Supabase client initialized, fetching leads...')
        fetchLeads()

        // Real-time subscription
        console.log('📡 Setting up real-time subscription...')
        const channel = supabase
            .channel('public:leads')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'leads' }, (payload) => {
                console.log("🔔 Lead change received!", payload)
                fetchLeads()
            })
            .subscribe()

        console.log('✅ Real-time subscription established')

        return () => {
            console.log('🧹 Cleaning up useLeads hook')
            supabase.removeChannel(channel)
        }
    }, [])

    async function fetchLeads() {
        console.log('🚀 fetchLeads() called')
        if (!supabase) {
            console.error('❌ fetchLeads: Supabase client not available')
            return
        }

        try {
            console.log('📡 Making Supabase query to leads table...')
            const { data, error } = await supabase
                .from('leads')
                .select('*, messages(*)')
                .neq('status', 'archived')
                .order('updated_at', { ascending: false })

            console.log('📊 Supabase response:', { data, error })

            if (error) throw error

            // Format data for UI
            const formatted = data.map(l => {
                // Extract last message content safely
                let lastMsgText = "Nuova conversazione"
                if (l.messages && l.messages.length > 0) {
                    // Sort descending to get last
                    const sortedMsgs = [...l.messages].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    const last = sortedMsgs[0]
                    lastMsgText = last.content || "Media/Status update"
                } else if (l.ai_summary) {
                    lastMsgText = l.ai_summary
                }

                // Format time safely
                let timeDisplay = ""
                const timeToUse = l.updated_at || l.created_at
                if (timeToUse) {
                    const date = new Date(timeToUse)
                    timeDisplay = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }

                return {
                    id: l.id,
                    phone: l.customer_phone,
                    name: l.customer_name || l.customer_phone,
                    lastMsg: lastMsgText,
                    time: timeDisplay,
                    status: l.status || "active",
                    budget_max: l.budget_max,
                    preferred_zones: l.preferred_zones,
                    email: l.email,
                    created_at: l.created_at,
                    fullMessages: l.messages, // Keep raw messages for chat window
                    metadata: l.metadata || {}, // Handle potential metadata
                    qualification_score: l.qualification_score,
                    qualification_status: l.qualification_status, // HOT, WARM, COLD
                    qualification_data: l.qualification_data,
                    raw: l // Keep full object
                }
            })

            setLeads(formatted)
        } catch (error) {
            console.error("Error fetching leads:", error)
        } finally {
            setLoading(false)
        }
    }

    return { leads, loading }
}
