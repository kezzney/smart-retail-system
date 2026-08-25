import React from 'react';
import { NavLink } from 'react-router-dom';

interface NavItemConfig {
  name: string;
  path: string;
  stage: string;
  icon: string;
}

const navItems: NavItemConfig[] = [
  { name: 'Business Dashboard', path: '/', stage: 'Stage 3 / 8', icon: '📊' },
  { name: 'Shelf Monitoring', path: '/shelf-monitoring', stage: 'Stage 5', icon: '🛒' },
  { name: 'Customer Analytics', path: '/customer-analytics', stage: 'Stage 6', icon: '👥' },
  { name: 'Predictive Restocking', path: '/predictive-restocking', stage: 'Stage 4', icon: '📦' },
  { name: 'Dynamic Pricing', path: '/dynamic-pricing', stage: 'Stage 7', icon: '🏷️' },
  { name: 'Product Misplacement', path: '/product-misplacement', stage: 'Stage 7', icon: '🔍' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
          SR
        </div>
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-white leading-tight">
            Smart Retail
          </h2>
          <p className="text-xs text-indigo-400 font-medium">AI Intelligence Suite</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Intelligence Modules
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <div className="flex items-center gap-2.5 truncate">
              <span className="text-base">{item.icon}</span>
              <span className="truncate">{item.name}</span>
            </div>
            <span
              className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 font-mono"
            >
              {item.stage}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* System Footer Info */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="text-xs text-slate-400">
          <p className="font-medium text-slate-300">Phase: Milestone 1</p>
          <p className="text-[11px] text-slate-500 mt-0.5">Project Foundation</p>
        </div>
      </div>
    </aside>
  );
};
