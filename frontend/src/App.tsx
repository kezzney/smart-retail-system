import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { ShelfMonitoringPage } from './pages/ShelfMonitoringPage';
import { CustomerAnalyticsPage } from './pages/CustomerAnalyticsPage';
import { PredictiveRestockingPage } from './pages/PredictiveRestockingPage';
import { DynamicPricingPage } from './pages/DynamicPricingPage';
import { ProductMisplacementPage } from './pages/ProductMisplacementPage';
import { NotFoundPage } from './pages/NotFoundPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="shelf-monitoring" element={<ShelfMonitoringPage />} />
          <Route path="customer-analytics" element={<CustomerAnalyticsPage />} />
          <Route path="predictive-restocking" element={<PredictiveRestockingPage />} />
          <Route path="dynamic-pricing" element={<DynamicPricingPage />} />
          <Route path="product-misplacement" element={<ProductMisplacementPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
