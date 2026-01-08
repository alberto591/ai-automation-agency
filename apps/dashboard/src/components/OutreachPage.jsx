import { useState, useEffect } from 'react'
import { Search, MapPin, Phone, MessageSquare, Send, CheckCircle, Clock, PlusCircle, AlertCircle } from 'lucide-react'

export default function OutreachPage() {
    const [targets, setTargets] = useState([])
    const [loading, setLoading] = useState(true)
    const [generating, setGenerating] = useState(false)
    const [sendingId, setSendingId] = useState(null)
    const [city, setCity] = useState("Milano")

    useEffect(() => {
        fetchTargets()
    }, [])

    const fetchTargets = async () => {
        setLoading(true)
        try {
            const res = await fetch(`/api/outreach/targets?city=${city}`)
            const json = await res.json()
            if (json.status === 'success') {
                setTargets(json.data)
            }
        } catch (error) {
            console.error('Failed to fetch outreach targets:', error)
        } finally {
            setLoading(false)
        }
    }

    const generateTargets = async () => {
        setGenerating(true)
        try {
            const res = await fetch('/api/outreach/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city })
            })
            const json = await res.json()
            if (json.status === 'success') {
                fetchTargets()
            }
        } catch (error) {
            console.error('Generation failed:', error)
        } finally {
            setGenerating(false)
        }
    }

    const sendOutreach = async (targetId) => {
        setSendingId(targetId)
        try {
            const res = await fetch('/api/outreach/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_id: targetId })
            })
            const json = await res.json()
            if (json.status === 'success') {
                // Update local state
                setTargets(targets.map(t =>
                    t.id === targetId ? { ...t, status: 'CONTACTED', last_contacted_at: new Date().toISOString() } : t
                ))
            }
        } catch (error) {
            console.error('Send failed:', error)
            alert("Failed to send message. Check terminal logs.")
        } finally {
            setSendingId(null)
        }
    }

    if (loading && !targets.length) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            </div>
        )
    }

    return (
        <div className="h-full overflow-y-auto p-6 space-y-6 bg-slate-50/10">
            <div className="flex justify-between items-center bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-emerald-600">B2B Outreach</h1>
                    <p className="text-slate-500 mt-1">Discover and contact potential partner agencies</p>
                </div>

                <div className="flex gap-3">
                    <div className="relative">
                        <MapPin className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
                        <input
                            type="text"
                            value={city}
                            onChange={(e) => setCity(e.target.value)}
                            className="pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500 transition-all w-32 font-bold"
                        />
                    </div>
                    <button
                        onClick={generateTargets}
                        disabled={generating}
                        className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all shadow-md shadow-indigo-100 disabled:opacity-50"
                    >
                        {generating ? <PlusCircle className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
                        Generate Leads
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {targets.map((target) => (
                    <div key={target.id} className="bg-white rounded-3xl border border-slate-100 p-6 shadow-sm hover:shadow-xl hover:shadow-indigo-50/50 transition-all group border-b-4 border-b-transparent hover:border-b-indigo-500">
                        <div className="flex justify-between items-start mb-4">
                            <div className="bg-indigo-50 p-3 rounded-2xl group-hover:scale-110 transition-transform">
                                <MessageSquare className="w-6 h-6 text-indigo-600" />
                            </div>
                            <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${target.status === 'CONTACTED' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                                }`}>
                                {target.status}
                            </div>
                        </div>

                        <h3 className="text-xl font-black text-slate-800 mb-1">{target.name}</h3>
                        <div className="flex items-center gap-2 text-slate-400 text-xs mb-4">
                            <MapPin className="w-3 h-3" />
                            {target.address || target.city}
                        </div>

                        <div className="bg-slate-50 rounded-2xl p-4 mb-6 relative group/msg">
                            <div className="text-xs font-bold text-slate-400 uppercase mb-2 flex justify-between">
                                AI Outreach Message
                                <Clock className="w-3 h-3 opacity-0 group-hover/msg:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-slate-600 leading-relaxed italic">
                                "{target.outreach_message}"
                            </p>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-slate-500 font-bold text-sm">
                                <Phone className="w-4 h-4" />
                                {target.phone}
                            </div>
                            <button
                                onClick={() => sendOutreach(target.id)}
                                disabled={target.status === 'CONTACTED' || sendingId === target.id}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-sm transition-all ${target.status === 'CONTACTED'
                                        ? 'bg-emerald-50 text-emerald-600 cursor-default'
                                        : 'bg-slate-900 hover:bg-indigo-600 text-white shadow-lg shadow-slate-200'
                                    }`}
                            >
                                {sendingId === target.id ? (
                                    <Clock className="w-4 h-4 animate-spin" />
                                ) : target.status === 'CONTACTED' ? (
                                    <CheckCircle className="w-4 h-4" />
                                ) : (
                                    <Send className="w-4 h-4" />
                                )}
                                {target.status === 'CONTACTED' ? 'Sent' : 'Send WhatsApp'}
                            </button>
                        </div>
                    </div>
                ))}

                {targets.length === 0 && !loading && (
                    <div className="col-span-full bg-white p-12 rounded-3xl border border-dashed border-slate-300 text-center space-y-4">
                        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto">
                            <AlertCircle className="w-8 h-8 text-slate-300" />
                        </div>
                        <div className="max-w-xs mx-auto">
                            <h3 className="font-bold text-slate-800">No Outreach Targets</h3>
                            <p className="text-slate-500 text-sm mt-1">Enter a city and click "Generate Leads" to find agencies to contact.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
