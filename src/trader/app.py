from flask import Flask, request
import logging
import os

import psycopg

from opentelemetry import trace
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

from opentelemetry import _logs as logs
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.processor.logrecord.baggage import BaggageLogRecordProcessor

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

if 'OTEL_EXPORTER_OTLP_ENDPOINT' in os.environ:
    print("enable otel tracing")
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

if 'OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED' in os.environ:
    print("enable otel logging")
    log_provider = logs.get_logger_provider()
    if 'OTEL_EXPORTER_OTLP_ENDPOINT' in os.environ:
        exporter = OTLPLogExporter()
    log_provider.add_log_record_processor(BaggageLogRecordProcessor(ALLOW_ALL_BAGGAGE_KEYS, exporter))

def init_db():
    try:
        with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE trades (trade_id VARCHAR(100) PRIMARY KEY, customer_id VARCHAR(100) NOT NULL, timestamp timestamp default current_timestamp, symbol VARCHAR(10) NOT NULL, shares float NOT NULL, share_price float NOT NULL, action VARCHAR(10) NOT NULL)")
                conn.commit()
        app.logger.info("created table")
    except Exception as inst:
        app.logger.warning("unable to create table")
        pass
init_db()

@app.post('/trade')
def trade():

    customer_id = request.args.get('customer_id')
    trade_id = request.args.get('trade_id')
    symbol = request.args.get('symbol', default=None, type=None)
    shares = request.args.get('shares', default=None, type=float)
    share_price = request.args.get('share_price', default=0, type=float)
    action = request.args.get('action', default=None, type=str)

    with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trades (trade_id, customer_id, symbol, action, shares, share_price) VALUES (%s, %s, %s, %s, %s, %s)",
                (trade_id, customer_id, symbol, action, shares, share_price))
            conn.commit()

            app.logger.info("trade committed")
            return {'result': 'committed'}