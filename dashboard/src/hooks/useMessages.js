import { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'

const normalizeMessages = (rawMessages) => {
    const normalized = []
    if (!rawMessages) return normalized

    rawMessages.forEach(msg => {
        if (msg.role && msg.content) {
            normalized.push(msg)
        } else if (msg.user || msg.ai) {
            // Priority to user field if it's actually the user
            if (msg.user && !msg.user.includes('Anzevino AI')) {
                normalized.push({
                    role: 'user',
                    content: msg.user,
                    timestamp: msg.timestamp
                })
            }

            // Priority to ai field if it's the AI
            if (msg.ai && msg.ai.includes('Anzevino AI')) {
                normalized.push({
                    role: 'assistant',
                    content: msg.ai,
                    timestamp: msg.timestamp
                })
            }

            // Fallbacks for reversed or unusual legacy structures
            if (msg.user && msg.user.includes('Anzevino AI') && !normalized.some(n => n.content === msg.user)) {
                normalized.push({
                    role: 'assistant',
                    content: msg.user,
                    timestamp: msg.timestamp
                })
            }
            if (msg.ai && !msg.ai.includes('Anzevino AI') && !normalized.some(n => n.content === msg.ai)) {
                normalized.push({
                    role: 'user',
                    content: msg.ai,
                    timestamp: msg.timestamp
                })
            }
        }
    })
    return normalized
}

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
                    if (payload.new.messages) setMessages(normalizeMessages(payload.new.messages))
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

            setMessages(normalizeMessages(data.messages))
            setStatus(data.status || "active")

        } catch (error) {
            console.error("Error fetching messages:", error)
        } finally {
            setLoading(false)
        }
    }

    return { messages, status, setStatus, loading }
}
