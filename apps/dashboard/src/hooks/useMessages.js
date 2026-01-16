import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

const _normalizeMessages = (rawMessages) => {
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

        async function fetchLeadStatus() {
            const { data } = await supabase.from('leads').select('status').eq('id', leadId).single()
            if (data) setStatus(data.status || "active")
        }

        async function fetchMessages() {
            try {
                const { data, error } = await supabase
                    .from('messages')
                    .select('*')
                    .eq('lead_id', leadId)
                    .order('created_at', { ascending: true })

                if (error) throw error
                setMessages(data)

            } catch (error) {
                console.error("Error fetching messages:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchMessages()
        fetchLeadStatus()

        // Real-time updates are now handled via Backend WebSocket in parent component

        return () => {
            // Cleanup if needed
        }
    }, [leadId])

    return { messages, setMessages, status, setStatus, loading }
}
