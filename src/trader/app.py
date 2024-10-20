from flask import Flask, request
import logging

import random
import os
import uuid
import math

import requests

from opentelemetry import trace, baggage, context
from opentelemetry.metrics import get_meter
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

from opentelemetry import _logs as logs
from opentelemetry.processor.logrecord.baggage import BaggageLogRecordProcessor

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

ATTRIBUTE_PREFIX = "com.example"

import model

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

if 'OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED' in os.environ:
    print("enable otel logging")
    log_provider = logs.get_logger_provider()
    log_provider.add_log_record_processor(BaggageLogRecordProcessor(ALLOW_ALL_BAGGAGE_KEYS))

tracer = trace.get_tracer("trader")

meter = get_meter("trader")
trading_revenue = meter.create_counter("trading_revenue", "units")
trading_volume = meter.create_counter("trading_volume", "shares")

def conform_request_bool(value):
    return value.lower() == 'true'

def set_attribute_and_baggage(key, value):
    current_span = trace.get_current_span()
    current_span.set_attribute(key, value)
    context.attach(baggage.set_baggage(key, value))

@app.post('/reset')
def reset():
    model.reset_market_data()
    return None
    
def decode_common_args():
    trade_id = str(uuid.uuid4())
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.trade_id", trade_id)
    
    customer_id = request.args.get('customer_id', default=None, type=str)
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.customer_id", customer_id)
    
    day_of_week = request.args.get('day_of_week', default=None, type=str)
    if day_of_week is None:
        day_of_week = random.choice(['M','Tu', 'W', 'Th', 'F'])
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.day_of_week", day_of_week)
    
    region = request.args.get('region', default="NA", type=str)
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.region", region)

    symbol = request.args.get('symbol', default='ESTC', type=str)
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.symbol", symbol)

    data_source = request.args.get('data_source', default='monkey', type=str)
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.data_source", data_source)

    classification = request.args.get('classification', default=None, type=str)
    if classification is not None:
        set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.classification", classification)
    
    # forced errors
    latency = request.args.get('latency', default=0, type=float)
    error_model = request.args.get('error_model', default=False, type=conform_request_bool)
    error_db = request.args.get('error_db', default=False, type=conform_request_bool)
    skew_market_factor = request.args.get('skew_market_factor', default=0, type=int)

    canary = request.args.get('canary', default="false", type=str)
    set_attribute_and_baggage(f"{ATTRIBUTE_PREFIX}.canary", canary)
    
    return trade_id, customer_id, day_of_week, region, symbol, latency, error_model, error_db, skew_market_factor, canary, data_source, classification

@tracer.start_as_current_span("trade")
def trade(*, trade_id, customer_id, symbol, day_of_week, shares, share_price, canary, action, error_db):
    current_span = trace.get_current_span()
    
    app.logger.info(f"trade requested for {symbol} on day {day_of_week}")
    
    current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.shares", shares)
    current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.share_price", share_price)
    current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.action", action)
    if action == 'buy' or action == 'sell':
        current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.value", shares * share_price)
        trading_revenue.add(math.ceil(share_price * shares * .001))
        trading_volume.add(shares)
    else:
        current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.value", 0)

    response = {}
    response['id'] = trade_id
    response['symbol']= symbol
        
    if error_db is True:
        share_price = -share_price
        shares = -shares
    trade_response = requests.post(f"http://{os.environ['ROUTER_HOST']}:9000/record", params={'canary': canary, 'customer_id': customer_id, 'trade_id': trade_id, 'symbol': symbol, 'shares': shares, 'share_price': share_price, 'action': action})
    trade_response.raise_for_status()
    trade_response_json = trade_response.json()

    response['shares']= shares
    response['share_price']= share_price
    response['action']= action
    
    app.logger.info(f"traded {symbol} on day {day_of_week} for {customer_id}")
    
    return response
    
@app.post('/trade/force')
def trade_force():
    trade_id, customer_id, day_of_week, region, symbol, latency, error_model, error_db, skew_market_factor, canary, data_source, classification = decode_common_args()

    action = request.args.get('action', type=str)
    shares = request.args.get('shares', type=int)
    share_price = request.args.get('share_price', type=float)

    return trade (trade_id=trade_id, symbol=symbol, customer_id=customer_id, day_of_week=day_of_week, shares=shares, share_price=share_price, canary=canary, action=action, error_db=False)

@app.post('/trade/request')
def trade_request():
    trade_id, customer_id, day_of_week, region, symbol, latency, error_model, error_db, skew_market_factor, canary, data_source, classification = decode_common_args()

    action, shares, share_price = run_model(trade_id=trade_id, customer_id=customer_id, day_of_week=day_of_week, symbol=symbol, 
                                                   error=error_model, latency=latency, skew_market_factor=skew_market_factor)

    return trade (trade_id=trade_id, symbol=symbol, customer_id=customer_id, day_of_week=day_of_week, shares=shares, share_price=share_price, canary=canary, action=action, error_db=error_db)

@tracer.start_as_current_span("run_model")
def run_model(*, trade_id, customer_id, day_of_week, symbol, error=False, latency=0.0, skew_market_factor=0):
    current_span = trace.get_current_span()
    
    market_factor, share_price = model.sim_market_data(symbol=symbol, day_of_week=day_of_week, skew_market_factor=skew_market_factor)
    current_span.set_attribute(f"{ATTRIBUTE_PREFIX}.market_factor", market_factor)
    
    action, shares = model.sim_decide(error=error, latency=latency, symbol=symbol, market_factor=market_factor)

    return action, shares, share_price