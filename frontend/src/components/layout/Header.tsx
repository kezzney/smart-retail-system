import React, { useState, useEffect, useCallback } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { getHealthStatus } from '../../services/api';
import type { HealthStatus } from '../../types';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus>({ status: 'loading' });
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchHealth = useCallback(async () => {
    try {
      const data = await getHealthStatus();
      setHealth(data);
    } catch {
      setHealth({ status: 'error', error: 'Failed to fetch status' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleManualRefresh = () => {
    setIsLoading(true);
    fetchHealth();
  };

  useEffect(() => {
    let isMounted = true;

    const runCheck = async () => {
      try {
        const data = await getHealthStatus();
        if (isMounted) {
          setHealth(data);
        }
      } catch {
        if (isMounted) {
          setHealth({ status: 'error', error: 'Failed to fetch status' });
        }
      }
    };

    runCheck();
    const interval = setInterval(runCheck, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      <div className="flex items-center gap-3">
        <h1 className="text-base font-semibold text-slate-800">
          Smart Retail Intelligence System
        </h1>
        <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono border border-slate-200">
          v0.1.0-foundation
        </span>
      </div>

      <div className="flex items-center gap-4">
        <StatusBadge
          health={health}
          onRefresh={handleManualRefresh}
          isLoading={isLoading}
        />
      </div>
    </header>
  );
};
