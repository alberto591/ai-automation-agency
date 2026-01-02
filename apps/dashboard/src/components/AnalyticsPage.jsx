import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

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

    useEffect(() => {
        fetchAnalytics()
    }, [period])

    const fetchAnalytics = async () => {
        setLoading(true)
        try {
            const [metricsRes, distributionRes, systemRes] = await Promise.all([
                fetch(`/api/analytics/qualification-metrics?days=${period}`),
                fetch(`/api/analytics/score-distribution?days=${period}`),
                fetch('/metrics')
            ])

            const metricsData = await metricsRes.json()
            const distributionData = await distributionRes.json()
            const systemText = await systemRes.text()

            setMetrics(metricsData)
            setDistribution(distributionData)

            // Parse Prometheus text
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
    const targetRate = 70 // From roadmap

    return (
        <div className="h-full overflow-y-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Lead Qualification Analytics</h1>
                    <p className="text-slate-500 mt-1">Track qualification flow performance and lead distribution</p>
                </div>

                {/* Period Selector */}
                <select
                    value={period}
                    onChange={(e) => setPeriod(Number(e.target.value))}
                    className="px-4 py-2 border border-slate-300 rounded-lg bg-white"
                >
                    <option value={7}>Last 7 days</option>
                    <option value={14}>Last 14 days</option>
                    <option value={30}>Last 30 days</option>
                    <option value={90}>Last 90 days</option>
                </select>
            </div>

            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-panel p-6 rounded-2xl">
                    <div className="text-sm text-slate-500 mb-1">Started</div>
                    <div className="text-3xl font-bold text-slate-800">{metrics?.started_count || 0}</div>
                </div>

                <div className="glass-panel p-6 rounded-2xl">
                    <div className="text-sm text-slate-500 mb-1">Completed</div>
                    <div className="text-3xl font-bold text-green-600">{metrics?.completed_count || 0}</div>
                </div>

                <div className="glass-panel p-6 rounded-2xl">
                    <div className="text-sm text-slate-500 mb-1">Completion Rate</div>
                    <div className="flex items-baseline gap-2">
                        <div className={`text-3xl font-bold ${completionRate >= targetRate ? 'text-green-600' : 'text-amber-600'}`}>
                            {completionRate.toFixed(1)}%
                        </div>
                        <div className="text-sm text-slate-400">/ {targetRate}% target</div>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl">
                    <div className="text-sm text-slate-500 mb-1">Total Leads</div>
                    <div className="text-3xl font-bold text-slate-800">{distribution?.total_leads || 0}</div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Score Distribution Pie Chart */}
                <div className="glass-panel p-6 rounded-2xl">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Lead Score Distribution</h2>
                    {distribution && (
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    )}

                    {/* Stats Below Chart */}
                    <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                        <div>
                            <div className="text-2xl font-bold text-red-600">{distribution?.hot_leads || 0}</div>
                            <div className="text-xs text-slate-500">HOT (≥9)</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-amber-600">{distribution?.warm_leads || 0}</div>
                            <div className="text-xs text-slate-500">WARM (6-8)</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-blue-600">{distribution?.cold_leads || 0}</div>
                            <div className="text-xs text-slate-500">COLD (\u003c6)</div>
                        </div>
                    </div>
                </div>

                {/* Completion Rate Progress */}
                <div className="glass-panel p-6 rounded-2xl">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Qualification Flow Health</h2>

                    <div className="space-y-6">
                        {/* Completion Rate Bar */}
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-slate-600">Completion Rate</span>
                                <span className={`font-semibold ${completionRate >= targetRate ? 'text-green-600' : 'text-amber-600'}`}>
                                    {completionRate.toFixed(1)}%
                                </span>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-500 ${completionRate >= targetRate ? 'bg-green-500' : 'bg-amber-500'}`}
                                    style={{ width: `${Math.min(completionRate, 100)}%` }}
                                ></div>
                            </div>
                            <div className="text-xs text-slate-400 mt-1">Target: {targetRate}%</div>
                        </div>

                        {/* Average Score */}
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-slate-600">Average Score</span>
                                <span className="font-semibold text-slate-800">{distribution?.avg_score.toFixed(1) || 0}/10</span>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                                <div
                                    className="h-full bg-indigo-500 transition-all duration-500"
                                    style={{ width: `${(distribution?.avg_score || 0) * 10}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Key Insights */}
                        <div className="mt-6 space-y-2">
                            <div className="text-sm font-semibold text-slate-700">Key Insights</div>
                            {completionRate >= targetRate ? (
                                <div className="text-sm text-green-700 bg-green-50 p-3 rounded-lg">
                                    ✅ Completion rate exceeds target! Flow is performing well.
                                </div>
                            ) : (
                                <div className="text-sm text-amber-700 bg-amber-50 p-3 rounded-lg">
                                    ⚠️ Completion rate below target. Consider optimizing question flow.
                                </div>
                            )}

                            {distribution && distribution.hot_leads > 0 && (
                                <div className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
                                    🔥 {distribution.hot_leads} HOT leads require immediate follow-up
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Period Info */}
            <div className="text-xs text-slate-400 text-center">
                Data from the last {period} days
            </div>

            {/* System Health Section */}
            <h2 className="text-lg font-semibold text-slate-800 mt-8 mb-4">System Health (Live)</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-8">
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-blue-500">
                    <div className="text-sm text-slate-500 mb-1">Cache Hit Rate</div>
                    <div className="text-2xl font-bold text-slate-800">
                        {systemMetrics ? (systemMetrics.cacheHitRate * 100).toFixed(1) : 0}%
                    </div>
                </div>
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-purple-500">
                    <div className="text-sm text-slate-500 mb-1">Perplexity API Calls</div>
                    <div className="text-2xl font-bold text-slate-800">
                        {systemMetrics?.apiCalls || 0}
                    </div>
                </div>
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-green-500">
                    <div className="text-sm text-slate-500 mb-1">Total Appraisals</div>
                    <div className="text-2xl font-bold text-slate-800">
                        {systemMetrics?.appraisals || 0}
                    </div>
                </div>
            </div>
        </div>
    )
}
