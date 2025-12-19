import { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'

export function useMessages(leadId) {
    const [messages, setMessages] = useState([])
    const [status, setStatus] = useState("active") // active | human_mode
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!leadId) return

        setLoading(true)
        fetchMessages()

        // Subscribe to changes on this specific row
        const channel = supabase
            .channel(`public:lead_conversations:id=eq.${leadId}`)
            .on('postgres_changes', {
                event: 'UPDATE',
                schema: 'public',
                table: 'lead_conversations',
                filter: `id=eq.${leadId}`
            }, (payload) => {
                if (payload.new) {
                    if (payload.new.messages) setMessages(payload.new.messages)
                    if (payload.new.status) setStatus(payload.new.status)
                }
            })
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [leadId])

    async function fetchMessages() {
        try {
            const { data, error } = await supabase
                .from('lead_conversations')
                .select('messages, status')
                .eq('id', leadId)
                .single()

            if (error) throw error
            setMessages(data.messages || [])
            setStatus(data.status || "active")

        } catch (error) {
            console.error("Error fetching messages:", error)
        } finally {
            setLoading(false)
        }
    }

    return { messages, status, setStatus, loading }
}
