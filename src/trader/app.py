from flask import Flask, request
import logging
import os
import math

import psycopg

from opentelemetry import trace
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

def init_db():
    try:
        with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE trades (id VARCHAR(100) PRIMARY KEY, timestamp timestamp default current_timestamp, symbol VARCHAR(10) NOT NULL, shares float NOT NULL, share_price float NOT NULL, action VARCHAR(10) NOT NULL)")
                conn.commit()
        app.logger.info("created table")
    except Exception as inst:
        app.logger.warning("unable to create table")
        pass
init_db()

@app.post('/trade')
def trade():

    trade_id = request.args.get('id')
    symbol = request.args.get('symbol', default=None, type=None)
    shares = request.args.get('shares', default=None, type=float)
    share_price = request.args.get('share_price', default=0, type=float)
    action = request.args.get('action', default=None, type=str)
    
    with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trades (id, symbol, action, shares, share_price) VALUES (%s, %s, %s, %s, %s)",
                (trade_id, symbol, action, shares, share_price))
            conn.commit()

            result = {'result': 'committed', 'id': trade_id}
            app.logger.info(result, extra={'trade_id': trade_id})
            return result