/**
 * Centralized API Client Service
 */

import axios from 'axios';
import type { HealthStatus, SystemStatus } from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch backend health status
 */
export async function getHealthStatus(): Promise<HealthStatus> {
  try {
    const response = await apiClient.get<HealthStatus>('/api/v1/health');
    return response.data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      return {
        status: 'error',
        error: err.message || 'Unable to connect to backend server',
      };
    }
    return {
      status: 'error',
      error: 'Unexpected error occurred while connecting to backend',
    };
  }
}

/**
 * Fetch detailed system diagnostic status
 */
export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await apiClient.get<SystemStatus>('/api/v1/status');
  return response.data;
}
