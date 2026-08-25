/**
 * Centralized API Client Service
 */

import axios from 'axios';
import type {
  HealthStatus,
  SystemStatus,
  AnalyticsOverview,
  SalesTrendData,
  ProductList,
  StoreList,
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
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

/**
 * Fetch executive dashboard KPIs overview
 */
export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const response = await apiClient.get<AnalyticsOverview>('/api/v1/analytics/overview');
  return response.data;
}

/**
 * Fetch time-series sales trend metrics
 */
export async function getSalesTrend(limit = 60): Promise<SalesTrendData> {
  const response = await apiClient.get<SalesTrendData>(`/api/v1/analytics/sales?limit=${limit}`);
  return response.data;
}

/**
 * Fetch catalog products list with pagination and search
 */
export async function getProducts(skip = 0, limit = 20, category?: string, search?: string): Promise<ProductList> {
  const params = new URLSearchParams();
  params.append('skip', String(skip));
  params.append('limit', String(limit));
  if (category) params.append('category', category);
  if (search) params.append('search', search);

  const response = await apiClient.get<ProductList>(`/api/v1/products?${params.toString()}`);
  return response.data;
}

/**
 * Fetch stores performance summaries
 */
export async function getStores(limit = 20, sortBy = 'total_sales'): Promise<StoreList> {
  const response = await apiClient.get<StoreList>(`/api/v1/stores?limit=${limit}&sort_by=${sortBy}`);
  return response.data;
}
