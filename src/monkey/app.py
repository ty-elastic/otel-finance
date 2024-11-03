from flask import Flask, request
import logging
import requests
import random
import time
import os
from threading import Thread

from opentelemetry import trace, baggage, context
from opentelemetry.metrics import get_meter
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

from opentelemetry import _logs as logs
from opentelemetry.processor.logrecord.baggage import BaggageLogRecordProcessor

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))

if 'OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED' in os.environ:
    print("enable otel logging")
    log_provider = logs.get_logger_provider()
    log_provider.add_log_record_processor(BaggageLogRecordProcessor(ALLOW_ALL_BAGGAGE_KEYS))

TRADE_TIMEOUT = 5
S_PER_DAY = 60
TRAINING_TRADE_COUNT = 1000

DAYS_OF_WEEK = ['M','Tu', 'W', 'Th', 'F']
ACTIONS = ['buy', 'sell', 'hold']

latency_per_action_per_region = {}
canary_per_region = {}
high_tput_per_customer = {}
high_tput_per_symbol = {}
high_tput_per_region = {}
db_error_per_region = {}
model_error_per_region = {}
skew_market_factor_per_symbol = {}

customers = ['b.smith', 'l.johnson', 'j.casey', 'l.hall', 'q.bert', 'carol.halley']
symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC']
regions = ['NA', 'LATAM', 'EU', 'EMEA']

def generate_trade_request(*, customer_id, symbol, day_of_week, region, latency_amount, latency_action, error_model, error_db, skew_market_factor, canary, data_source):
    try:
        trade_response = requests.post(f"http://{os.environ['TRADER_HOST']}:9001/trade/request", 
                                       params={'symbol': symbol, 
                                               'day_of_week': day_of_week, 
                                               'customer_id': customer_id, 
                                               'latency_amount': latency_amount,
                                               'latency_action': latency_action,
                                               'region': region,
                                               'error_model': error_model,
                                               'error_db': error_db,
                                               'skew_market_factor': skew_market_factor,
                                               'canary': canary,
                                               'data_source': data_source},
                                       timeout=TRADE_TIMEOUT)
        trade_response.raise_for_status()
    except Exception as inst:
        print(inst)

def generate_trade_requests():
    idx_of_week = 0
    day_start = 0
    next_region = None
    next_customer = None
    next_symbol = None
    
    while True:
        now = time.time()
        if now - day_start >= S_PER_DAY:
            idx_of_week = (idx_of_week + 1) % len(DAYS_OF_WEEK)
            print(f"advance to {DAYS_OF_WEEK[idx_of_week]}")
            day_start = now

        sleep = float(random.randint(1, 1000) / 1000)
        
        region = next_region if next_region is not None else random.choice(regions)
        symbol = next_symbol if next_symbol is not None else random.choice(symbols)
        customer_id = next_customer if next_customer is not None else random.choice(customers)

        if region in latency_per_action_per_region:
            latency_amount = random.randint(latency_per_action_per_region[region]['amount']-50, latency_per_action_per_region[region]['amount']+50) / 1000.0
            latency_action = latency_per_action_per_region[region]['action']
        else:
            latency_amount = 0
            latency_action = None

        if region in model_error_per_region:
            error_model = True if random.randint(0, 100) > (100-model_error_per_region[region]) else False
        else:
            error_model = False

        if region in db_error_per_region:
            error_db = True if random.randint(0, 100) > (100-db_error_per_region[region]) else False
        else:
            error_db = False

        if symbol in skew_market_factor_per_symbol:
            skew_market_factor = skew_market_factor_per_symbol[symbol]
        else:
            skew_market_factor = 0

        if region in canary_per_region:
            canary = "true"
        else:
            canary = "false"

        print(f"trading {symbol} for {customer_id} on {DAYS_OF_WEEK[idx_of_week]} from {region} with latency {latency_amount}, error_model={error_model}, error_db={error_db}, skew_market_factor={skew_market_factor}, canary={canary}")

        generate_trade_request(customer_id=customer_id, symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week], region=region,
                    latency_amount=latency_amount, latency_action=latency_action, error_model=error_model, error_db=error_db, skew_market_factor=skew_market_factor, canary=canary,
                    data_source='monkey')
        
        if len(high_tput_per_region.keys()) > 0:
            next_high_tput_region = random.choice(list(high_tput_per_region.keys()))
            next_region = next_high_tput_region if random.randint(0, 100) > (100-high_tput_per_region[next_high_tput_region]) else None
            if next_region is not None:
                sleep = float(random.randint(1, 4) / 1000)
        
        if len(high_tput_per_customer.keys()) > 0:
            next_high_tput_customer = random.choice(list(high_tput_per_customer.keys()))
            next_customer = next_high_tput_customer if random.randint(0, 100) > (100-high_tput_per_customer[next_high_tput_customer]) else None
            if next_customer is not None:
                sleep = float(random.randint(1, 4) / 1000)

        if len(high_tput_per_symbol.keys()) > 0:
            next_high_tput_symbol = random.choice(list(high_tput_per_symbol.keys()))
            next_symbol = next_high_tput_symbol if random.randint(0, 100) > (100-high_tput_per_symbol[next_high_tput_symbol]) else None
            if next_symbol is not None:
                sleep = float(random.randint(1, 4) / 1000)

        time.sleep(sleep)

