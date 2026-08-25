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
