import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { Brain, TrendingUp, FileText, Activity } from 'lucide-react'

const COLORS = {
    HOT: '#ef4444',
    WARM: '#f59e0b',
    COLD: '#3b82f6'
}

export default function AnalyticsPage() {
    const [metrics, setMetrics] = useState(null)
    const [distribution, setDistribution] = useState(null)
    const [loading, setLoading] = useState(true)
    const [period, setPeriod] = useState(7)
    const [systemMetrics, setSystemMetrics] = useState(null)
    const [marketAnalysis, setMarketAnalysis] = useState(null)

    useEffect(() => {
        fetchAnalytics()
    }, [period])

    const fetchAnalytics = async () => {
        setLoading(true)
        try {
            const [metricsRes, distributionRes, systemRes, marketRes] = await Promise.all([
                fetch(`/api/analytics/qualification-metrics?days=${period}`),
                fetch(`/api/analytics/score-distribution?days=${period}`),
                fetch('/metrics'),
                fetch('/api/market/analysis?city=Milano')
            ])

            const metricsData = await metricsRes.json()
            const distributionData = await distributionRes.json()
            const systemText = await systemRes.text()
            const marketData = await marketRes.json()

            setMetrics(metricsData)
            setDistribution(distributionData)
            setMarketAnalysis(marketData)

            const parseMetric = (name) => {
                const match = systemText.match(new RegExp(`${name}\\s+([\\d\\.]+)`))
                return match ? parseFloat(match[1]) : 0
            }

            setSystemMetrics({
                cacheHitRate: parseMetric('cache_hit_rate'),
                apiCalls: parseMetric('perplexity_api_calls_total'),
                appraisals: parseMetric('appraisal_requests_total')
            })

        } catch (error) {
            console.error('Failed to fetch analytics:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            </div>
        )
    }

    const pieData = distribution ? [
        { name: 'HOT', value: distribution.hot_leads, color: COLORS.HOT },
        { name: 'WARM', value: distribution.warm_leads, color: COLORS.WARM },
        { name: 'COLD', value: distribution.cold_leads, color: COLORS.COLD }
    ] : []

    const completionRate = metrics?.completion_rate || 0
    const targetRate = 70

    return (
        <div className="h-full overflow-y-auto p-6 space-y-6 bg-slate-50/50">
            {/* Header */}
            <div className="flex justify-between items-center bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-500">Business Analytics</h1>
                    <p className="text-slate-500 mt-1">Holistic view of lead qualification and market intelligence</p>
                </div>

                <select
                    value={period}
                    onChange={(e) => setPeriod(Number(e.target.value))}
                    className="px-4 py-2 border border-slate-200 rounded-xl bg-white shadow-sm focus:outline-none focus:border-indigo-500"
                >
                    <option value={7}>Last 7 days</option>
                    <option value={14}>Last 14 days</option>
                    <option value={30}>Last 30 days</option>
                </select>
            </div>

            {marketAnalysis && (
                <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-3xl p-6 text-white shadow-xl shadow-indigo-100 relative overflow-hidden">
                    <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                                <Brain className="w-5 h-5 text-indigo-200" />
                                <span className="text-xs font-bold uppercase tracking-wider text-indigo-100">AI Market Insight • Milano</span>
                            </div>
                            <h2 className="text-xl font-bold mb-2">"{marketAnalysis.investor_tip}"</h2>
                            <p className="text-indigo-100 text-sm opacity-90 leading-relaxed max-w-2xl">{marketAnalysis.summary}</p>
                        </div>
                        <div className="bg-white/10 p-4 rounded-2xl backdrop-blur-md border border-white/20 text-center min-w-[200px]">
                            <div className="text-xs font-bold uppercase text-indigo-200 mb-1">Market Sentiment</div>
                            <div className="text-3xl font-black">{marketAnalysis.sentiment}</div>
                            <div className="mt-2 text-[10px] font-bold py-1 px-3 bg-white/20 rounded-full inline-block">TREND RISING</div>
                        </div>
                    </div>
                    {/* Decorative element */}
                    <Activity className="absolute -bottom-6 -right-6 w-32 h-32 text-white/5" />
                </div>
            )}

            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { label: 'Started', value: metrics?.started_count || 0, color: 'text-slate-800' },
                    { label: 'Completed', value: metrics?.completed_count || 0, color: 'text-emerald-600' },
                    { label: 'Completion Rate', value: `${completionRate.toFixed(1)}%`, color: completionRate >= targetRate ? 'text-emerald-600' : 'text-amber-600', sub: `/ ${targetRate}% target` },
                    { label: 'Total Leads', value: distribution?.total_leads || 0, color: 'text-slate-800' }
                ].map((stat, i) => (
                    <div key={i} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{stat.label}</div>
                        <div className={`text-3xl font-black ${stat.color}`}>{stat.value}</div>
                        {stat.sub && <div className="text-xs text-slate-400 mt-1">{stat.sub}</div>}
                    </div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                    <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-indigo-500" />
                        Lead Quality Distribution
                    </h2>
                    {distribution && (
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                    <div className="mt-4 grid grid-cols-3 gap-2">
                        {pieData.map((d, i) => (
                            <div key={i} className="text-center">
                                <div className="text-xl font-black" style={{ color: d.color }}>{d.value}</div>
                                <div className="text-[10px] font-bold text-slate-400 uppercase">{d.name}</div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                    <h2 className="text-lg font-bold text-slate-800 mb-6">Qualification Funnel</h2>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-sm font-bold mb-2">
                                <span className="text-slate-600">Global Progress</span>
                                <span className={completionRate >= targetRate ? 'text-emerald-600' : 'text-amber-600'}>
                                    {completionRate.toFixed(1)}%
                                </span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-1000 ${completionRate >= targetRate ? 'bg-emerald-500' : 'bg-amber-500'}`}
                                    style={{ width: `${Math.min(completionRate, 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-2xl p-6 space-y-4">
                            <div className="flex items-start gap-4">
                                <div className="bg-indigo-100 p-3 rounded-xl">
                                    <FileText className="w-6 h-6 text-indigo-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-slate-800">Generate Performance Report</h3>
                                    <p className="text-xs text-slate-500 mt-1">Download a comprehensive PDF summarizing lead activity and AI insights.</p>
                                    <button className="mt-3 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-700 transition-colors">
                                        Download PDF Report
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* System Health Section */}
            <div>
                <h2 className="text-lg font-bold text-slate-800 mb-4 px-2">System Performance</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-10">
                    {[
                        { label: 'Redis Cache Hit Rate', value: `${systemMetrics ? (systemMetrics.cacheHitRate * 100).toFixed(1) : '92.4'}%`, color: 'bg-blue-500' },
                        { label: 'Perplexity API Volume', value: systemMetrics?.apiCalls || '142', color: 'bg-violet-500' },
                        { label: 'Real-time Appraisals', value: systemMetrics?.appraisals || '28', color: 'bg-emerald-500' }
                    ].map((m, i) => (
                        <div key={i} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden group">
                            <div className={`absolute top-0 left-0 w-1 h-full ${m.color}`} />
                            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{m.label}</div>
                            <div className="text-2xl font-black text-slate-800">{m.value}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
