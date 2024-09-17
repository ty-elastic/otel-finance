from flask import Flask, request
import logging
import os
import math

import psycopg

from opentelemetry import trace, baggage
from opentelemetry.metrics import get_meter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

meter = get_meter("metric-trader")
trade_fee_dollars = meter.create_counter("trade-fee-dollars")
trade_volume_shares = meter.create_counter("trade-volume-shares")
trade_volume_dollars = meter.create_counter("trade-volume-dollars")

def init_db():
    try:
        with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE trades (id VARCHAR(100) PRIMARY KEY, symbol VARCHAR(10), shares float NOT NULL, action VARCHAR(10))")
                conn.commit()
    except Exception as inst:
        app.logger.warning("unable to recreate table")
        pass

@app.post('/trade')
def trade():

    trade_id = request.args.get('id')
    symbol = request.args.get('symbol', default=None, type=str)
    shares = request.args.get('shares', default=None, type=float)
    share_cost = request.args.get('share_cost', default=0, type=float)
    action = request.args.get('action', default=None, type=str)
   
    error = request.args.get('error', default='false', type=str)
        
    current_span = trace.get_current_span()
    current_span.set_attribute("in.symbol", symbol)
    current_span.set_attribute("in.shares", shares)
    current_span.set_attribute("in.share_cost", share_cost)
    current_span.set_attribute("in.action", action)
    
    print(error)
    if error == 'true':
        shares = None
     
    with psycopg.connect(f"host={os.environ['POSTGRES_HOST']} port=5432 dbname=trades user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trades (id, symbol, action, shares) VALUES (%s, %s, %s, %s)",
                (trade_id, symbol, action, shares))
            conn.commit()
            
            trade_fee_dollars.add(math.ceil(share_cost * shares * .10))
            trade_volume_shares.add(shares)
            trade_volume_dollars.add(math.ceil(share_cost * shares))
            
            current_span.set_attribute("out.result", 'committed')
            
            result = {'result': 'committed', 'id': trade_id}
            app.logger.info(result)
            return result

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=9000)