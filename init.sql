CREATE TABLE IF NOT EXISTS stock_prices (
    symbol      TEXT        NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    volume      BIGINT,
    CONSTRAINT stock_prices_pk PRIMARY KEY (symbol, timestamp)
);

