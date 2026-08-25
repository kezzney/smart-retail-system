import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getSystemStatus } from '../services/api';
import type { SystemStatus } from '../types';

export const DashboardPage: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    getSystemStatus()
      .then((data) => {
        if (isMounted) {
          setStatus(data);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Could not connect to backend');
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const modules = [
    {
      name: 'Shelf Monitoring',
      path: '/shelf-monitoring',
      stage: 'Stage 5',
      icon: '🛒',
      desc: 'Real-time SKU detection and stock level tracking.',
    },
    {
      name: 'Customer Analytics',
      path: '/customer-analytics',
      stage: 'Stage 6',
      icon: '👥',
      desc: 'Footfall traffic, heatmaps, and dwell time analysis.',
    },
    {
      name: 'Predictive Restocking',
      path: '/predictive-restocking',
      stage: 'Stage 4',
      icon: '📦',
      desc: 'Demand forecasting to prevent stockouts and waste.',
    },
    {
      name: 'Dynamic Pricing',
      path: '/dynamic-pricing',
      stage: 'Stage 7',
      icon: '🏷️',
      desc: 'Margin optimization and rule-based pricing suggestions.',
    },
    {
      name: 'Product Misplacement',
      path: '/product-misplacement',
      stage: 'Stage 7',
      icon: '🔍',
      desc: 'Detects out-of-place goods on retail planograms.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Smart Retail Intelligence System
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              AI-powered retail intelligence and decision-support platform.
            </p>
          </div>
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full text-xs font-semibold">
            Milestone 1: Project Foundation
          </span>
        </div>
      </div>

      {/* System Diagnostic Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Backend Service
          </p>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-lg font-bold text-slate-900">
              {status ? status.service_name : 'FastAPI Server'}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-semibold ${
                status?.status === 'ok'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              {status?.status || (error ? 'Offline' : 'Connecting')}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Environment: <span className="font-mono text-slate-700">{status?.environment || 'development'}</span>
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Database Engine
          </p>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-lg font-bold text-slate-900">
              {status?.database_type ? status.database_type.toUpperCase() : 'SQLite (Local)'}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-semibold ${
                status?.database_connected
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-rose-100 text-rose-800'
              }`}
            >
              {status?.database_connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Configurable for PostgreSQL via <span className="font-mono text-slate-700">DATABASE_URL</span>
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Current Stage
          </p>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-lg font-bold text-slate-900">Stage 1 — Foundation</span>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">
              Active
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            AI modules will be developed incrementally.
          </p>
        </div>
      </div>

      {/* Modules Overview Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900">Core Planned Intelligence Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {modules.map((mod) => (
            <Link
              key={mod.path}
              to={mod.path}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-indigo-300 hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">{mod.icon}</span>
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-xs font-mono font-medium">
                    {mod.stage}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                  {mod.name}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {mod.desc}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-indigo-600 font-medium">
                <span>View Specification</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
