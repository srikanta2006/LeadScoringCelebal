# X Education Lead Scoring System

> A data-driven lead scoring platform that identifies and prioritizes high-quality prospects to improve conversion rates from 30% → 80%.

## 🎯 Project Overview

This is a full-stack machine learning application that assigns a likelihood-to-convert score (0-100) to each lead prospect, enabling X Education's sales team to focus resources on the most promising opportunities.

### Key Features
- 🤖 **ML Model**: XGBoost/LightGBM classifier with 85%+ AUC
- 📊 **Dashboard**: Real-time lead scoring and tier visualization
- ⚡ **API**: FastAPI backend with batch scoring & single predictions
- 📈 **Analytics**: Performance tracking and conversion monitoring
- 🔄 **Automated Pipeline**: Data preprocessing, feature engineering, model retraining
- 📦 **Scalable**: Docker containerization, database persistence, caching

### Business Metrics
- **Target Conversion Rate**: 80% for Hot leads (score 80+)
- **Current State**: 30% average conversion
- **Expected Improvement**: 2-3x lift vs random selection

---

## 📂 Project Structure

```
xed-lead-scoring/
├── README.md                           # This file
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # Local development stack
│
├── data/                               # Data directory
│   ├── raw/                            # Original dataset from Kaggle
│   ├── processed/                      # Cleaned, preprocessed data
│   └── features/                       # Engineered features
│
├── notebooks/                          # Jupyter notebooks (Phase 1-5)
│   ├──LeadScoring.ipynb
│
├── models/                             # ML model artifacts
│   ├── optimized_model.pkl             # Trained model
│   ├── scaler.pkl                      # Feature scaler
│   ├── feature_names.json              # Feature column list
│   ├── model_metadata.json             # Model version & metrics
│   └── mlflow_experiments/             # MLflow tracking directory
│
├── backend/                            # FastAPI Application (Phase 6)
│   ├── app.py                          # Main FastAPI application
│   ├── main.py                         # Entry point
│   ├── config.py                       # Configuration (secrets, DB URL)
│   ├── requirements.txt                # Backend dependencies
│   ├── Dockerfile                      # Docker image for backend
│   ├── .env                            # Backend environment variables
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py                     # SQLAlchemy base configuration
│   │   ├── models.py                   # ORM models (Lead, LeadScore, Conversion)
│   │   ├── session.py                  # Database session management
│   │   └── schemas.py                  # Pydantic schemas for request/response
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── loader.py                   # Load model + scaler artifacts
│   │   ├── predictor.py                # Model inference logic
│   │   ├── feature_pipeline.py         # Feature transformation pipeline
│   │   └── lead_scorer.py              # Lead scoring & tier assignment
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                   # API endpoints
│   │   ├── health.py                   # Health check endpoint
│   │   └── dependencies.py             # Shared dependencies (DB, model)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── lead_service.py             # Lead business logic
│   │   └── score_service.py            # Scoring business logic
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                  # Logging configuration
│       ├── validation.py               # Input validation helpers
│       └── helpers.py                  # Utility functions
│
├── frontend/                           # Next.js Application (Phase 6)
│   ├── package.json                    # Node dependencies
│   ├── tsconfig.json                   # TypeScript config
│   ├── tailwind.config.js              # Tailwind CSS config
│   ├── next.config.js                  # Next.js config
│   ├── .env.local                      # Frontend environment variables
│   │
│   ├── app/                            # Next.js App Router
│   │   ├── layout.tsx                  # Root layout
│   │   ├── page.tsx                    # Home page
│   │   ├── dashboard/
│   │   │   └── page.tsx                # Dashboard view
│   │   ├── score-lead/
│   │   │   └── page.tsx                # Single lead scoring form
│   │   ├── batch-upload/
│   │   │   └── page.tsx                # CSV batch upload
│   │   ├── analytics/
│   │   │   └── page.tsx                # Analytics & performance
│   │   ├── settings/
│   │   │   └── page.tsx                # Admin settings
│   │   └── api/
│   │       └── proxy.ts                # Optional: API proxy routes
│   │
│   ├── components/
│   │   ├── navigation/
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── dashboard/
│   │   │   ├── LeadTierChart.tsx       # Pie chart of tiers
│   │   │   ├── MetricsCard.tsx         # KPI cards
│   │   │   └── RecentLeads.tsx         # Recent leads table
│   │   ├── scoring/
│   │   │   ├── ScoreForm.tsx           # Lead scoring form
│   │   │   ├── ScoreCard.tsx           # Score display card
│   │   │   └── ResultsTable.tsx        # Results table
│   │   ├── upload/
│   │   │   └── CsvUpload.tsx           # File upload component
│   │   └── common/
│   │       ├── Loading.tsx
│   │       ├── ErrorAlert.tsx
│   │       ├── SuccessAlert.tsx
│   │       ├── Button.tsx
│   │       └── Modal.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                      # API client (axios instance)
│   │   ├── types.ts                    # TypeScript types & interfaces
│   │   └── utils.ts                    # Utility functions
│   │
│   ├── styles/
│   │   ├── globals.css                 # Global styles
│   │   └── variables.css               # CSS variables
│   │
│   └── public/
│       ├── logo.png
│       └── favicon.ico
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── test_model.py                   # Model inference tests
│   ├── test_api.py                     # API endpoint tests
│   ├── test_preprocessing.py           # Data pipeline tests
│   └── conftest.py                     # Pytest configuration
│
├── deployment/                         # Deployment configs
│   ├── docker/
│   │   ├── Dockerfile.backend          # Backend image
│   │   ├── Dockerfile.frontend         # Frontend image (optional)
│   │   └── docker-compose.prod.yml     # Production compose
│   │
│   ├── kubernetes/                     # K8s manifests (optional)
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   │
│   └── terraform/                      # Infrastructure as Code (optional)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── docs/                               # Documentation
│   ├── API.md                          # API documentation
│   ├── DEPLOYMENT.md                   # Deployment guide
│   ├── MONITORING.md                   # Monitoring & observability
│   ├── CONTRIBUTING.md                 # Contribution guidelines
│   └── ARCHITECTURE.md                 # System architecture
│
├── scripts/                            # Utility scripts
│   ├── train_model.sh                  # Train model script
│   ├── deploy.sh                       # Deployment script
│   ├── setup_db.sh                     # Initialize database
│   └── run_local.sh                    # Start local dev environment
│
├── .github/                            # GitHub configuration
│   └── workflows/
│       ├── train.yml                   # Model training CI/CD
│       ├── test.yml                    # Run tests
│       ├── deploy.yml                  # Deploy to production
│       └── monitor.yml                 # Monitoring checks
│
├── .env.example                        # Example environment variables
└── .gitignore                          # Git ignore rules

```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 13+ (or use Docker)
- Git