Thread(target=generate_trade_requests, daemon=False).start()

@app.route('/health')
def health():
    return f"KERNEL OK"

@app.post('/reset/market')
def reset_market():
    global high_tput_per_customer
    global high_tput_per_symbol
    global high_tput_per_region
    global skew_market_factor_per_symbol
    
    high_tput_per_customer = {}
    high_tput_per_symbol = {}
    high_tput_per_region = {}
    skew_market_factor_per_symbol = {}
    
    app.logger.info(f"market reset")
    return None

@app.post('/reset/error')
def reset_error():
    global latency_per_action_per_region
    global db_error_per_region
    global model_error_per_region
    
    latency_per_action_per_region = {}
    db_error_per_region = {}
    model_error_per_region = {}
    
    app.logger.info(f"error reset")
    return None

@app.post('/reset/test')
def test_error():
    global canary_per_region

    canary_per_region = {}
    
    app.logger.info(f"test reset")
    return None

@app.get('/state')
def get_state():
    state = {
        'days_of_week': DAYS_OF_WEEK,
        'customers': customers,
        'symbols': symbols,
        'regions': regions,
        
        'latency_per_action_per_region': latency_per_action_per_region,
        'canary_per_region': canary_per_region,
        'high_tput_per_customer': high_tput_per_customer,
        'high_tput_per_symbol': high_tput_per_symbol,
        'high_tput_per_region': high_tput_per_region,
        'db_error_per_region': db_error_per_region,
        'model_error_per_region': model_error_per_region,
        'skew_market_factor_per_symbol': skew_market_factor_per_symbol
    }
    return state

@app.post('/tput/region/<region>/<speed>')
def tput_region(region, speed):
    global high_tput_per_region
    high_tput_per_region[region] = 50
    return high_tput_per_region
@app.delete('/tput/region/<region>')
def tput_region_delete(region):
    if region in high_tput_per_region:
        del high_tput_per_region[region]
    return high_tput_per_region

@app.post('/tput/customer/<customer>/<speed>')
def tput_customer(customer, speed):
    global high_tput_per_customer
    high_tput_per_customer[customer] = 50
    return high_tput_per_customer
@app.delete('/tput/customer/<customer>')
def tput_customer_delete(customer):
    if customer in high_tput_per_customer:
        del high_tput_per_customer[customer]
    return high_tput_per_customer

@app.post('/tput/symbol/<symbol>/<speed>')
def tput_symbol(symbol, speed):
    global high_tput_per_symbol
    high_tput_per_symbol[symbol] = 50
    return high_tput_per_symbol
@app.delete('/tput/symbol/<symbol>')
def tput_symbol_delete(symbol):
    global high_tput_per_symbol
    if symbol in high_tput_per_symbol:
        del high_tput_per_symbol[symbol]
    return high_tput_per_symbol

@app.post('/latency/region/<region>/<amount>')
def latency_region(region, amount):
    global latency_per_action_per_region
    latency_action = request.args.get('latency_action', default=None, type=str)
    latency_per_action_per_region[region] = {'action': latency_action, 'amount': int(amount)}
    high_tput_per_region[region] = 90
    return latency_per_action_per_region    
@app.delete('/latency/region/<region>')
def latency_region_delete(region):
    global latency_per_action_per_region
    if region in latency_per_action_per_region:
        del latency_per_action_per_region[region]
    if region in high_tput_per_region:
        del high_tput_per_region[region]
    return latency_per_action_per_region    

@app.post('/err/db/region/<region>/<amount>')
def err_db_region(region, amount):
    global db_error_per_region
    db_error_per_region[region] = int(amount)
    high_tput_per_region[region] = 90
    return db_error_per_region
@app.delete('/err/db/region/<region>')
def err_db_region_delete(region):
    global db_error_per_region
    if region in db_error_per_region:
        del db_error_per_region[region]
    if region in high_tput_per_region:
        del high_tput_per_region[region]
    return db_error_per_region

@app.post('/err/model/region/<region>/<amount>')
def err_model_region(region, amount):
    global model_error_per_region
    model_error_per_region[region] = int(amount)
    high_tput_per_region[region] = 90
    return model_error_per_region    
