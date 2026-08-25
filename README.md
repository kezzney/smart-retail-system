# Smart Retail Intelligence System

An AI-Powered Smart Retail Intelligence and Decision-Support Platform combining Computer Vision, Object Detection, Customer Tracking, Inventory Analytics, Demand Forecasting, and Dynamic Pricing Recommendations.

> **Current Status (Milestone 1 — Project Foundation):**
> The project is currently in **Stage 1 (Foundation)**. The backend FastAPI architecture, database connectivity layer, frontend shell with routing, test suites, and CI workflows are established.
> ⚠️ **Note:** The AI intelligence modules (YOLO shelf monitoring, MOT customer tracking, M5 forecasting, dynamic pricing, and misplacement detection) and datasets are planned for subsequent incremental stages and are not implemented yet.

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
│       └── ci.yml              # GitHub Actions CI workflow
├── backend/
│   ├── app/
│   │   ├── api/                # API router & v1 endpoints
│   │   │   └── v1/
│   │   │       └── health.py   # /api/v1/health and /api/v1/status
│   │   ├── database/           # SQLAlchemy engine & session factory
│   │   ├── models/             # ORM entity models (Stage 2+)
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic layer
│   │   ├── config.py           # Environment configuration
│   │   └── main.py             # FastAPI entrypoint
│   ├── tests/                  # Backend unit & integration tests
│   ├── .env.example            # Backend environment template
│   └── requirements.txt        # Pinned Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI layout & module components
│   │   ├── pages/              # Module placeholder views & dashboard
│   │   ├── services/           # Centralized API client
│   │   ├── types/              # TypeScript interface definitions
│   │   ├── App.tsx             # Root router configuration
│   │   └── main.tsx            # React application entrypoint
│   ├── .env.example            # Frontend environment template
│   └── package.json            # Node.js dependencies & scripts
├── database/                   # Database migrations & schemas
├── docs/                       # Technical documentation
├── model/                      # ML model artifacts (Future stages)
├── AGENTS.md                   # Engineering rules & development principles
└── README.md                   # Project documentation
```

---

## Planned Core Modules

1. **Business Dashboard:** Executive KPIs, store health summary, revenue, and inventory metrics.
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

### 2. Backend Setup

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

4. Configure environment variables (optional for local SQLite):
   ```bash
   # Copy example template if needed
   cp .env.example .env
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000`. Interactive Swagger API docs are available at `http://localhost:8000/docs`.

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend application will be available at `http://localhost:5173`.

---

## Testing and Verification

### Run Backend Tests
From the project root:
```bash
# Run pytest with venv Python
pytest backend/tests -v
```

### Run Frontend Lint & Production Build
From the frontend directory:
```bash
cd frontend
npm run lint
npm run build
```

---

## Development Principles

This repository follows the development guidelines specified in `AGENTS.md`:
- Development progresses incrementally through distinct milestones.
- AI recommendations remain human-reviewable.
- Raw datasets are kept separate from processed data pipelines.