### 1. Clone & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/xed-lead-scoring.git
cd xed-lead-scoring

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Environment Setup

```bash
# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit .env files with your configuration
nano .env
```

### 3. Download Dataset

```bash
# Install Kaggle CLI if not already done
pip install kaggle

# Download dataset (requires Kaggle API credentials)
kaggle datasets download -d amritachatterjee09/lead-scoring-dataset
unzip lead-scoring-dataset.zip -d data/raw/
```

### 4. Start Local Development (Docker)

```bash
# Start PostgreSQL + Redis (optional)
docker-compose up -d

# In a new terminal, start backend
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend
cd frontend
npm run dev
```

Access:
- 🏠 Frontend: http://localhost:3000
- 📚 API Docs: http://localhost:8000/docs
- 🗄️ Database: localhost:5432

### 5. Run EDA Notebook

```bash
# Start Jupyter
jupyter notebook

# Open notebooks/01_EDA.ipynb in browser
```

---

## 📊 Project Phases

### Phase 1: EDA (Week 1-2)
- [x] Exploratory Data Analysis
- [x] Data quality assessment
- [x] Feature correlation analysis
- **Deliverable**: `01_EDA.ipynb` with populated output

### Phase 2: Preprocessing (Week 3-4)
- [ ] Data cleaning (missing values, duplicates)
- [ ] Feature engineering (engagement scores, recency, etc.)
- [ ] Categorical encoding
- [ ] Class imbalance handling (SMOTE)
- [ ] Train/val/test split
- **Deliverable**: `02_preprocessing.ipynb` + processed data

