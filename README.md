# Smart Retail Intelligence System

An AI-Powered Smart Retail Intelligence and Decision-Support Platform combining Computer Vision, Object Detection, Customer Tracking, Inventory Analytics, Demand Forecasting, and Dynamic Pricing Recommendations.

> **Current Status (Milestone 2 — Data Pipeline & Business Analytics):**
> The project has completed its Foundation and Data Pipeline stages. The backend API serves live analytics from real dataset ingestion (Rossmann, Grocery, M5). The React dashboard renders executive KPIs, sales trend charts, store performance, and product catalog via live API calls.
> ⚠️ **Note:** The AI intelligence modules (YOLO shelf monitoring, MOT customer tracking, demand forecasting model training, dynamic pricing, and misplacement detection) are planned for subsequent incremental stages and are not implemented yet.

---

## Technology Stack

### Backend
- **Framework:** Python 3.12+ / FastAPI
- **Database / ORM:** SQLAlchemy 2.0+ (SQLite default for local development, PostgreSQL ready for production)
- **Validation:** Pydantic 2.0+
- **Testing:** Pytest, pytest-asyncio, HTTPX

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite 8
- **Styling:** TailwindCSS 4
- **Routing:** React Router DOM 7
- **HTTP Client:** Axios
- **Charts:** Chart.js & React-Chartjs-2

---

## Project Structure

```text
smart-retail-system/
├── .github/
│   └── workflows/
│       └── ci.yml                      # GitHub Actions CI workflow
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── health.py           # /api/v1/health and /api/v1/status
│   │   │       ├── analytics.py        # /api/v1/analytics/overview & /sales
│   │   │       ├── products.py         # /api/v1/products
│   │   │       └── stores.py           # /api/v1/stores
│   │   ├── database/                   # SQLAlchemy engine & session factory
│   │   ├── models/                     # ORM entity models
│   │   │   ├── product.py
│   │   │   ├── store.py
│   │   │   └── analytics.py
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── services/                   # Business logic & ETL pipelines
│   │   │   ├── grocery_etl.py          # Grocery catalog ingestion
│   │   │   ├── rossmann_etl.py         # Rossmann sales ingestion
│   │   │   ├── m5_etl.py               # M5 forecasting data preparation
│   │   │   ├── analytics_service.py    # KPI queries
│   │   │   └── data_manager.py         # Pipeline orchestrator
│   │   ├── config.py                   # Environment configuration
│   │   └── main.py                     # FastAPI entrypoint
│   ├── tests/                          # Backend unit & integration tests (17 tests)
│   ├── .env.example                    # Backend environment template
│   └── requirements.txt               # Pinned Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                 # Reusable UI layout components
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx       # Executive analytics dashboard
│   │   │   └── ...                     # Module placeholder pages
│   │   ├── services/api.ts             # Centralized backend API client
│   │   ├── types/index.ts              # TypeScript type definitions
│   │   ├── App.tsx                     # Root router configuration
│   │   └── main.tsx                    # React application entrypoint
│   ├── .env.example
│   └── package.json
├── data/
│   └── processed/                      # ETL output CSVs (gitkeep only — data excluded)
│       ├── inventory/
│       ├── sales/
│       ├── forecasting/
│       └── analytics/
├── AGENTS.md                           # Engineering rules & development principles
├── DATASET_AUDIT.md                    # Dataset inspection report
├── DATA_PIPELINE.md                    # ETL pipeline architecture documentation
└── README.md
```

---

## Available API Endpoints

### Infrastructure
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Service health check |
| GET | `/api/v1/status` | Full diagnostic status (DB, version, environment) |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/overview` | Executive KPIs (revenue, footfall, stores, promo lift) |
| GET | `/api/v1/analytics/sales?limit=60` | Time-series daily sales trend data |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | Paginated grocery product catalog |
| GET | `/api/v1/products?category=X&search=Y` | Filtered product search |
| GET | `/api/v1/products/{id}` | Single product detail |

### Stores
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stores` | Store performance summary list |
| GET | `/api/v1/stores?sort_by=total_sales&limit=20` | Sorted store leaderboard |
| GET | `/api/v1/stores/{id}` | Single store detail |

Interactive Swagger docs are available at `http://localhost:8000/docs`.

---

## Planned Core Modules

1. **Business Dashboard:** Executive KPIs, store health summary, revenue, and inventory metrics. ✅ **(Active)**
2. **Shelf Monitoring:** Computer vision (YOLO) detecting SKU placement, density, and out-of-stock conditions.
3. **Customer Analytics:** Multi-object tracking (MOT), footfall traffic, dwell time, and heatmap visualization.
4. **Predictive Restocking:** Demand forecasting (M5/Rossmann models) to optimize inventory replenishment.
5. **Dynamic Pricing:** Decision-support price optimization based on margins, aging, and demand elasticity.
6. **Product Misplacement:** Automated planogram compliance verification and misplaced product detection.

---

## Local Development Setup

### 1. Prerequisites
- Python 3.12+ (or 3.14)
- Node.js 20+ and npm

### 2. Dataset Configuration

The datasets live **outside** the repository to avoid committing large binary files.

Set the `SMART_RETAIL_DATA_ROOT` environment variable to the folder containing your datasets:

```bash
# Windows (PowerShell)
$env:SMART_RETAIL_DATA_ROOT = "C:\Users\CHANDAN\Downloads\SmartRetailData"

# Linux/macOS
export SMART_RETAIL_DATA_ROOT="/path/to/SmartRetailData"
```

Or create `backend/.env` from the template:
```bash
cp backend/.env.example backend/.env
# Then edit SMART_RETAIL_DATA_ROOT in backend/.env
```

Expected dataset structure inside `SMART_RETAIL_DATA_ROOT`:
```
SmartRetailData/
├── 02_M5/raw/
│   ├── sales_train_validation.csv
│   ├── calendar.csv
│   └── sell_prices.csv
├── 03_Rossmann/raw/
│   ├── train.csv
│   └── store.csv
└── 04_Grocery/raw/
    └── GroceryDataset.csv
```

### 3. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the ETL data ingestion pipeline to populate the local database:
   ```bash
   python app/services/data_manager.py
   ```
   This reads from `SMART_RETAIL_DATA_ROOT`, transforms all datasets, and seeds the SQLite database. This must be run at least once before the analytics endpoints will return data.

5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000`.

### 4. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. (Optional) Configure the API base URL by copying `.env.example`:
   ```bash
   cp .env.example .env
   # Default: VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend application will be available at `http://localhost:5173`.

---

## Testing and Verification

### Run Backend Tests
From the project root:
```bash
backend\.venv\Scripts\pytest.exe backend/tests -v
# Expected: 17 passed
```

### Run Frontend Lint & Production Build
```bash
cd frontend
npm run lint   # Expected: 0 errors
npm run build  # Expected: successful production bundle
```

---

## Development Principles

This repository follows the development guidelines specified in `AGENTS.md`:
- Development progresses incrementally through distinct milestones.
- AI recommendations remain human-reviewable.
- Raw datasets are kept **outside** the repository and are never committed.
- Processed data is generated reproducibly via ETL pipelines.
- See `DATA_PIPELINE.md` for a detailed description of all data transformations.
