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
  RestockingListResponse,
  ForecastResponse,
  ForecastCatalogResponse,
  DetectionResponse,
  ShelfAnalysisResponse,
  SampleImagesResponse,
} from '../types';


const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

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

/**
 * Fetch restocking recommendations
 */
export async function getRestockingRecommendations(limit = 50, urgency?: string): Promise<RestockingListResponse> {
  const params = new URLSearchParams();
  params.append('limit', String(limit));
  if (urgency) params.append('urgency', urgency);

  const response = await apiClient.get<RestockingListResponse>(`/api/v1/restocking/recommendations?${params.toString()}`);
  return response.data;
}

/**
 * Fetch demand forecast for a single SKU
 */
export async function getItemForecast(itemId: string, storeId = 'CA_1', horizon = 14): Promise<ForecastResponse> {
  const response = await apiClient.get<ForecastResponse>(`/api/v1/forecast/${encodeURIComponent(itemId)}?store_id=${encodeURIComponent(storeId)}&horizon=${horizon}`);
  return response.data;
}

/**
 * Fetch forecast catalog items
 */
export async function getForecastCatalog(limit = 100, category?: string): Promise<ForecastCatalogResponse> {
  const params = new URLSearchParams();
  params.append('limit', String(limit));
  if (category) params.append('category', category);

  const response = await apiClient.get<ForecastCatalogResponse>(`/api/v1/forecast?${params.toString()}`);
  return response.data;
}

/**
 * Fetch available sample shelf images
 */
export async function getVisionSamples(): Promise<SampleImagesResponse> {
  const response = await apiClient.get<SampleImagesResponse>('/api/v1/vision/samples');
  return response.data;
}

/**
 * Get direct URL to sample image
 */
export function getSampleImageUrl(sampleId: string): string {
  return `${API_BASE_URL}/api/v1/vision/samples/${encodeURIComponent(sampleId)}/image`;
}

/**
 * Run product detection and return raw bounding boxes
 */
export async function detectProducts(options: {
  file?: File;
  sampleId?: string;
  conf?: number;
  iou?: number;
}): Promise<DetectionResponse> {
  const conf = options.conf ?? 0.25;
  const iou = options.iou ?? 0.45;

  if (options.file) {
    const formData = new FormData();
    formData.append('file', options.file);
    const response = await apiClient.post<DetectionResponse>(
      `/api/v1/vision/detect?conf=${conf}&iou=${iou}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  } else if (options.sampleId) {
    const response = await apiClient.post<DetectionResponse>(
      `/api/v1/vision/detect?sample_id=${encodeURIComponent(options.sampleId)}&conf=${conf}&iou=${iou}`
    );
    return response.data;
  } else {
    throw new Error('Must provide either a file or sampleId for product detection');
  }
}

/**
 * Run shelf monitoring and stock gap analysis
 */
export async function analyzeShelf(options: {
  file?: File;
  sampleId?: string;
  conf?: number;
  iou?: number;
}): Promise<ShelfAnalysisResponse> {
  const conf = options.conf ?? 0.25;

  const iou = options.iou ?? 0.45;

  if (options.file) {
    const formData = new FormData();
    formData.append('file', options.file);
    const response = await apiClient.post<ShelfAnalysisResponse>(
      `/api/v1/vision/shelf-analysis?conf=${conf}&iou=${iou}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  } else if (options.sampleId) {
    const response = await apiClient.post<ShelfAnalysisResponse>(
      `/api/v1/vision/shelf-analysis?sample_id=${encodeURIComponent(options.sampleId)}&conf=${conf}&iou=${iou}`
    );
    return response.data;
  } else {
    throw new Error('Must provide either a file or sampleId for shelf analysis');
  }
}



