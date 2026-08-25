# Smart Retail System — Agent Instructions

## 1. Project

This repository contains an AI-Powered Smart Retail Intelligence System.

The project combines:

* Computer Vision
* Object Detection
* Customer Tracking
* Inventory Analytics
* Demand Forecasting
* Pricing Recommendations
* Product Misplacement Detection
* Business Intelligence
* Interactive Dashboard

The project proposal defines six core modules:

1. Shelf Monitoring
2. Customer Heatmap
3. Predictive Restocking
4. Dynamic Pricing
5. Product Misplacement Detection
6. Business Dashboard

---

## 2. Existing Technology Stack

### Frontend

* React
* TypeScript
* Vite

### Backend

* Python
* FastAPI
* SQLAlchemy

### Database

* PostgreSQL for the production architecture
* SQLite may be used for lightweight local development when appropriate

### Computer Vision

* OpenCV
* YOLO

### Data / Machine Learning

* Pandas
* NumPy
* scikit-learn
* TensorFlow when justified by the specific model

### Deployment

* Frontend: Vercel
* Backend: Railway

### CI/CD

* GitHub Actions

---

## 3. Important Development Principle

Do NOT attempt to build the entire project at once.

Implement the project incrementally through clearly defined milestones.

Only work on the milestone explicitly requested by the user.

Do not implement future modules unless explicitly instructed.

---

## 4. Agent Behaviour

Before implementing a significant feature:

1. Inspect the existing repository.
2. Understand the existing architecture.
3. Identify files that will be affected.
4. Identify dependencies.
5. Explain the proposed implementation briefly.
6. Implement the smallest complete version.
7. Run relevant tests.
8. Run relevant builds.
9. Fix errors.
10. Verify the implementation.
11. Summarize what changed.

Do not claim that something works unless it has actually been tested.

---

## 5. Preserve Existing Work

The repository may already contain partially implemented frontend, backend, CI, or configuration files.

Do NOT rebuild or replace working components unnecessarily.

Before creating a new component:

* Check whether an equivalent already exists.
* Reuse existing architecture where practical.
* Modify existing code rather than creating duplicate implementations.

Do not delete major functionality without explicit approval.

---

## 6. Dataset Rules

Never assume that a dataset contains a particular type of data.

Before using a dataset:

1. Inspect its structure.
2. Identify its files.
3. Identify its schema.
4. Identify available labels.
5. Determine sample counts.
6. Check missing values.
7. Check duplicates.
8. Determine whether it is suitable for the intended task.
9. Document important limitations.

The project proposal references:

* SKU-110K — shelf product detection
* MOT17 / Retail CCTV — customer tracking
* M5 Forecasting — inventory prediction
* Rossmann Store Sales — sales and demand forecasting
* Grocery Store Dataset — product classification
* FER2013 — future emotion detection

The actual locally available datasets must always be verified before implementation.

If a required dataset is unavailable, clearly report the gap instead of inventing or simulating the missing data.

---

## 7. Data Pipeline

Keep raw datasets separate from processed datasets.

Preferred structure:

data/
├── raw/
└── processed/

Raw data must not be modified directly.

Data preprocessing should be reproducible.

Whenever practical:

raw data
→ validation
→ cleaning
→ transformation
→ processed data
→ database / ML pipeline

---

## 8. Backend Architecture

Keep responsibilities separated.

Preferred structure:

backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database/
│   └── main.py
└── tests/

API routes should not contain large amounts of business logic.

Business logic should live in services.

Database models should be separated from API schemas.

Machine-learning inference should be separated from API routing.

---

## 9. Frontend Architecture

Keep React components focused.

Prefer a structure such as:

frontend/
└── src/
├── components/
├── pages/
├── charts/
├── hooks/
├── services/
└── types/

Do not put large amounts of API/business logic directly inside UI components.

Use reusable components where appropriate.

Keep API communication centralized where practical.

---

## 10. Computer Vision

Computer vision should be implemented as an independent subsystem before being tightly coupled to inventory or business logic.

Preferred flow:

Camera / Image / Video
→ OpenCV
→ YOLO
→ Detection / Tracking
→ Structured output
→ Backend
→ Database / Analytics
→ Dashboard

