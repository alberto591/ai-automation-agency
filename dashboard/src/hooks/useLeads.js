import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function useLeads() {
    const [leads, setLeads] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchLeads()

        // Real-time subscription
        const channel = supabase
            .channel('public:lead_conversations')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'lead_conversations' }, (payload) => {
                console.log("Change received!", payload)
                fetchLeads() // Simple re-fetch strategy for now
            })
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [])

    async function fetchLeads() {
        try {
            const { data, error } = await supabase
                .from('lead_conversations')
                .select('*')
                .neq('status', 'archived')
                .order('updated_at', { ascending: false })

            if (error) throw error

            // Format data for UI
            const formatted = data.map(l => {
                // Extract last message content safely
                let lastMsgText = "Nuova conversazione"
                if (l.messages && l.messages.length > 0) {
                    const last = l.messages[l.messages.length - 1]
                    lastMsgText = last.content || last.user || last.ai || "Media/System Message"

                    // Cleanup: if it's a legacy object, we might want to prioritize the response
                    if (!last.content && last.ai && last.user) {
                        // If both exist, the 'user' field in legacy often contained the AI's actual WhatsApp response
                        lastMsgText = last.user.includes('Anzevino AI') ? last.user : last.ai
                    }
                } else if (l.last_message) {
                    lastMsgText = l.last_message
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
