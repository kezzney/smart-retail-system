# Demand Forecasting & Predictive Restocking Architecture

This document describes the design, machine learning methodology, evaluation protocol, restocking heuristics, and API specifications for the **Demand Forecasting and Predictive Restocking** module (Stage 4) of the Smart Retail System.

---

## 1. Overview & Business Objective

Predictive restocking solves two fundamental retail inventory problems:
1. **Stockouts & Lost Sales**: Preventing empty shelves on high-velocity items by forecasting demand ahead of supplier lead time.
2. **Excess Holding Costs & Shrink**: Avoiding over-purchasing slow-moving or perishable SKUs by computing dynamic safety stocks.

In alignment with **AGENTS.md Rule 18 (Human-in-the-Loop)**, all automated restocking outputs are presented as **decision-support recommendations** with transparent reasoning and explicit manager approval workflows.

---

## 2. Dataset & Sampling Pipeline

* **Primary Source**: M5 Forecasting Dataset (`sales_train_validation.csv`, `calendar.csv`, `sell_prices.csv`).
* **Subset Extraction (`m5_etl.py`)**:
  * Evaluates 30,490 raw series and extracts 48 representative high-velocity SKUs across all three retail categories: `FOODS`, `HOBBIES`, `HOUSEHOLD`.
  * Longitudinal transformation across a 365-day rolling observation window (17,520 records total).
  * Enriched with calendar signals (events, holidays, SNAP assistance days) and pricing trajectory.
  * Processed output stored cleanly at `data/processed/forecasting/m5_representative_skus.csv`.

---

## 3. Forecasting Methodology & ML Architecture

### Model Architecture
To achieve high performance on resource-constrained deployment targets (Railway/Docker) without the latency and memory overhead of deep neural networks (LSTMs/Transformers), the forecasting subsystem utilizes a **scikit-learn Linear Regression engine with rich temporal & lag feature engineering**:

| Feature Category | Features | Rationale |
|---|---|---|
| **Calendar & Seasonality** | `day_of_week`, `month`, `day_of_month`, `week_of_year` | Captures weekly shopping cycles and monthly patterns |
| **Autoregressive Lags** | `lag_7`, `lag_14` | Day-of-week seasonality (7-day and 14-day lagged actual demand) |
| **Rolling Momentum** | `rolling_7_mean`, `rolling_14_mean` | Captures short-term velocity trends and baseline drift |
| **Event Exogenous Signals** | `has_event` | Binary indicator for calendar events and holiday spikes |

### Baseline & Fallback Strategy
* **Primary Model**: `LinearRegression` with `StandardScaler` feature normalization.
* **Rolling Mean Baseline**: 14-day rolling window mean (\(\mu_{14}\)).
* **Fallback Guarantee**: If insufficient historical records exist or matrix rank issues occur, the service automatically falls back to the rolling-mean baseline without failing the API request.
* **In-Memory Caching**: Models and predictions are cached per `(item_id, store_id, horizon)` tuple on first evaluation, achieving sub-10ms response times on subsequent requests.

---

## 4. Evaluation Protocol & Metrics

Following **AGENTS.md Rule 11 (Evaluation Methodology)**:
* **Validation Split**: Out-of-sample holdout on the last 28 days of historical data for each SKU.
* **Metrics**:
  * **Mean Absolute Error (MAE)**: \(\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|\)
  * **Root Mean Squared Error (RMSE)**: \(\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}\)

---

## 5. Restocking Business Logic & Decision Rules

Recommendations are computed using standard retail inventory formulas:

### Formula
$$\text{Recommended Order Qty} = \left\lceil D_{\text{forecast}} \times L \times (1 + S) \right\rceil$$

Where:
* $D_{\text{forecast}}$: Average daily forecast demand over the next 14 days.
* $L$: Supplier lead time (default: **7 days**).
* $S$: Safety stock buffer percentage (default: **25%**).

### Urgency Classification Matrix

| Urgency Level | Trigger Condition | System Action / Recommendation |
|---|---|---|
| **CRITICAL** | $D_{\text{recent}} \ge 5$ AND $\text{Trend} \ge +20\%$ | Demand spike detected; immediate expedited reorder recommended |
| **CRITICAL** | $D_{\text{recent}} \ge 10$ | High-velocity SKU with low safe stock coverage |
| **REORDER_SOON** | $D_{\text{forecast}} \ge 3$ AND $\text{Trend} \ge +5\%$ | Rising demand trajectory; schedule reorder within current cycle |
| **REORDER_SOON** | $D_{\text{recent}} \ge 2$ AND $D_{\text{forecast}} \ge D_{\text{recent}}$ | Stable high-mover; reorder to maintain safety buffer |
| **MONITOR** | $1.0 \le D_{\text{forecast}} < 3.0$ | Low steady demand; track weekly run-rate |
| **ADEQUATE** | $D_{\text{forecast}} < 1.0$ | Minimal demand; no immediate purchase order required |

---

## 6. API Endpoints Reference

### 1. `GET /api/v1/restocking/recommendations`
Returns ranked SKU restocking recommendations with priority sorting (CRITICAL first).

* **Query Parameters**:
  * `limit` (int, default: 50): Maximum number of recommendations to return.
  * `urgency` (string, optional): Filter by urgency (`CRITICAL`, `REORDER_SOON`, `MONITOR`, `ADEQUATE`).

### 2. `GET /api/v1/forecast/{item_id}`
Returns historical demand points and future predicted demand points for a specific SKU.

* **Path Parameters**: `item_id` (e.g., `FOODS_3_090`)
* **Query Parameters**:
  * `store_id` (string, default: `CA_1`): Store identifier.
  * `horizon` (int, default: 14): Forecast horizon in days (7–28).

### 3. `GET /api/v1/forecast`
Lists all available item and store pairs in the forecasting catalog.

---

## 7. Interactive Dashboard (`/restocking`)

The frontend application provides a dedicated **Predictive Restocking** dashboard featuring:
1. **Executive KPI Cards**: Tracked SKUs, Critical Alerts, Reorder Soon count, and Total Recommended Units.
2. **Interactive Chart Visualizer**: Dual-line chart displaying 60-day historical unit sales alongside 7/14/28-day forward forecasts.
3. **Model Diagnostics Bar**: Live display of model type, validation MAE, and RMSE.
4. **Decision Support Drawer**: Explains algorithmic rationale and computes lead-time metrics.
5. **Interactive Queue Table**: Filter by urgency/category, search by SKU, and toggle manager approval status.
