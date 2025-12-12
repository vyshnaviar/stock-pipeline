import os
import logging
import pandas as pd
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database config
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))

# Tickers to fetch
TICKERS = ["TSLA", "AAPL", "GOOGL", "MSFT", "AMZN"]

# UPSERT SQL
UPSERT_SQL = """
INSERT INTO stock_prices (symbol, timestamp, open, high, low, close, volume)
VALUES %s
ON CONFLICT (symbol, timestamp) DO UPDATE SET
  open = EXCLUDED.open,
  high = EXCLUDED.high,
  low = EXCLUDED.low,
  close = EXCLUDED.close,
  volume = EXCLUDED.volume;
"""

# Fetch stock data
def fetch_stock_data(symbol, period="2d", interval="1h"):
    try:
        logger.info("Fetching %s (period=%s interval=%s)", symbol, period, interval)
        df = yf.Ticker(symbol).history(period=period, interval=interval)
        if df.empty:
            logger.warning("Empty data for %s", symbol)
            return None
        df = df.reset_index()
        return df
    except Exception as e:
        logger.exception("Error fetching data for %s: %s", symbol, e)
        return None

# Prepare rows for DB
def prepare_rows(df, symbol):
    rows = []
    for _, row in df.iterrows():
        ts = row.get("Datetime") or row.get("Date")
        if pd.isna(ts):
            continue
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime()

        rows.append(
            (
                symbol,
                ts,
                None if pd.isna(row.get("Open")) else float(row["Open"]),
                None if pd.isna(row.get("High")) else float(row["High"]),
                None if pd.isna(row.get("Low")) else float(row["Low"]),
                None if pd.isna(row.get("Close")) else float(row["Close"]),
                None if pd.isna(row.get("Volume")) else int(row["Volume"]),
            )
        )
    return rows

# Upsert rows into DB
def upsert_rows(rows):
    if not rows:
        logger.info("No rows to upsert.")
        return

    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
        )
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, UPSERT_SQL, rows, page_size=200)
        logger.info("Upserted %d rows", len(rows))
    except Exception as e:
        logger.exception("Database error: %s", e)
    finally:
        if conn:
            conn.close()

# Main pipeline
def main():
    all_rows = []

    for symbol in TICKERS:
        df = fetch_stock_data(symbol)
        if df is None:
            continue
        rows = prepare_rows(df, symbol)
        all_rows.extend(rows)

    if not all_rows:
        logger.info("No data fetched for any ticker.")
        return

    upsert_rows(all_rows)

if __name__ == "__main__":
    main()
