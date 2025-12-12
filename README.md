# **Dockerized Stock Data Pipeline with Airflow**
# **Objective**

This project implements a Dockerized data pipeline using Airflow to automatically fetch, parse, and store stock market data in PostgreSQL. The pipeline fetches stock data hourly from Yahoo Finance (yfinance), handles missing data gracefully, and logs all operations.
<img width="947" height="399" alt="image" src="https://github.com/user-attachments/assets/d8378c2d-78e7-420b-981f-2edde3281ee6" />

# Features

Automatic Data Fetching: Retrieves stock market data on a scheduled basis (hourly).

Data Parsing & Storage: Converts raw data into structured format and upserts into PostgreSQL.

Error Handling: Robust try/except blocks to manage API or DB errors.

Dockerized & Portable: Full pipeline runs via Docker Compose.

Environment Variables: Manages credentials securely using .env file.

Scalable & Resilient: Batch inserts, Airflow DAG retries, and max active runs configuration.

# Project Structure
stock-pipeline/
│
├─ dags/
│   └─ stock_dag.py           # Airflow DAG orchestrating the pipeline
│
├─ scripts/
│   └─ fetch_and_store.py     # Python script fetching and upserting stock data
│
├─ docker-compose.yml         # Docker Compose configuration
├─ Dockerfile                 # Airflow image setup
├─ init.sql                   # PostgreSQL table initialization
├─ requirements.txt           # Python dependencies
├─ .gitignore
├─ README.md
└─ .env.example               # Example environment variables

Quick Start

Copy .env.example → .env and fill in your credentials:

POSTGRES_USER=stockuser
POSTGRES_PASSWORD=stockpass
POSTGRES_DB=stockdb
POSTGRES_PORT=5432
POSTGRES_HOST=stock_postgres
STOCK_SYMBOL=TSLA
ALPHA_VANTAGE_KEY=your_key_here (optional)


Build and start the stack:

docker compose up --build -d


Access Airflow UI:

http://localhost:8080


Enable and trigger DAG fetch_stock_hourly manually for testing.

Database Verification

Connect to the Postgres container:

docker exec -it stock_postgres psql -U stockuser -d stockdb
<img width="941" height="441" alt="image" src="https://github.com/user-attachments/assets/f44eb15a-67f1-460a-b43c-31ecbb8aac90" />

Sample queries:

-- Check tickers inserted
SELECT DISTINCT symbol FROM stock_prices;

-- Count rows per ticker
SELECT symbol, COUNT(*) FROM stock_prices GROUP BY symbol ORDER BY symbol;

-- View recent data
SELECT * FROM stock_prices ORDER BY timestamp DESC LIMIT 20;

Logging

Logs include:

Raw DataFrame preview from yfinance.

Parsed rows before database insertion.

Logs are accessible in Airflow UI → DAG Run → Task Logs.

# Technical Highlights

Docker Compose: Starts Postgres, Airflow Scheduler, Webserver, and DB init container.

Airflow DAG: stock_dag.py defines hourly task using PythonOperator.

Data Pipeline:

Fetch stock data via yfinance.

Parse DataFrame to Python tuples.

Upsert into Postgres (ON CONFLICT DO UPDATE).

Handle missing data (NaN → NULL) and log exceptions.

Security: All credentials handled via environment variables (.env).

Scalability: Batch inserts using execute_values and Airflow concurrency settings.

Docker Cleanup & Troubleshooting

Rebuild everything if Postgres table didn’t initialize:

docker compose down -v
docker compose up --build -d


Ignore Airflow logs for Git:

logs/


Ensure .env is added to .gitignore to avoid committing secrets.

# Evaluation Alignment
Criteria	Implementation
Correctness	Data fetched hourly, parsed, and upserted accurately.
Error Handling	try/except, warnings for missing data, DAG retries configured.
Scalability	Batch inserts, Airflow concurrency control, supports multiple tickers.
Code Quality	Modular functions, logging for debugging, clean structure.
Dockerization	Single command deployment using Docker Compose.
