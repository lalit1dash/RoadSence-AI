# 🛣️ RoadSense – AI-Powered Road Damage Detection & Risk Prediction

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18.3-61dafb?logo=react)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green?logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-yellow)

> An intelligent road damage inspection system powered by computer vision and machine learning. Upload road images to detect damage types, estimate severity, predict repair risk, and generate AI-powered inspection reports.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                            │
│   ┌─────────┐  ┌───────────┐  ┌──────┐  ┌─────────┐  ┌─────────┐  │
│   │  Upload  │  │ Dashboard │  │ Map  │  │ Reports │  │ History │  │
│   └────┬─────┘  └─────┬─────┘  └──┬───┘  └────┬────┘  └────┬────┘  │
│        └──────────────┴───────────┴────────────┴────────────┘       │
│                              React + Vite (Tailwind CSS)             │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ HTTP / REST API
┌──────────────────────────────────▼──────────────────────────────────┐
│                       BACKEND (FastAPI)                              │
│   ┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐ │
│   │  /detection  │  │ /inspections │  │ /dashboard │  │ /reports │ │
│   └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  └────┬─────┘ │
│          └─────────────────┴────────────────┴───────────────┘       │
│                              ML Pipeline                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│   │Module A  │→ │Module B  │→ │Module C  │→ │   Module D       │   │
│   │ YOLO Det │  │Severity  │  │  Risk    │  │Report Generation │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ Motor (async)
┌──────────────────────────────────▼──────────────────────────────────┐
│                       MongoDB (Atlas / Local)                        │
│        inspections │ reports │ users │ audit_logs                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | 🔍 **Damage Detection** | Identifies road damage regions using YOLO-based object detection |
| 2 | 🏷️ **Damage Classification** | Classifies damage into types: cracks, potholes, rutting, etc. |
| 3 | 📊 **Severity Estimation** | Scores damage severity (Low / Medium / High / Critical) |
| 4 | ⚠️ **Risk Prediction** | Predicts repair risk using ML models with contextual factors |
| 5 | 🔧 **Repair Priority** | Recommends repair urgency and estimated timeline |
| 6 | 🗺️ **Interactive Map** | Visualizes inspections geographically with Leaflet.js |
| 7 | 📄 **AI Reports** | Generates comprehensive PDF inspection reports |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Vite, Tailwind CSS | UI framework and build tooling |
| **UI Components** | Framer Motion, Lucide React | Animations and icons |
| **Charts** | Recharts | Dashboard visualizations |
| **Maps** | Leaflet, React-Leaflet | Interactive map display |
| **HTTP Client** | Axios | API communication |
| **Backend** | FastAPI, Uvicorn | REST API and ASGI server |
| **ML** | OpenCV, NumPy, scikit-learn | Image processing and ML |
| **Detection** | YOLO (via OpenCV DNN) | Road damage detection |
| **Database** | MongoDB 7, Motor | Async document storage |
| **Reports** | ReportLab | PDF generation |
| **Auth** | python-jose, passlib | JWT authentication |

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB 7.0 (local or Atlas)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/roadsense.git
cd roadsense
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (if needed)
# Edit src/config/api.js for custom API URLs

# Run development server
npm run dev
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 🐳 Docker Setup

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `DB_NAME` | `roadsense` | Database name |
| `SECRET_KEY` | — | JWT signing secret (required) |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins (comma-separated) |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum upload image size in MB |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded images |

---

## 🤖 ML Modules

### Module A – YOLO Detection
Processes uploaded road images through a YOLO object detection model to identify and localize damage regions. Returns bounding boxes with class labels and confidence scores.

**Outputs:** `detections[]` with `class_name`, `confidence`, `bbox`, `area_ratio`

### Module B – Severity Classification
Analyzes the detection results to compute an overall severity score using damage area coverage, number of detections, damage type weights, and confidence levels.

**Outputs:** `level` (Low/Medium/High/Critical), `score` (0–100), `features` dict

### Module C – Risk Prediction
Applies a scikit-learn classifier (or rule-based logic in demo mode) to predict repair risk based on severity features, damage density, and historical patterns.

**Outputs:** `level`, `score`, `factors[]`, `repair_priority`, `estimated_repair_time`

### Module D – Report Generation
Generates comprehensive inspection reports using ReportLab PDF library. Includes executive summary, damage analysis, severity assessment, risk evaluation, and prioritized recommendations.

**Outputs:** PDF binary / structured JSON report with all sections

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `POST` | `/api/detection/analyze` | Upload and analyze a road image |
| `GET` | `/api/detection/{id}` | Get a single detection result |
| `GET` | `/api/inspections/` | List all inspections (paginated) |
| `GET` | `/api/inspections/{id}` | Get inspection details |
| `DELETE` | `/api/inspections/{id}` | Delete an inspection |
| `GET` | `/api/dashboard/stats` | Aggregated dashboard statistics |
| `GET` | `/api/dashboard/map-data` | Inspection map points |
| `GET` | `/api/dashboard/recent` | Recent inspections |
| `POST` | `/api/reports/generate/{id}` | Generate report for inspection |
| `GET` | `/api/reports/` | List all reports |
| `GET` | `/api/reports/{id}` | Get report details |
| `GET` | `/api/reports/{id}/pdf` | Download PDF report |

---

## 📖 Usage Guide

1. **Navigate to Detect page** (`/detect`)
2. **Upload a road image** (JPG/PNG, max 10MB) by dragging or clicking the upload zone
3. **Optionally add location** (latitude, longitude, address) for map integration
4. **Click "Analyze Road"** – the AI pipeline processes the image
5. **Review results**: annotated image, detections, severity, risk, and repair priority
6. **Generate a report** by clicking "Generate Report"
7. **View the interactive map** at `/map` to see all geolocated inspections
8. **Browse history** at `/history` to review past inspections
9. **Access dashboard** at `/dashboard` for aggregate statistics and charts

---

## 📁 Project Structure

```
roadsense/
├── README.md
├── .env.example
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Pydantic settings
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py        # Motor async MongoDB client
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic v2 request/response models
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── demo_data.py         # Demo mode data generators
│   │   └── weights/             # Model weight files (not in git)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── health.py            # Health check endpoint
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Shared utility functions
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    └── src/
        ├── main.jsx             # React entry point
        ├── App.jsx              # Router setup with lazy pages
        ├── index.css            # Tailwind directives + custom CSS
        └── config/
            └── api.js           # Axios instance
```

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent async web framework
- [YOLO](https://ultralytics.com/) for the detection architecture inspiration
- [OpenStreetMap](https://www.openstreetmap.org/) for map tiles via Leaflet
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
