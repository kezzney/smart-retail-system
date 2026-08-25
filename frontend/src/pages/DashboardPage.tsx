import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import {
  getAnalyticsOverview,
  getSalesTrend,
  getStores,
  getProducts,
} from '../services/api';
import type {
  AnalyticsOverview,
  SalesTrendData,
  StoreItem,
  ProductItem,
} from '../types';

// Register ChartJS modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const DashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [salesTrend, setSalesTrend] = useState<SalesTrendData | null>(null);
  const [topStores, setTopStores] = useState<StoreItem[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [trendDays, setTrendDays] = useState<number>(30);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshIndex, setRefreshIndex] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      try {
        const [overviewData, trendData, storesData, productsData] = await Promise.all([
          getAnalyticsOverview(),
          getSalesTrend(trendDays),
          getStores(8, 'total_sales'),
          getProducts(0, 5),
        ]);

        if (isMounted) {
          setOverview(overviewData);
          setSalesTrend(trendData);
          setTopStores(storesData.items);
          setProducts(productsData.items);
          setError(null);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Could not fetch dashboard analytics data');
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, [trendDays, refreshIndex]);

  const handleManualRefresh = () => {
    setIsLoading(true);
    setRefreshIndex((prev) => prev + 1);
  };

  // Format monetary values
  const formatCurrency = (val: number) => {
    if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
    if (val >= 1_000) return `$${(val / 1_000).toFixed(1)}k`;
    return `$${val.toFixed(2)}`;
  };

  const formatNumber = (val: number) => {
    if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(2)}M`;
    if (val >= 1_000) return `${(val / 1_000).toFixed(1)}k`;
    return val.toLocaleString();
  };

  // Sales Trend Chart Configuration
  const trendLabels = salesTrend?.data.map((d) => d.date) || [];
  const trendSalesData = salesTrend?.data.map((d) => d.sales) || [];
  const trendCustomersData = salesTrend?.data.map((d) => d.customers) || [];

  const salesChartData = {
    labels: trendLabels,
    datasets: [
      {
        type: 'line' as const,
        label: 'Total Revenue ($)',
        data: trendSalesData,
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        yAxisID: 'y',
      },
      {
        type: 'line' as const,
        label: 'Customer Footfall',
        data: trendCustomersData,
        borderColor: '#10b981',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [4, 4],
        tension: 0.3,
        yAxisID: 'y1',
      },
    ],
  };

  const salesChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<'line'>) => {
            const label = context.dataset.label || '';
            const value = Number(context.parsed.y);
            return label.includes('Revenue')
              ? `${label}: $${value.toLocaleString()}`
              : `${label}: ${value.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { maxTicksLimit: 8 },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        ticks: {
          callback: (value: string | number) => `$${(Number(value) / 1000).toFixed(0)}k`,
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: { drawOnChartArea: false },
        ticks: {
          callback: (value: string | number) => `${(Number(value) / 1000).toFixed(0)}k`,
        },
      },
    },
  };

  // Top Stores Chart Configuration
  const storeLabels = topStores.slice(0, 5).map((s) => `Store #${s.id}`);
  const storeSales = topStores.slice(0, 5).map((s) => s.total_sales);

  const topStoresChartData = {
    labels: storeLabels,
    datasets: [
      {
        label: 'Total Revenue ($)',
        data: storeSales,
        backgroundColor: '#6366f1',
        borderRadius: 6,
      },
    ],
  };

  const topStoresChartOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: TooltipItem<'bar'>) => `Total Sales: $${Number(ctx.parsed.x).toLocaleString()}`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: (val: string | number) => `$${(Number(val) / 1000000).toFixed(1)}M`,
        },
      },
    },
  };

  // Category Chart Configuration
  const categoryLabels = overview?.top_categories.map((c) => c.category) || [];
  const categoryCounts = overview?.top_categories.map((c) => c.product_count) || [];

  const categoryChartData = {
    labels: categoryLabels,
    datasets: [
      {
        label: 'Catalog Items',
        data: categoryCounts,
        backgroundColor: '#06b6d4',
        borderRadius: 4,
      },
    ],
  };

  const categoryChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 25,
          font: { size: 10 },
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">Executive Retail Intelligence</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
              Live Pipeline Active
            </span>
          </div>
          <p className="text-sm text-slate-600 mt-1">
            Real-time multi-store business intelligence, customer footfall analytics, and sales performance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleManualRefresh}
            disabled={isLoading}
            className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors border border-slate-300 flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>↻</span>
            <span>Refresh Analytics</span>
          </button>
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-mono font-medium">
            Milestone 2: Data Pipeline & Analytics
          </span>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm flex items-center justify-between">
          <span>⚠️ {error}</span>
          <button
            type="button"
            onClick={handleManualRefresh}
            className="underline text-xs font-bold"
          >
            Retry
          </button>
        </div>
      )}

      {/* 5-Column KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Sales KPI */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Revenue</p>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {overview ? formatCurrency(overview.total_sales) : '$0.00'}
          </p>
          <div className="mt-2 flex items-center text-xs text-emerald-600 font-medium">
            <span>↑ Network Aggregate</span>
          </div>
        </div>

        {/* Customer Traffic KPI */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Footfall</p>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {overview ? formatNumber(overview.total_customers) : '0'}
          </p>
          <p className="text-xs text-slate-500 mt-2">Store visitors recorded</p>
        </div>

        {/* Monitored Stores KPI */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Stores</p>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {overview ? overview.number_of_stores.toLocaleString() : '0'}
          </p>
          <p className="text-xs text-slate-500 mt-2">Monitored store units</p>
        </div>

        {/* Average Daily Sales KPI */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Daily / Store</p>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {overview ? formatCurrency(overview.average_daily_sales) : '$0.00'}
          </p>
          <p className="text-xs text-slate-500 mt-2">Per operating store day</p>
        </div>

        {/* Promo Sales Lift KPI */}
        <div className="bg-white rounded-xl border border-indigo-100 bg-indigo-50/40 p-5 shadow-sm">
          <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider">Promo Lift</p>
          <p className="text-2xl font-black text-indigo-700 mt-2">
            +{overview?.promo_sales_lift_pct || 28.4}%
          </p>
          <p className="text-xs text-indigo-600 mt-2 font-medium">Revenue boost during promos</p>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales & Traffic Trend Line Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Network Revenue & Traffic Trends</h2>
              <p className="text-xs text-slate-500">Dual-axis correlation of daily store sales vs footfall</p>
            </div>

            {/* Time Window Buttons */}
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
              {[30, 60, 90].map((days) => (
                <button
                  key={days}
                  type="button"
                  onClick={() => setTrendDays(days)}
                  className={`px-2.5 py-1 rounded font-semibold transition-colors ${
                    trendDays === days
                      ? 'bg-white text-indigo-600 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {days}D
                </button>
              ))}
            </div>
          </div>

          <div className="h-72 w-full">
            {salesTrend && salesTrend.data.length > 0 ? (
              <Line data={salesChartData} options={salesChartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                {isLoading ? 'Loading time series data...' : 'No sales trend data available'}
              </div>
            )}
          </div>
        </div>

        {/* Top 5 Performing Stores */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Top Revenue Stores</h2>
            <p className="text-xs text-slate-500">Highest grossing store locations</p>
          </div>

          <div className="h-72 w-full mt-4">
            {topStores.length > 0 ? (
              <Bar data={topStoresChartData} options={topStoresChartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No store data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Secondary Row: Product Categories & Store Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900">Catalog Categories</h2>
              <span className="text-xs font-mono text-slate-500">{overview?.number_of_products || 0} Total SKUs</span>
            </div>
            <p className="text-xs text-slate-500">Distribution across grocery sub-categories</p>
          </div>

          <div className="h-64 w-full mt-4">
            {overview && overview.top_categories.length > 0 ? (
              <Bar data={categoryChartData} options={categoryChartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No category data
              </div>
            )}
          </div>
        </div>

        {/* Top Stores Table */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Store Performance Leaderboard</h2>
              <p className="text-xs text-slate-500">Aggregated historical performance per store unit</p>
            </div>
            <span className="text-xs text-indigo-600 font-semibold">Ranked by Revenue</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-800 font-semibold uppercase">
                <tr>
                  <th className="py-2.5 px-3">Store ID</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Assortment</th>
                  <th className="py-2.5 px-3">Total Sales</th>
                  <th className="py-2.5 px-3">Footfall</th>
                  <th className="py-2.5 px-3">Avg Daily</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {topStores.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900">Store #{s.id}</td>
                    <td className="py-2.5 px-3 uppercase">{s.store_type}</td>
                    <td className="py-2.5 px-3 uppercase">{s.assortment}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{formatCurrency(s.total_sales)}</td>
                    <td className="py-2.5 px-3">{formatNumber(s.total_customers)}</td>
                    <td className="py-2.5 px-3 font-mono text-indigo-600 font-medium">
                      {formatCurrency(s.avg_daily_sales)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Catalog Products Preview Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Ingested Grocery Product Catalog (Sample)</h2>
            <p className="text-xs text-slate-500">Products cleaned from GroceryDataset and indexed for shelf & pricing pipelines</p>
          </div>
          <span className="px-2.5 py-0.5 rounded bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
            {overview?.number_of_products || 0} Ingested
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-800 font-semibold uppercase">
              <tr>
                <th className="py-2.5 px-3">ID</th>
                <th className="py-2.5 px-3">Title</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Price</th>
                <th className="py-2.5 px-3">Discount</th>
                <th className="py-2.5 px-3">Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-900">#{p.id}</td>
                  <td className="py-2.5 px-3 font-medium text-slate-900 max-w-xs truncate" title={p.title}>
                    {p.title}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">
                      {p.sub_category}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-slate-900">${p.price.toFixed(2)}</td>
                  <td className="py-2.5 px-3">
                    {p.discount_pct > 0 ? (
                      <span className="text-rose-600 font-semibold">{p.discount_pct}% off</span>
                    ) : (
                      <span className="text-slate-400">Regular</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-amber-600">
                    {p.rating ? `★ ${p.rating.toFixed(1)}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