@app.delete('/err/model/region/<region>')
def err_model_region_delete(region):
    global model_error_per_region
    if region in model_error_per_region:
        del model_error_per_region[region]
    if region in high_tput_per_region:
        del high_tput_per_region[region]
    return model_error_per_region

@app.post('/skew_market_factor/symbol/<symbol>/<amount>')
def skew_market_factor_symbol(symbol, amount):
    global skew_market_factor_per_symbol
    skew_market_factor_per_symbol[symbol] = int(amount)
    return skew_market_factor_per_symbol
@app.delete('/skew_market_factor/symbol/<symbol>')
def skew_pr_symbol_delete(symbol):
    global skew_market_factor_per_symbol
    if symbol in skew_market_factor_per_symbol:
        del skew_market_factor_per_symbol[symbol]
    return skew_market_factor_per_symbol

@app.post('/canary/region/<region>')
def canary_region(region):
    global canary_per_region
    canary_per_region[region] = True
    return canary_per_region    
@app.delete('/canary/region/<region>')
def canary_region_delete(region):
    global canary_per_region
    if region in canary_per_region:
        del canary_per_region[region]
    return canary_per_region  

def generate_trade_force(*, customer_id, day_of_week, region, symbol, action, shares, share_price, data_source, classification):
    try:
        trade_response = requests.post(f"http://{os.environ['TRADER_HOST']}:9001/trade/force", 
                                       params={'symbol': symbol,
                                               'day_of_week': day_of_week, 
                                               'shares': shares, 
                                               'action': action,
                                               'region': region,
                                               'customer_id': customer_id,
                                               'share_price': share_price,
                                               'data_source': data_source,
                                               'classification': classification
                                               },
                                       timeout=TRADE_TIMEOUT)
        trade_response.raise_for_status()
    except Exception as inst:
        print(inst)

def generate_trades(*, fixed_day_of_week=None, fixed_region = None, fixed_symbol = None,
                    fixed_action = None, fixed_shares_min = None, fixed_shares_max = None, 
                    fixed_share_price_min = None, fixed_share_price_max = None, classification):

    if fixed_day_of_week is None:
        idx_of_week = 0
    else:
        idx_of_week = DAYS_OF_WEEK.index(fixed_day_of_week)
    
    for x in range(0, TRAINING_TRADE_COUNT):
        
        trade_classification = f"not {classification}"
        
        idx_of_week = DAYS_OF_WEEK.index(random.choice(DAYS_OF_WEEK))
        if fixed_day_of_week is not None and DAYS_OF_WEEK.index(fixed_day_of_week) == idx_of_week:
            trade_classification = classification

        region = random.choice(regions)
        if fixed_region is not None and fixed_region == region:
            trade_classification = classification
 
        symbol = random.choice(symbols)
        if fixed_symbol is not None and fixed_symbol == symbol:
            trade_classification = classification

        customer_id = random.choice(customers)
        
        action = random.choice(ACTIONS)
        if fixed_action is not None and fixed_action == action:
            trade_classification = classification

        shares = random.randint(1, 100)
        if fixed_shares_min is not None and shares >= fixed_shares_min and shares <= fixed_shares_max:
            trade_classification = classification

        share_price = random.randint(1, 1000)
        if fixed_share_price_min is not None and share_price >= fixed_share_price_min and share_price <= fixed_share_price_max:
            trade_classification = classification

        print(f"training {symbol} for {customer_id} on {DAYS_OF_WEEK[idx_of_week]} from {region}, classification {trade_classification}")

        generate_trade_force(symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week], region=region, customer_id=customer_id,
                             action=action, shares=shares, share_price=share_price, classification=trade_classification,
                             data_source='training')

        sleep = float(random.randint(1, 10) / 1000)
        time.sleep(sleep)

@app.post('/train/<classification>')
def train_label(classification):

    day_of_week = request.args.get('day_of_week', default=None, type=str)
    region = request.args.get('region', default=None, type=str)
    symbol = request.args.get('symbol', default=None, type=str)
    action = request.args.get('action', default=None, type=str)
    shares_min = request.args.get('shares_min', default=None, type=int)
    shares_max = request.args.get('shares_max', default=None, type=int)
    share_price_min = request.args.get('share_price_min', default=None, type=float)
    share_price_max = request.args.get('share_price_max', default=None, type=float)
    
    generate_trades(fixed_day_of_week=day_of_week, fixed_region = region, fixed_symbol = symbol,
                    fixed_action = action, fixed_shares_min = shares_min, fixed_shares_max = shares_max, 
                    fixed_share_price_min=share_price_min, fixed_share_price_max=share_price_max, 
                    classification=classification)
    
    return None
