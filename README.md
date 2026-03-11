# 🚆 TrainRadar

Real-Time Train Data Ingestion & ETL Platform

A production-grade data pipeline that ingests real-time train data
from multiple sources, processes it through Apache Kafka, and stores
it in TimescaleDB for querying via a FastAPI REST API.

---

## What it does

- Fetches train schedules from REST APIs every 30 seconds
- Listens to live train positions via WebSocket streams
- Parses GTFS-RT feeds (the international standard for real-time transit data)
- Publishes all data into Apache Kafka topics
- ETL workers consume from Kafka, validate the data, and save to TimescaleDB
- FastAPI serves the processed data via REST endpoints

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Message Broker | Apache Kafka |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| Data Validation | Pydantic |
| Containerisation | Docker Compose |

---

## Project Structure
```
trainradar/
├── config/           # Settings and logging
├── ingestion/
│   ├── sources/      # REST poller, WebSocket listener, GTFS-RT parser
│   └── producers/    # Kafka producers
├── etl/
│   ├── consumers/    # Kafka consumers
│   ├── transformers/ # Data transformation
│   └── validators/   # Pydantic schemas
├── api/
│   ├── routers/      # FastAPI endpoints
│   └── schemas/      # Response models
├── db/
│   ├── migrations/   # SQL schema files
│   └── models/       # SQLAlchemy models
├── scripts/          # Utility and test scripts
└── docker-compose.yml
```

---

## Getting Started

### 1 - Clone the repo
```bash
git clone https://github.com/vijayasundari937-glitch/trainradar.git
cd trainradar
```

### 2 - Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3 - Start Docker services
```bash
docker compose up -d
```

### 4 - Run database migrations
```bash
type "db\migrations\001_initial_schema.sql" | docker exec -i trainradar_db psql -U trainradar -d trainradar_db
```

### 5 - Start the API
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6 - Open in browser
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Kafka UI: http://localhost:8080

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| GET | /positions | Get latest train positions |
| GET | /positions/{train_id} | Get position history for one train |

---

## Built With

- Python 3.11
- FastAPI
- Apache Kafka
- TimescaleDB
- Docker