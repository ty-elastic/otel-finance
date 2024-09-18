from flask import Flask, request
import logging
import time
import random
import os
import uuid
import math

import requests
from opentelemetry import trace, baggage, context
from opentelemetry.metrics import get_meter
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

import model

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

tracer = trace.get_tracer("decider")

meter = get_meter("decider")
trade_fee_dollars = meter.create_counter("trade-fee-dollars")
trade_volume_shares = meter.create_counter("trade-volume-shares")

def set_attribute_and_baggage(key, value):
    current_span = trace.get_current_span()
    current_span.set_attribute(key, value)
    context.attach(baggage.set_baggage(key, value))

@app.post('/decide')
def decide():
    current_span = trace.get_current_span()
    
    trade_id = str(uuid.uuid4())
    set_attribute_and_baggage("trade_id", trade_id)
    
    customer_id = request.args.get('customer_id', default=None, type=str)
    set_attribute_and_baggage("customer_id", customer_id)
    
    day_of_week = request.args.get('day_of_week', default=None, type=str)
    if day_of_week is None:
        day_of_week = random.choice(['M','Tu', 'W', 'Th', 'F'])
    set_attribute_and_baggage("in.day_of_week", day_of_week)
    
    symbol = request.args.get('symbol', default='ESTC', type=str)
    set_attribute_and_baggage("in.symbol", symbol)

    latency_model, error_model, error_db = model.sim_errors(day_of_week=day_of_week, symbol=symbol )
    current_span.set_attribute("err.latency_model", latency_model)
    current_span.set_attribute("err.error_model", error_model)
    current_span.set_attribute("err.error_db", error_db)
     
    action, shares, share_price = decide_model(trade_id=trade_id, customer_id=customer_id, day_of_week=day_of_week, symbol=symbol, error=error_model, latency=latency_model)

    response = {}
    response['id'] = trade_id
    response['symbol']= symbol
        
    if error_db is True:
        symbol = None
    trade_response = requests.post(f"http://{os.environ['TRADER_HOST']}:9000/trade", params={'customer_id': customer_id, 'trade_id': trade_id, 'symbol': symbol, 'shares': shares, 'share_price': share_price, 'action': action})
    trade_response.raise_for_status()
    trade_response_json = trade_response.json()

    response['shares']= shares
    response['share_price']= share_price
    response['action']= action
    
    return response

@tracer.start_as_current_span("decide_model")
def decide_model(*, trade_id, customer_id, day_of_week, symbol, error=False, latency=0.0):

    app.logger.info(f"trade requested for {symbol} on day {day_of_week}", extra={'trade_id': trade_id, 'customer_id': customer_id})
    
    pr_volume, share_price = model.sim_market_data(symbol=symbol, day_of_week=day_of_week)
    
    current_span = trace.get_current_span()
    current_span.set_attribute("in.pr_volume", pr_volume)
    
    if error:
        current_span.set_attribute("canary_build", "true")
        raise Exception("CUDA out of memory. Tried to allocate 256.00 MiB (GPU 0; 11.17 GiB total capacity; 9.70 GiB already allocated; 179.81 MiB free; 9.85 GiB reserved in total by PyTorch)") 
    
    ## MODEL WOULD BE CALLED HERE
    action, shares = model.sim_decide(symbol=symbol, pr_volume=pr_volume)
    if latency > 0:
        time.sleep(latency)

    current_span.set_attribute("out.shares", shares)
    current_span.set_attribute("out.share_price", share_price)
    current_span.set_attribute("out.action", action)
    if action == 'buy' or action == 'sell':
        current_span.set_attribute("out.value", shares * share_price)
        trade_fee_dollars.add(math.ceil(share_price * shares * .001))
        trade_volume_shares.add(shares)
    else:
        current_span.set_attribute("out.value", 0)
        
    app.logger.info(f"traded {symbol} on day {day_of_week}", extra={'trade_id': trade_id, 'customer_id': customer_id})

    return action, shares, share_price