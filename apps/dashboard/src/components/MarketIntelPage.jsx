import { useState, useEffect } from 'react'
import { Search, TrendingUp, TrendingDown, ExternalLink, Brain, Target, BarChart3, Info } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function MarketIntelPage() {
    const [data, setData] = useState([])
    const [analysis, setAnalysis] = useState(null)
    const [loading, setLoading] = useState(true)
    const [analyzing, setAnalyzing] = useState(false)
    const [searchQuery, setSearchQuery] = useState("")
    const [city, setCity] = useState("Milano")

    useEffect(() => {
        fetchMarketData()
    }, [])

    const fetchMarketData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`/api/market/data?city=${city}`)
            const json = await res.json()
            if (json.status === 'success') {
                setData(json.data)
            }
        } catch (error) {
            console.error('Failed to fetch market data:', error)
        } finally {
            setLoading(false)
        }
    }

    const runAIAnalysis = async () => {
        setAnalyzing(true)
        try {
            const res = await fetch(`/api/market/analysis?city=${city}${searchQuery ? `&zone=${searchQuery}` : ""}`)
            const json = await res.json()
            setAnalysis(json)
        } catch (error) {
            console.error('AI Analysis failed:', error)
        } finally {
            setAnalyzing(false)
        }
    }

    const filteredData = data.filter(item =>
        (item.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.zone || "").toLowerCase().includes(searchQuery.toLowerCase())
    )

    // Prepare chart data (Price distribution)
    const prepareChartData = () => {
        if (!filteredData.length) return []
        const bins = 5
        const min = Math.min(...filteredData.map(d => d.price_per_mq))
        const max = Math.max(...filteredData.map(d => d.price_per_mq))
        const step = (max - min) / bins

        let chartData = []
        for (let i = 0; i < bins; i++) {
            const low = min + (i * step)
            const high = low + step
            const count = filteredData.filter(d => d.price_per_mq >= low && d.price_per_mq < (i === bins - 1 ? high + 1 : high)).length
            chartData.push({
                range: `€${Math.round(low / 1000)}k-€${Math.round(high / 1000)}k`,
                count,
                avg: (low + high) / 2
            })
        }
        return chartData
    }

    const chartData = prepareChartData()

    if (loading && !data.length) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            </div>
        )
    }

    return (
        <div className="h-full overflow-y-auto p-6 space-y-6 bg-slate-50/30">
            <div className="flex justify-between items-center bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">Market Intelligence</h1>
                    <p className="text-slate-500 mt-1">AI-driven property valuation and sentiment analysis</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Filter zone..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500 transition-all w-64"
                        />
                    </div>
                    <button
                        onClick={runAIAnalysis}
                        disabled={analyzing}
                        className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all shadow-md shadow-indigo-100 disabled:opacity-50"
                    >
                        {analyzing ? <Brain className="w-4 h-4 animate-pulse" /> : <Brain className="w-4 h-4" />}
                        AI Analysis
                    </button>
                </div>
            </div>

            {analysis && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-top-4 duration-500">
                    <div className="glass-panel p-6 rounded-3xl border border-indigo-100 bg-white/80 shadow-sm relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Target className="w-20 h-20 text-indigo-600" />
                        </div>
                        <div className="text-xs font-bold text-indigo-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                            <Info className="w-3 h-3" /> Sentiment
                        </div>
                        <div className={`text-2xl font-black ${analysis.sentiment === 'POSITIVO' ? 'text-emerald-600' : 'text-amber-600'}`}>
                            {analysis.sentiment}
                        </div>
                        <p className="text-sm text-slate-500 mt-2 leading-relaxed">{analysis.summary}</p>
                    </div>

                    <div className="glass-panel p-6 rounded-3xl border border-violet-100 bg-white/80 shadow-sm md:col-span-2 flex flex-col justify-center">
                        <div className="text-xs font-bold text-violet-500 uppercase tracking-widest mb-2">AI Investor Tip</div>
                        <div className="text-slate-800 font-medium leading-relaxed italic text-lg">
                            "{analysis.investor_tip}"
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-100 bg-white shadow-sm overflow-hidden">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="font-bold text-slate-800 flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-indigo-500" />
                            Distribuzione Prezzi/mq
                        </h3>
                    </div>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                <YAxis hide />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#6366f1' : '#8b5cf6'} fillOpacity={0.8} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-3xl border border-slate-100 bg-white shadow-sm flex flex-col">
                    <h3 className="font-bold text-slate-800 mb-6">Quick Stats</h3>
                    <div className="space-y-6 flex-1">
                        <div className="flex justify-between items-end border-b border-slate-50 pb-4">
                            <div>
                                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Average Price</div>
                                <div className="text-2xl font-black text-slate-800">
                                    €{Math.round(filteredData.reduce((acc, d) => acc + d.price_per_mq, 0) / filteredData.length || 0).toLocaleString()} <span className="text-sm font-normal text-slate-400">/mq</span>
                                </div>
                            </div>
                            <TrendingUp className="w-8 h-8 text-emerald-500 p-1 bg-emerald-50 rounded-lg mb-1" />
                        </div>
                        <div className="flex justify-between items-end border-b border-slate-50 pb-4">
                            <div>
                                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Total Listings</div>
                                <div className="text-2xl font-black text-slate-800">{filteredData.length}</div>
                            </div>
                        </div>
                        <div className="pt-2">
                            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Zone Liquidity</div>
                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-500 w-[65%]" />
                            </div>
                            <div className="flex justify-between mt-1 text-[10px] font-bold text-slate-400 uppercase">
                                <span>Low</span>
                                <span className="text-indigo-600">Medium</span>
                                <span>High</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="glass-panel overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Property</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Zone</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Price</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Price/mq</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredData.map((item) => (
                            <tr key={item.id} className="hover:bg-slate-50/50 transition-colors group">
                                <td className="px-6 py-4">
                                    <div className="text-sm font-bold text-slate-800 truncate max-w-xs">{item.title}</div>
                                    <div className="text-[10px] text-slate-400 mt-1">{item.sqm} m² • {item.city}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm text-slate-600 bg-slate-100 px-2 py-1 rounded-md inline-block uppercase font-bold text-[10px] tracking-tighter">{item.zone}</div>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="text-sm font-black text-slate-900">€{item.price?.toLocaleString()}</div>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="flex items-center justify-end gap-2">
                                        <span className="text-sm font-bold text-slate-800">€{item.price_per_mq?.toFixed(0)}</span>
                                        {item.price_per_mq > 4000 ? (
                                            <TrendingUp className="w-3 h-3 text-red-500" />
                                        ) : (
                                            <TrendingDown className="w-3 h-3 text-emerald-500" />
                                        )}
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <a
                                        href={item.portal_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="mx-auto w-8 h-8 flex items-center justify-center bg-slate-50 group-hover:bg-indigo-600 text-slate-400 group-hover:text-white rounded-full transition-all"
                                    >
                                        <ExternalLink className="w-4 h-4" />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
