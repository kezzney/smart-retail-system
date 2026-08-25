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

export interface NavItem {
  name: string;
  path: string;
  iconName: string;
  stage: string;
  description: string;
}
