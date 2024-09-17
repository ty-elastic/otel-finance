from flask import Flask, request
import logging
import time
import random
import os
import uuid
import math

import requests
from opentelemetry import trace, baggage
from opentelemetry.metrics import get_meter
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

tracer = trace.get_tracer("decider")

meter = get_meter("decider")
trade_fee_dollars = meter.create_counter("trade-fee-dollars")
trade_volume_shares = meter.create_counter("trade-volume-shares")
trade_volume_dollars = meter.create_counter("trade-volume-dollars")

def sim_errors(*, strategy, symbol):
    
    latency_model = 0
    error_model = False
    error_db = False

    if strategy == 'conservative':
        latency_model = random.randint(50, 60) / 100.0
        if symbol == 'BAD':
            error_db = True
    else:
        if symbol == 'ERR':
            error_model = True

    return latency_model, error_model, error_db

def sim_market_data(*, strategy, symbol):
    pr_volume = random.randint(-100, 100)
    return pr_volume

def sim_decide(*, strategy, symbol, pr_volume):
    
    action = 'hold'
    rand = random.randint(0, 2)
    if rand == 1:
        action = 'buy'
    elif rand == 1:
        action = 'sell'
        
    shares = random.randint(1, 10 if strategy == 'conservative' else 100 if strategy == 'balanced' else 1000)
    share_price = random.randint(1, 500)
    
    return action, shares, share_price
    
@app.post('/decide')
def decide():
    current_span = trace.get_current_span()
    
    trade_id = str(uuid.uuid4())
    #current_span.set_attribute("trade_id", trade_id)
    baggage.set_baggage("trade_id", trade_id)
    
    strategy = request.args.get('strategy', default='balanced', type=str)
    symbol = request.args.get('symbol', default='ESTC', type=str)

    #current_span.set_attribute("symbol", symbol)
    baggage.set_baggage("symbol", symbol)

    latency_model, error_model, error_db = sim_errors(strategy=strategy, symbol=symbol )
    current_span.set_attribute("latency_model", latency_model)
    current_span.set_attribute("error_model", error_model)
    current_span.set_attribute("error_db", error_db)
     
    action, shares, share_price = decide_model(strategy=strategy, symbol=symbol, error=error_model, latency=latency_model)

    response = {}
    response['id'] = trade_id
    response['symbol']= symbol
        
    if error_db is True:
        symbol = None
        print('error DB!')
    trade_response = requests.post(f"http://{os.environ['TRADER_HOST']}:9000/trade", params={'id': trade_id, 'symbol': symbol, 'shares': shares, 'share_price': share_price, 'action': action})
    trade_response.raise_for_status()
    trade_response_json = trade_response.json()

    response['shares']= shares
    response['share_price']= share_price
    response['action']= action
    
    return response

@tracer.start_as_current_span("decide_model")
def decide_model(*, strategy, symbol, error=False, latency=0.0):
    
    app.logger.info("deciding to trade")
    
    pr_volume = sim_market_data(strategy=strategy, symbol=symbol)
    
    current_span = trace.get_current_span()
    current_span.set_attribute("in.pr_volume", pr_volume)
    current_span.set_attribute("in.strategy", strategy)
    
    if error:
        raise Exception("model failed") 
    
    ## MODEL WOULD BE CALLED HERE
    action, shares, share_price = sim_decide(strategy=strategy, symbol=symbol, pr_volume=pr_volume)
    if latency > 0:
        time.sleep(latency)

    current_span.set_attribute("out.shares", shares)
    current_span.set_attribute("out.share_price", share_price)
    current_span.set_attribute("out.action", action)
    if action == 'buy' or action == 'sell':
        current_span.set_attribute("out.value", shares * share_price)
        trade_fee_dollars.add(math.ceil(share_price * shares * .10))
        trade_volume_shares.add(shares)
        trade_volume_dollars.add(math.ceil(share_price * shares))
    else:
        current_span.set_attribute("out.value", 0)

    return action, shares, share_price
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001)