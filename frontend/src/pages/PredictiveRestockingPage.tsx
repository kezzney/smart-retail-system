/**
 * Predictive Restocking & Demand Forecasting Page
 *
 * Implements Stage 4 of the Smart Retail System:
 * - SKU-level demand forecasting using lightweight ML models
 * - Prioritized human-reviewable restocking recommendation queue
 * - Interactive historical demand + forecast visualizer
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Line } from 'react-chartjs-2';

import {
  getRestockingRecommendations,
  getItemForecast,
} from '../services/api';
import type {
  RestockingRecommendation,
  ForecastResponse,
  RestockUrgency,
} from '../types';

// Register Chart.js modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const URGENCY_CONFIG: Record<
  RestockUrgency,
  { label: string; bg: string; text: string; border: string; symbol: string }
> = {
  CRITICAL: {
    label: 'Critical',
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/30',
    symbol: '🔴',
  },
  REORDER_SOON: {
    label: 'Reorder Soon',
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    symbol: '🟡',
  },
  MONITOR: {
    label: 'Monitor',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    symbol: '🔵',
  },
  ADEQUATE: {
    label: 'Adequate',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30',
    symbol: '🟢',
  },
};

export const PredictiveRestockingPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RestockingRecommendation[]>([]);
  const [selectedItem, setSelectedItem] = useState<RestockingRecommendation | null>(null);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastHorizon, setForecastHorizon] = useState<number>(14);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshIndex, setRefreshIndex] = useState(0);

  // Filters
  const [urgencyFilter, setUrgencyFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Approved orders set (human-in-the-loop review)
  const [approvedOrders, setApprovedOrders] = useState<Set<string>>(new Set());

  // Load recommendations
  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const res = await getRestockingRecommendations(100);
        if (isMounted) {
          setRecommendations(res.items);
          if (res.items.length > 0) {
            setSelectedItem((prev) => prev ?? res.items[0]);
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : 'Failed to fetch restocking recommendations';
          setError(msg);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadData();
    return () => {
      isMounted = false;
    };
  }, [refreshIndex]);

  // Load forecast when selected item or horizon changes
  useEffect(() => {
    if (!selectedItem) return;
    let isMounted = true;

    async function loadForecast() {
      try {
        setForecastLoading(true);
        if (!selectedItem) return;
        const res = await getItemForecast(
          selectedItem.item_id,
          selectedItem.store_id,
          forecastHorizon
        );
        if (isMounted) {
          setForecastData(res);
        }
      } catch (err) {
        console.error('Failed to load forecast for item:', err);
      } finally {
        if (isMounted) setForecastLoading(false);
      }
    }

    loadForecast();
    return () => {
      isMounted = false;
    };
  }, [selectedItem, forecastHorizon]);

  // Filter recommendations
  const filteredRecs = useMemo(() => {
    return recommendations.filter((r) => {
      const matchUrgency = urgencyFilter === 'ALL' || r.urgency === urgencyFilter;
      const matchCategory = categoryFilter === 'ALL' || r.category === categoryFilter;
      const matchSearch =
        searchQuery === '' ||
        r.item_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.store_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchUrgency && matchCategory && matchSearch;
    });
  }, [recommendations, urgencyFilter, categoryFilter, searchQuery]);

  // KPI calculations
  const kpiStats = useMemo(() => {
    const total = recommendations.length;
    const critical = recommendations.filter((r) => r.urgency === 'CRITICAL').length;
    const reorderSoon = recommendations.filter((r) => r.urgency === 'REORDER_SOON').length;
    const totalUnits = recommendations.reduce((acc, r) => acc + r.recommended_reorder_qty, 0);
    return { total, critical, reorderSoon, totalUnits };
  }, [recommendations]);

  // Handle order approval (human-in-the-loop)
  const handleToggleApprove = (key: string) => {
    setApprovedOrders((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Chart configuration
  const chartData = useMemo(() => {
    if (!forecastData) {
      return { labels: [], datasets: [] };
    }

    const hist = forecastData.history || [];
    const fc = forecastData.forecast || [];

    const histLabels = hist.map((h) => h.date.slice(5)); // MM-DD
    const fcLabels = fc.map((f) => f.date.slice(5));
    const allLabels = [...histLabels, ...fcLabels];

    const actualData: (number | null)[] = [
      ...hist.map((h) => h.actual),
      ...fc.map(() => null),
    ];

    // Bridge historical last point to forecast start so line is continuous
    const bridgeVal = hist.length > 0 ? hist[hist.length - 1].actual : null;
    const forecastLineData: (number | null)[] = [
      ...hist.slice(0, -1).map(() => null),
      bridgeVal,
      ...fc.map((f) => f.predicted),
    ];

    return {
      labels: allLabels,
      datasets: [
        {
          label: 'Historical Demand (Units)',
          data: actualData,
          borderColor: '#38bdf8', // sky-400
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.2,
          fill: true,
        },
        {
          label: `Forecast (${forecastData.forecast_horizon_days}d Ahead)`,
          data: forecastLineData,
          borderColor: '#f59e0b', // amber-500
          backgroundColor: 'rgba(245, 158, 11, 0.12)',
          borderWidth: 2.5,
          borderDash: [5, 5],
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#f59e0b',
          tension: 0.2,
          fill: true,
        },
      ],
    };
  }, [forecastData]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#94a3b8',
          font: { size: 12 },
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: (item: TooltipItem<'line'>) => {
            if (item.raw === null || item.raw === undefined) return '';
            return ` ${item.dataset.label}: ${Number(item.raw).toFixed(1)} units`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#64748b', maxTicksLimit: 14, font: { size: 11 } },
      },
      y: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#64748b', font: { size: 11 } },
        title: {
          display: true,
          text: 'Daily Unit Demand',
          color: '#64748b',
          font: { size: 11 },
        },
      },
    },
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              Demand Forecasting & Predictive Restocking
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Stage 4 Active
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Machine learning demand prediction and human-reviewable restocking recommendations.
          </p>
        </div>

        <button
          onClick={() => setRefreshIndex((c) => c + 1)}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 hover:text-white transition disabled:opacity-50"
        >
          <span className={loading ? 'animate-spin inline-block' : ''}>🔄</span>
          Refresh Pipeline
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 text-lg">
            📦
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">{kpiStats.total}</div>
            <div className="text-xs text-slate-400">Tracked SKU Series</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 text-lg">
            ⚠️
          </div>
          <div>
            <div className="text-2xl font-bold text-red-400">{kpiStats.critical}</div>
            <div className="text-xs text-slate-400">Critical Restock Alerts</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 text-lg">
            ⏰
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-400">{kpiStats.reorderSoon}</div>
            <div className="text-xs text-slate-400">Reorder Soon Items</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-lg">
            📈
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-400">
              {kpiStats.totalUnits.toLocaleString()}
            </div>
            <div className="text-xs text-slate-400">Recommended Units</div>
          </div>
        </div>
      </div>

      {/* Main Content Grid: Chart (Top/Left) + Recommendations (Bottom/Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive Forecast Chart Section */}
        <div className="lg:col-span-12 xl:col-span-7 bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-700/60">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold text-slate-100">
                  {selectedItem ? `${selectedItem.item_id} @ ${selectedItem.store_id}` : 'Select a SKU to View Forecast'}
                </h2>
                {selectedItem && (
                  <span
                    className={`px-2 py-0.5 text-xs font-semibold rounded border ${
                      URGENCY_CONFIG[selectedItem.urgency].bg
                    } ${URGENCY_CONFIG[selectedItem.urgency].text} ${
                      URGENCY_CONFIG[selectedItem.urgency].border
                    }`}
                  >
                    {URGENCY_CONFIG[selectedItem.urgency].symbol} {URGENCY_CONFIG[selectedItem.urgency].label}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {selectedItem
                  ? `Category: ${selectedItem.category} • Recent Avg: ${selectedItem.avg_recent_demand} u/d • Forecast: ${selectedItem.avg_forecast_demand} u/d`
                  : 'Click on any item in the table below to load its forecast curve.'}
              </p>
            </div>

            {/* Horizon Selector */}
            <div className="flex items-center gap-1.5 bg-slate-900/60 p-1 rounded-lg border border-slate-700/60 text-xs">
              <span className="text-slate-400 text-xs px-2 font-medium">Horizon:</span>
              {[7, 14, 28].map((days) => (
                <button
                  key={days}
                  onClick={() => setForecastHorizon(days)}
                  className={`px-2.5 py-1 rounded font-medium transition ${
                    forecastHorizon === days
                      ? 'bg-amber-500 text-slate-950 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {days}d
                </button>
              ))}
            </div>
          </div>

          {/* Model Diagnostic Badge */}
          {forecastData && (
            <div className="flex flex-wrap items-center gap-4 py-2.5 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-500">Model:</span>
                <span className="font-mono text-slate-300">{forecastData.model_name}</span>
              </div>
              {forecastData.mae !== null && (
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-500">Validation MAE:</span>
                  <span className="font-mono text-amber-400">{forecastData.mae}</span>
                </div>
              )}
              {forecastData.rmse !== null && (
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-500">RMSE:</span>
                  <span className="font-mono text-amber-400">{forecastData.rmse}</span>
                </div>
              )}
              <div className="ml-auto text-[11px] text-slate-500 italic">
                Trained on M5 historical sales + calendar events
              </div>
            </div>
          )}

          {/* Chart Canvas */}
          <div className="h-72 w-full mt-2 relative">
            {forecastLoading && (
              <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center rounded-lg z-10">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <span className="animate-spin inline-block text-amber-400">🔄</span>
                  Generating Forecast...
                </div>
              </div>
            )}
            {chartData.labels.length > 0 ? (
              <Line data={chartData} options={chartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                No time-series data available.
              </div>
            )}
          </div>
        </div>

        {/* Action Panel / Restock Guidance Card */}
        <div className="lg:col-span-12 xl:col-span-5 bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60">
              <span className="text-amber-400 text-base">⚡</span>
              <h2 className="text-base font-semibold text-slate-100">Restocking Decision Support</h2>
            </div>

            {selectedItem ? (
              <div className="mt-4 space-y-4 text-sm">
                {/* Reason Explanation */}
                <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/50">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    System Reasoning
                  </div>
                  <p className="text-slate-200 text-xs leading-relaxed">{selectedItem.reason}</p>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/40">
                    <div className="text-slate-400">14-Day Recent Average</div>
                    <div className="text-lg font-bold text-slate-200 mt-1">
                      {selectedItem.avg_recent_demand}{' '}
                      <span className="text-xs font-normal text-slate-500">units/day</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/40">
                    <div className="text-slate-400">Forecast Daily Average</div>
                    <div className="text-lg font-bold text-amber-400 mt-1">
                      {selectedItem.avg_forecast_demand}{' '}
                      <span className="text-xs font-normal text-slate-500">units/day</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/40">
                    <div className="text-slate-400">Demand Trend</div>
                    <div className="flex items-center gap-1 text-base font-bold mt-1">
                      {selectedItem.demand_trend_pct >= 0 ? (
                        <span className="text-emerald-400">↑ +{selectedItem.demand_trend_pct}%</span>
                      ) : (
                        <span className="text-rose-400">↓ {selectedItem.demand_trend_pct}%</span>
                      )}
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/40">
                    <div className="text-slate-400">Recommended Order</div>
                    <div className="text-lg font-bold text-slate-100 mt-1">
                      {selectedItem.recommended_reorder_qty}{' '}
                      <span className="text-xs font-normal text-slate-500">units</span>
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 space-y-1 pt-1">
                  <div>• Calculated with 7-day supplier lead time + 25% safety stock.</div>
                  <div>• AI recommendations remain human-reviewable per store manager approval.</div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 text-sm">
                Select a SKU recommendation below to review decision metrics.
              </div>
            )}
          </div>

          {selectedItem && (
            <div className="mt-4 pt-4 border-t border-slate-700/60 flex items-center justify-between gap-3">
              <span className="text-xs text-slate-400">
                {approvedOrders.has(`${selectedItem.item_id}|${selectedItem.store_id}`)
                  ? '✓ Order approved for ERP dispatch'
                  : 'Pending manager approval'}
              </span>
              <button
                onClick={() =>
                  handleToggleApprove(`${selectedItem.item_id}|${selectedItem.store_id}`)
                }
                className={`px-4 py-2 text-xs font-semibold rounded-lg transition shadow-sm ${
                  approvedOrders.has(`${selectedItem.item_id}|${selectedItem.store_id}`)
                    ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    : 'bg-amber-500 text-slate-950 hover:bg-amber-400'
                }`}
              >
                {approvedOrders.has(`${selectedItem.item_id}|${selectedItem.store_id}`)
                  ? 'Revoke Approval'
                  : 'Approve Reorder'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations Table Section */}
      <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 space-y-4">
        {/* Filter Bar */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">⚡</span>
            <h2 className="text-base font-semibold text-slate-100">
              Restocking Recommendations Queue
            </h2>
            <span className="text-xs text-slate-400 font-normal">
              ({filteredRecs.length} of {recommendations.length} SKUs)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="🔍 Search SKU or store..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-1.5 text-xs bg-slate-900/80 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-hidden focus:border-amber-500 w-40 sm:w-48"
              />
            </div>

            {/* Urgency Filter */}
            <select
              value={urgencyFilter}
              onChange={(e) => setUrgencyFilter(e.target.value)}
              className="text-xs bg-slate-900/80 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-hidden focus:border-amber-500"
            >
              <option value="ALL">All Urgency</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="REORDER_SOON">Reorder Soon</option>
              <option value="MONITOR">Monitor</option>
              <option value="ADEQUATE">Adequate</option>
            </select>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="text-xs bg-slate-900/80 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-hidden focus:border-amber-500"
            >
              <option value="ALL">All Categories</option>
              <option value="FOODS">FOODS</option>
              <option value="HOBBIES">HOBBIES</option>
              <option value="HOUSEHOLD">HOUSEHOLD</option>
            </select>
          </div>
        </div>

        {/* Table Content */}
        {loading ? (
          <div className="py-12 flex items-center justify-center text-sm text-slate-400 gap-2">
            <span className="animate-spin inline-block text-amber-400">🔄</span>
            Loading Restocking Recommendations...
          </div>
        ) : error ? (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center justify-between">
            <span>Error: {error}</span>
            <button
              onClick={() => setRefreshIndex((c) => c + 1)}
              className="text-xs px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded"
            >
              Retry
            </button>
          </div>
        ) : filteredRecs.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No restocking recommendations match the current filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/60 border-y border-slate-700/60">
                <tr>
                  <th className="py-2.5 px-3">Urgency</th>
                  <th className="py-2.5 px-3">SKU / Item ID</th>
                  <th className="py-2.5 px-3">Store</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-right">Recent Demand</th>
                  <th className="py-2.5 px-3 text-right">Forecast Demand</th>
                  <th className="py-2.5 px-3 text-right">Trend</th>
                  <th className="py-2.5 px-3 text-right">Reorder Qty</th>
                  <th className="py-2.5 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {filteredRecs.map((r) => {
                  const key = `${r.item_id}|${r.store_id}`;
                  const isSelected =
                    selectedItem?.item_id === r.item_id && selectedItem?.store_id === r.store_id;
                  const isApproved = approvedOrders.has(key);
                  const urgencyStyle = URGENCY_CONFIG[r.urgency];

                  return (
                    <tr
                      key={key}
                      onClick={() => setSelectedItem(r)}
                      className={`cursor-pointer transition hover:bg-slate-700/40 ${
                        isSelected ? 'bg-slate-700/60 font-medium' : ''
                      }`}
                    >
                      <td className="py-3 px-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold border ${urgencyStyle.bg} ${urgencyStyle.text} ${urgencyStyle.border}`}
                        >
                          <span>{urgencyStyle.symbol}</span>
                          {urgencyStyle.label}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-200 font-medium">{r.item_id}</td>
                      <td className="py-3 px-3 font-mono text-slate-400">{r.store_id}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-700/60">
                          {r.category}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">{r.avg_recent_demand} u/d</td>
                      <td className="py-3 px-3 text-right font-medium text-amber-400">
                        {r.avg_forecast_demand} u/d
                      </td>
                      <td className="py-3 px-3 text-right">
                        <span
                          className={r.demand_trend_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}
                        >
                          {r.demand_trend_pct >= 0 ? '+' : ''}
                          {r.demand_trend_pct}%
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right font-bold text-slate-100">
                        {r.recommended_reorder_qty.toLocaleString()}
                      </td>
                      <td className="py-3 px-3 text-center whitespace-nowrap">
                        {isApproved ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
                            ✓ Approved
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-500">Pending</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
