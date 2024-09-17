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

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

tracer = trace.get_tracer("decider")

meter = get_meter("decider")
trade_fee_dollars = meter.create_counter("trade-fee-dollars")
trade_volume_shares = meter.create_counter("trade-volume-shares")
trade_volume_dollars = meter.create_counter("trade-volume-dollars")

def sim_errors(*, day_of_week, symbol):
    
    latency_model = 0
    error_model = False
    error_db = False

    if day_of_week == 3:
        latency_model = random.randint(50, 55) / 100.0
        if symbol == 'ERR':
            error_db = True
    elif symbol == 'ERR':
        error_model = True

    return latency_model, error_model, error_db

market_data_seed = [random.randint(50, 100), random.randint(100, 250), random.randint(250, 300)]
market_data = {}

class StreamingMovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.sum = 0

    def process(self, value):
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)
    
    def get(self):
        return float(self.sum) / len(self.values)

def sim_market_data(*, symbol, day_of_week):
    
    pr_volume = 0
    
    if symbol == 'OD1':
        pr_volume = random.randint(90, 100)
    elif day_of_week == 1:
        pr_volume = random.randint(-100, 25)
    elif day_of_week == 2:
        pr_volume = random.randint(-75, 50)
    elif day_of_week == 3:
        pr_volume = random.randint(-50, 50)
    elif day_of_week == 4:
        pr_volume = random.randint(-50, 75)
    elif day_of_week == 5:
        pr_volume = random.randint(-25, 100)
    app.logger.info(f"pr_volume: {symbol}={pr_volume}")
        
    initial_idx = hash(symbol) % len(market_data_seed)
    if symbol not in market_data:
        share_price = market_data_seed[initial_idx]
        market_data[symbol] = StreamingMovingAverage(window_size=10)
        app.logger.info(f"initial share price: {symbol}={share_price}, idx={initial_idx}")
    else:
        current_share_price = market_data[symbol].get()
        share_price = current_share_price + (current_share_price * (float(pr_volume) / 100.0))
        if share_price < 1:
            share_price = market_data_seed[initial_idx] * abs(pr_volume / 100)
            app.logger.info(f"reset market share price: {symbol}={share_price}")
    
    smoothed_share_price = market_data[symbol].process(share_price)
    app.logger.info(f"current market share price: {symbol}={share_price},{smoothed_share_price}")

    return pr_volume, smoothed_share_price

def sim_decide(*, symbol, pr_volume):
    
    action = 'hold'
    if symbol == 'OD2':
        action = 'buy'
        shares = random.randint(90, 100)
    elif pr_volume <= -25:
        action = 'sell'
        if pr_volume <= -75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)
    elif pr_volume >= -25:
        action = 'buy'
        if pr_volume >= -75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)

    return action, shares
    
@app.post('/decide')
def decide():
    current_span = trace.get_current_span()
    
    trade_id = str(uuid.uuid4())
    context.attach(baggage.set_baggage("trade_id", trade_id))
    
    day_of_week = request.args.get('day_of_week', default=None, type=int)
    symbol = request.args.get('symbol', default='ESTC', type=str)
    context.attach(baggage.set_baggage("symbol", symbol))

    latency_model, error_model, error_db = sim_errors(day_of_week=day_of_week, symbol=symbol )
    current_span.set_attribute("latency_model", latency_model)
    current_span.set_attribute("error_model", error_model)
    current_span.set_attribute("error_db", error_db)
     
    action, shares, share_price = decide_model(day_of_week=day_of_week, symbol=symbol, error=error_model, latency=latency_model)

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
def decide_model(*, day_of_week=None, symbol, error=False, latency=0.0):
    
    if day_of_week is None:
        day_of_week = random.randint(1,5)
    
    app.logger.info(f"deciding to trade {symbol} on day {day_of_week}")
    
    pr_volume, share_price = sim_market_data(symbol=symbol, day_of_week=day_of_week)
    
    current_span = trace.get_current_span()
    current_span.set_attribute("in.pr_volume", pr_volume)
    current_span.set_attribute("in.day_of_week", day_of_week)
    
    if error:
        raise Exception("model failed") 
    
    ## MODEL WOULD BE CALLED HERE
    action, shares = sim_decide(symbol=symbol, pr_volume=pr_volume)
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