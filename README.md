# 🚆 TrainRadar

**Real-Time Train Data Ingestion & ETL Platform**

TrainRadar is a production-grade backend system that ingests, processes,
and serves real-time train data via a secure REST API.

Built with Python, FastAPI, Kafka, TimescaleDB, and Docker.

---

## 🏗️ Architecture
```
Data Sources → Kafka → ETL Consumer → TimescaleDB → FastAPI → Clients
```

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Message Broker | Apache Kafka |
| Database | TimescaleDB (PostgreSQL) |
| Cache | Redis |
| Ingestion | REST polling, WebSocket, GTFS-RT |
| Containerisation | Docker + Docker Compose |
| Testing | Pytest (35 tests) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop

### 1. Clone the repo
```bash
git clone https://github.com/vijayasundari937-glitch/trainradar.git
cd trainradar
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux
```
Edit `.env` with your settings.

### 5. Start Docker services
```bash
docker compose up -d
```

### 6. Run database migrations
```bash
type "db\migrations\001_initial_schema.sql" | docker exec -i trainradar_db psql -U trainradar -d trainradar_db
```

### 7. Seed test data (optional)
```bash
python scripts/seed_data.py
```

### 8. Start the API
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 9. Open the docs
```
http://localhost:8000/docs
```

---

## 🔑 Authentication

All endpoints (except `/health`) require an API key in the request header:
```
X-API-Key: your-secret-key
```

Set your key in `.env`:
```
API_SECRET_KEY=your-secret-key
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/health` | Health check | ❌ |
| GET | `/positions` | All train positions | ✅ |
| GET | `/positions/{train_id}` | Single train history | ✅ |
| GET | `/delays` | Trip delay updates | ✅ |
| GET | `/delays/{trip_id}` | Single trip delays | ✅ |
| GET | `/alerts` | Service alerts | ✅ |
| GET | `/alerts/{alert_id}` | Single alert | ✅ |
| GET | `/search?q=` | Search all data | ✅ |
| GET | `/stats` | Network statistics | ✅ |

### Filter Examples
```bash
# Filter positions by route
GET /positions?route_id=ROUTE_A

# Filter positions by source
GET /positions?source=gtfs-rt

# Filter delays by minimum delay
GET /delays?min_delay=120

# Filter alerts by effect
GET /alerts?effect=DELAY

# Search across everything
GET /search?q=IC123
```

---

## 🐳 Docker Services

| Service | Image | Port |
|---|---|---|
| TimescaleDB | timescale/timescaledb:latest-pg16 | 5432 |
| Kafka | confluentinc/cp-kafka:7.6.0 | 9092 |
| Zookeeper | confluentinc/cp-zookeeper:7.6.0 | 2181 |
| Redis | redis:7-alpine | 6379 |
| Kafka UI | provectuslabs/kafka-ui | 8080 |
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# Stop all services
docker compose down
```

---

## 🧪 Running Tests
```bash
# Run all 35 tests
python -m pytest tests/ -v

# Run only auth tests
python -m pytest tests/units/test_auth.py -v

# Run only validator tests
python -m pytest tests/units/test_validators.py -v
```

---

## 📁 Project Structure
```
trainradar/
├── api/                    # FastAPI application
│   ├── routers/            # Endpoint handlers
│   │   ├── health.py
│   │   ├── positions.py
│   │   ├── delays.py
│   │   ├── alerts.py
│   │   ├── search.py
│   │   └── stats.py
│   ├── schemas/            # Pydantic response models
│   ├── auth.py             # API key authentication
│   └── main.py             # App entry point
├── config/                 # Settings and logging
├── db/                     # Database models and migrations
├── etl/                    # ETL consumers and validators
├── ingestion/              # Data source connectors
│   └── sources/
│       ├── rest_poller.py
│       ├── ws_listener.py
│       ├── gtfs_rt_parser.py
│       └── tfl_connector.py
├── scripts/                # Utility scripts
├── tests/                  # Test suite (35 tests)
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | Environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address | `localhost:9092` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `API_SECRET_KEY` | API authentication key | - |
| `TFL_API_KEY` | Transport for London API key | - |

---

## 📊 Kafka Topics

| Topic | Purpose |
|---|---|
| `raw.train.positions` | Raw position data from all sources |
| `raw.train.schedules` | Raw schedule data |
| `raw.train.gtfs` | Raw GTFS-RT feed data |
| `processed.train.events` | Processed and validated events |
| `dead.letter.queue` | Failed messages for inspection |

---

## 🛠️ Tech Stack

- **Python 3.11** — Core language
- **FastAPI** — REST API framework
- **SQLAlchemy** — Async ORM
- **asyncpg** — Async PostgreSQL driver
- **aiokafka** — Async Kafka client
- **TimescaleDB** — Time-series database
- **aiohttp** — Async HTTP client
- **Pydantic** — Data validation
- **Pytest** — Testing framework
- **Docker** — Containerisation
- **structlog** — Structured logging

---

## 📝 License

MIT License — feel free to use this project as a learning reference.
```

Save with `Ctrl+S`.

---

## Create `.env.example`

In the root of your project create `.env.example` — this is a safe template others can use without your real secrets:
```
# TrainRadar - Environment Variables
# Copy this file to .env and fill in your values

APP_ENV=development
APP_NAME=TrainRadar
LOG_LEVEL=INFO

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_RAW_POSITIONS=raw.train.positions
KAFKA_TOPIC_RAW_SCHEDULES=raw.train.schedules
KAFKA_TOPIC_RAW_GTFS=raw.train.gtfs
KAFKA_TOPIC_PROCESSED=processed.train.events
KAFKA_TOPIC_DLQ=dead.letter.queue
KAFKA_CONSUMER_GROUP=trainradar-etl-group

# Database
DATABASE_URL=postgresql+asyncpg://trainradar:your_password@localhost:5432/trainradar_db
DB_USER=trainradar
DB_PASSWORD=your_password
DB_NAME=trainradar_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Authentication
API_SECRET_KEY=your-secret-key-here

# TfL API (optional)
# Get a free key at https://api-portal.tfl.gov.uk
TFL_API_KEY=your_tfl_key_here