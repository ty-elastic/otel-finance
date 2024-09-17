from flask import Flask, request
import logging
import time
import random
import os
import uuid

import requests
from opentelemetry import trace, baggage, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("decider.tracer")

@app.post('/decide')
def decide():
    
    trade_id = str(uuid.uuid4())
    context.attach(baggage.set_baggage("trade_id", trade_id))
    
    bags = baggage.get_all()
    print(bags)
    
    strategy = request.args.get('strategy', default='aggressive', type=str)
    pr_volume = request.args.get('pr_volume', default=0, type=int)
    symbol = request.args.get('symbol', default='ESTC', type=str)
    
    model_error = request.args.get('model_error', default='false', type=str)
    model_latency = request.args.get('model_latency', default=0, type=int)
    
    sql_error = request.args.get('sql_error', default='false', type=str)

    app.logger.info("deciding to trade")
    
    action, shares, share_cost = decide_model(strategy=strategy, pr_volume=pr_volume, symbol=symbol, error=model_error, latency=model_latency)

    response = requests.post(f"http://{os.environ['TRADER_HOST']}:9000/trade", params={'id': trade_id, 'symbol': symbol, 'shares': shares, 'share_cost': share_cost, 'action': action, 'error': sql_error})
    response_json = response.json()

    response_json['id'] = trade_id
    response_json['strategy']= strategy
    response_json['symbol']= symbol
    response_json['shares']= shares
    response_json['action']= action
    response_json['share_cost']= share_cost

    return response_json

@tracer.start_as_current_span("decide_model")
def decide_model(*, strategy, pr_volume, symbol, error=False, latency=0):
    
    current_span = trace.get_current_span()
    current_span.set_attribute("in.strategy", strategy)
    current_span.set_attribute("in.pr_volume", pr_volume)
    current_span.set_attribute("in.symbol", symbol)
    
    ## MODEL WOULD BE CALLED HERE
    
    if error == 'true':
        raise Exception("model failed") 
    if latency > 0:
        time.sleep(latency)
        
    action = 'buy' if random.randint(0, 1) == 0 else 'sell'
    shares = random.randint(1, 10 if strategy == 'conservative' else 100 if strategy == 'balanced' else 1000)
    share_cost = random.randint(1, 500)
  
    current_span.set_attribute("out.share_cost", share_cost)
    current_span.set_attribute("out.action", action)
    current_span.set_attribute("out.shares", shares)
    current_span.set_attribute("out.value", shares * share_cost)

    return action, shares, share_cost
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001)