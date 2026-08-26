/**
 * Application Type Definitions
 */

export interface HealthStatus {
  status: 'ok' | 'degraded' | 'error' | 'loading';
  version?: string;
  environment?: string;
  database?: string;
  timestamp?: string;
  error?: string;
}

export interface SystemStatus {
  service_name: string;
  status: string;
  version: string;
  environment: string;
  database_connected: boolean;
  database_type: string;
  timestamp: string;
}

export interface TopStore {
  store_id: number;
  store_type: string;
  total_sales: number;
  total_customers: number;
  avg_daily_sales: number;
}

export interface CategorySummary {
  category: string;
  product_count: number;
  avg_price: number;
  min_price: number;
  max_price: number;
}

export interface AnalyticsOverview {
  total_sales: number;
  total_customers: number;
  number_of_stores: number;
  number_of_products: number;
  average_daily_sales: number;
  active_promotions: number;
  promo_sales_lift_pct: number;
  top_performing_store: TopStore;
  top_categories: CategorySummary[];
}

export interface SalesTrendPoint {
  date: string;
  sales: number;
  customers: number;
  open_stores: number;
  promo_active: boolean;
  avg_sales_per_store: number;
}

export interface SalesTrendData {
  start_date: string;
  end_date: string;
  total_points: number;
  data: SalesTrendPoint[];
}

export interface ProductItem {
  id: number;
  title: string;
  sub_category: string;
  price: number;
  discount: string;
  discount_pct: number;
  rating: number | null;
  currency: string;
  feature: string | null;
  description: string | null;
}

export interface ProductList {
  total: number;
  skip: number;
  limit: number;
  items: ProductItem[];
}

export interface StoreItem {
  id: number;
  store_type: string;
  assortment: string;
  competition_distance: number | null;
  competition_open_year: number | null;
  promo2: number;
  total_sales: number;
  total_customers: number;
  avg_daily_sales: number;
  avg_daily_customers: number;
}

export interface StoreList {
  total: number;
  items: StoreItem[];
}

export interface ForecastPoint {
  date: string;
  actual: number | null;
  predicted: number;
}

export interface ForecastResponse {
  item_id: string;
  store_id: string;
  category: string;
  model_name: string;
  forecast_horizon_days: number;
  mae: number | null;
  rmse: number | null;
  history: ForecastPoint[];
  forecast: ForecastPoint[];
}

export type RestockUrgency = 'CRITICAL' | 'REORDER_SOON' | 'MONITOR' | 'ADEQUATE';

export interface RestockingRecommendation {
  item_id: string;
  store_id: string;
  category: string;
  avg_recent_demand: number;
  avg_forecast_demand: number;
  demand_trend_pct: number;
  recommended_reorder_qty: number;
  urgency: RestockUrgency;
  reason: string;
  forecast_horizon_days: number;
}

export interface RestockingListResponse {
  total: number;
  limit: number;
  items: RestockingRecommendation[];
}

export interface ForecastCatalogItem {
  item_id: string;
  store_id: string;
  category: string;
}

export interface ForecastCatalogResponse {
  total: number;
  items: ForecastCatalogItem[];
}

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  confidence: number;
  class_id: number;
  class_name: string;
}

export interface DetectionResponse {
  total_detections: number;
  inference_time_ms: number;
  image_width: number;
  image_height: number;
  confidence_threshold: number;
  detections: BoundingBox[];
}

export interface ShelfGap {
  shelf_row: number;
  gap_x_start: number;
  gap_x_end: number;
  gap_width: number;
  estimated_missing_units: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface ShelfAnalysisResponse {
  total_detected_products: number;
  estimated_shelf_capacity: number;
  estimated_occupancy_pct: number;
  stock_status: 'OPTIMAL' | 'MODERATE' | 'LOW_STOCK' | 'CRITICAL_STOCKOUT';
  detected_gaps: ShelfGap[];
  detections: BoundingBox[];
  inference_time_ms: number;
  image_width: number;
  image_height: number;
  disclaimer: string;
}

export interface SampleImageItem {
  sample_id: string;
  filename: string;
  split: string;
  title: string;
  description: string;
}

export interface SampleImagesResponse {
  total: number;
  samples: SampleImageItem[];
}