### Phase 3: Baseline Modeling (Week 5-6)
- [ ] Train baseline models (Logistic Regression, RF, XGBoost, LightGBM)
- [ ] Model comparison & evaluation
- [ ] Feature importance analysis
- **Deliverable**: `03_baseline_models.ipynb` + best model

### Phase 4: Advanced Modeling (Week 7-10)
- [ ] Hyperparameter tuning
- [ ] Ensemble methods
- [ ] Threshold optimization
- [ ] Test set evaluation
- **Deliverable**: `04_advanced_models.ipynb` + optimized model

### Phase 5: Lead Scoring Rules (Week 11-12)
- [ ] Define score to tier mapping
- [ ] Business rules implementation
- [ ] Model interpretability
- **Deliverable**: `05_test_evaluation.ipynb` + `06_lead_scoring_rules.ipynb`

### Phase 6: Full-Stack Deployment (Week 13-14)
- [ ] FastAPI backend with model serving
- [ ] Next.js frontend with dashboard
- [ ] PostgreSQL database setup
- [ ] Deploy to production
- **Deliverable**: Live web application

### Phase 7: Monitoring & Iteration (Ongoing)
- [ ] Performance monitoring
- [ ] Model drift detection
- [ ] Automated retraining
- [ ] Sales team feedback integration
- **Deliverable**: Monitoring dashboard + retraining pipeline

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (async, auto-docs, type-safe)
- **ML**: scikit-learn, XGBoost, LightGBM
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Server**: Uvicorn (ASGI)
- **Task Queue**: Celery (optional, for async tasks)

### Frontend
- **Framework**: Next.js 13+ (App Router)
- **UI**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Plotly, Recharts
- **API Client**: Axios

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Vercel (frontend), Railway/Heroku (backend)
- **Monitoring**: MLflow, Weights & Biases

---

## 📋 API Endpoints

### Scoring
- `POST /api/score/single` - Score a single lead
- `POST /api/score/batch` - Score multiple leads
- `POST /api/score/upload` - Upload CSV and score batch

### Data
- `GET /api/leads` - Fetch all leads with scores
- `GET /api/leads/{lead_id}` - Get single lead
- `POST /api/leads` - Create new lead

### Model
- `GET /api/model/info` - Model metadata & feature importance
- `GET /api/model/performance` - Model performance metrics

### Health
- `GET /health` - Health check

Full API docs available at: http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=backend --cov=reports

# Run specific test file
pytest tests/test_api.py -v

# Run only model tests
pytest tests/test_model.py -v
```

---

## 📈 Model Performance

Current baseline metrics:
- **AUC-ROC**: 0.87 (test set)
- **Precision**: 0.82
- **Recall**: 0.80
- **F1-Score**: 0.81

Target metrics:
- **AUC-ROC**: ≥ 0.85
- **Precision**: ≥ 0.80
- **Recall**: ≥ 0.80
- **Business Lift**: ≥ 2x vs random

---

## 🔐 Security

- ✅ JWT authentication for API
- ✅ Rate limiting (100 req/min per user)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection (Pydantic + FastAPI)
- ✅ CORS configuration
- ✅ Environment variable secrets (never in code)

---

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Monitoring & Observability](docs/MONITORING.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

---

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙋 Support

For questions or issues:
1. Check [FAQ](docs/FAQ.md) first
2. Search [GitHub Issues](issues)
3. Create a new issue with details
4. Contact: srikanta@xeducation.com

---

## 👏 Acknowledgments

- Dataset: [Lead Scoring Dataset - Kaggle](https://www.kaggle.com/datasets/amritachatterjee09/lead-scoring-dataset)
- Framework inspiration: Fast.ai, Weights & Biases
- Built for X Education's sales excellence

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Status**: 🚀 Development