Model paths, confidence thresholds, camera sources, and other configuration must not be hardcoded.

Use environment variables or configuration files where appropriate.

---

## 11. Machine Learning

Do not automatically choose a complex model.

For forecasting and predictive systems:

1. Establish a simple baseline.
2. Establish appropriate train/validation/test methodology.
3. Train the proposed model.
4. Evaluate it using appropriate metrics.
5. Compare against the baseline.
6. Document limitations.

Do not claim that an ML model is accurate without evaluation.

Keep training and inference code separate.

---

## 12. Database

Use migrations for schema changes where the project architecture supports them.

Never perform destructive database changes without explicit approval.

Do not hardcode database credentials.

Use environment variables for:

* database URLs
* secret keys
* API keys
* external service credentials
* model locations when appropriate

---

## 13. Testing

Backend changes should include appropriate tests.

Frontend changes should at minimum pass:

* TypeScript checks where configured
* production build

Before completing a milestone, run the relevant test/build commands.

If tests cannot be run because the required infrastructure does not yet exist, clearly report that instead of claiming success.

---

## 14. Git

Use small, meaningful commits.

Prefer feature branches for substantial features.

Do not rewrite Git history unless explicitly requested.

Do not commit:

* passwords
* API keys
* `.env` files containing secrets
* virtual environments
* `node_modules`
* large raw datasets
* generated build artifacts

---

## 15. Security

Never expose secrets in source code.

Never commit credentials.

Do not introduce authentication or authorization architecture without discussing the requirement first if it materially affects the system design.

Validate user/API input.

Do not trust client-provided data blindly.

---

## 16. Deployment

The intended deployment architecture is:

React frontend
→ Vercel

FastAPI backend
→ Railway

Do not modify deployment infrastructure unnecessarily.

Deployment configuration must remain compatible with the local development architecture.

---

## 17. Project Development Order

Unless the user explicitly changes the order, the project should generally progress through:

### Stage 1 — Foundation

* Backend foundation
* Frontend foundation
* Database
* API structure
* Testing
* CI

### Stage 2 — Data

* Dataset inspection
* Data validation
* Preprocessing
* Database ingestion

### Stage 3 — Business Analytics

* Inventory analytics
* Sales analytics
* Basic dashboard

### Stage 4 — Forecasting

* Demand forecasting
* Predictive restocking

### Stage 5 — Computer Vision

* Camera input
* OpenCV
* YOLO
* Product detection
* Shelf monitoring

### Stage 6 — Customer Analytics

* Person detection
* Tracking
* Dwell time
* Customer heatmap

### Stage 7 — Advanced Intelligence

* Product misplacement
* Dynamic pricing

### Stage 8 — Final Integration

* Unified dashboard
* Alerts
* Reports
* Performance improvements
* Deployment

Future modules such as emotion analytics or theft detection should not be implemented unless explicitly requested.

---

## 18. Important Product Principle

The system is intended as an AI-powered retail intelligence and decision-support platform.

AI recommendations should initially remain human-reviewable.

Do not automatically execute consequential business actions such as changing prices or placing orders unless explicitly requested and appropriately designed.

---

## 19. When to Ask the User

Ask the user before:

* deleting major functionality
* changing the overall architecture
* making destructive database changes
* adding paid external services
* adding external APIs that were not planned
* changing deployment infrastructure
* introducing major security/authentication architecture
* uploading project data to an external service
* making an assumption that materially changes project requirements

For ordinary implementation decisions within the existing architecture, proceed autonomously.

---

## 20. Definition of Done

A feature is not considered complete merely because code has been written.

A milestone should be considered complete only when:

* implementation exists
* relevant tests exist or the testing limitation is documented
* tests pass where applicable
* frontend builds successfully where applicable
* integration has been verified where applicable
* configuration is documented
* no secrets are committed
* the implementation follows this document
* remaining limitations are clearly reported

---

## 21. Communication Style

Be concise and technical.

Before a major implementation, provide a short plan.

During implementation, work autonomously rather than repeatedly asking for confirmation about minor coding decisions.

After implementation, report:

1. What was changed
2. What was tested
3. Test/build results
4. Any remaining issues
5. Any manual verification required

Do not claim success without verification.
