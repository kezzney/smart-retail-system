import React from 'react';
import type { HealthStatus } from '../../types';

interface StatusBadgeProps {
  health: HealthStatus;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  health,
  onRefresh,
  isLoading = false,
}) => {
  const getStatusColor = () => {
    if (isLoading || health.status === 'loading') return 'bg-amber-100 text-amber-800 border-amber-300';
    if (health.status === 'ok') return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (health.status === 'degraded') return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-rose-100 text-rose-800 border-rose-300';
  };

  const getStatusDot = () => {
    if (isLoading || health.status === 'loading') return 'bg-amber-500 animate-pulse';
    if (health.status === 'ok') return 'bg-emerald-500';
    if (health.status === 'degraded') return 'bg-yellow-500';
    return 'bg-rose-500';
  };

  const getLabel = () => {
    if (isLoading || health.status === 'loading') return 'Checking Backend...';
    if (health.status === 'ok') return 'Backend Online (v' + (health.version || '0.1.0') + ')';
    if (health.status === 'degraded') return 'Backend Degraded (DB issue)';
    return 'Backend Unavailable';
  };

  return (
    <div className="flex items-center gap-2">
      <div
        className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor()}`}
        title={health.error || `DB: ${health.database || 'unknown'} | Env: ${health.environment || 'local'}`}
      >
        <span className={`w-2 h-2 rounded-full ${getStatusDot()}`} />
        <span>{getLabel()}</span>
      </div>
      {onRefresh && (
        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          className="p-1 text-xs text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors disabled:opacity-50"
          title="Refresh backend status"
        >
          ↻
        </button>
      )}
    </div>
  );
};
