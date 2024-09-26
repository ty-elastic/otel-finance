from flask import Flask, request
import logging
import requests
import random
import time
import os
from threading import Thread

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

TRADE_TIMEOUT = 5
DAYS_OF_WEEK = ['M','Tu', 'W', 'Th', 'F']
S_PER_DAY = 60

high_latency_region = None

high_tput_customer = None
high_tput_symbol = None
high_tput_region = None

db_error_region = None
model_error_region = None

customers = ['b.smith', 'l.johnson', 'j.casey', 'l.hall', 'q.bert']
symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC']
regions = ['NA', 'LATAM', 'EU']

def generate_trade(*, customer_id, symbol, day_of_week, region, latency, error_model, error_db):
    try:
        trade_response = requests.post(f"http://{os.environ['DECIDER_HOST']}:9001/decide", 
                                       params={'symbol': symbol, 
                                               'day_of_week': day_of_week, 
                                               'customer_id': customer_id, 
                                               'latency': latency,
                                               'region': region,
                                               'error_model': error_model,
                                               'error_db': error_db},
                                       timeout=TRADE_TIMEOUT)
        trade_response.raise_for_status()
    except Exception as inst:
        print(inst)

def generate_trades():
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
        else:
            sleep = float(random.randint(1, 1000) / 1000)
            
            region = next_region if next_region is not None else random.choice(regions)
            symbol = next_symbol if next_symbol is not None else random.choice(symbols)
            customer_id = next_customer if next_customer is not None else random.choice(customers)

            if high_latency_region == region:
                latency = random.randint(50, 60) / 100.0
            else:
                latency = 0

            if model_error_region == region:
                error_model = True if random.randint(0, 100) > 20 else False
            else:
                error_model = False

            if db_error_region == region:
                error_db = True if random.randint(0, 100) > 30 else False
            else:
                error_db = False

            print(f"trading {symbol} for {customer_id} on {DAYS_OF_WEEK[idx_of_week]} from {region} with latency {latency}, error_model={error_model}, error_db={error_db}")

            generate_trade(customer_id=customer_id, symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week], region=region, 
                        latency=latency, error_model=error_model, error_db=error_db)
            
            if high_tput_region is not None:
                next_region = high_tput_region if random.randint(0, 100) > 50 else None
                if next_region is not None:
                    sleep = float(random.randint(1, 10) / 1000)
            
            if high_tput_customer is not None:
                next_customer = high_tput_customer if random.randint(0, 100) > 50 else None
                if next_customer is not None:
                    sleep = float(random.randint(1, 10) / 1000)

            if high_tput_symbol is not None:
                next_symbol = high_tput_symbol if random.randint(0, 100) > 50 else None
                if next_symbol is not None:
                    sleep = float(random.randint(1, 10) / 1000)

            time.sleep(sleep)


Thread(target=generate_trades, daemon=False).start()

@app.post('/tput/region/<region>/<speed>')
def tput_region(region, speed):
    global high_tput_region
    if speed == 'default':
        high_tput_region = None
    elif speed == 'high':
        high_tput_region = region
    return {'region': region, 'speed': speed}

@app.post('/tput/customer/<customer>/<speed>')
def tput_customer(customer, speed):
    global high_tput_customer
    if speed == 'default':
        high_tput_customer = None
    elif speed == 'high':
        high_tput_customer = customer
    return {'customer': customer, 'speed': speed}

@app.post('/tput/symbol/<symbol>/<speed>')
def tput_symbol(symbol, speed):
    global high_tput_symbol
    if speed == 'default':
        high_tput_symbol = None
    elif speed == 'high':
        high_tput_symbol = symbol
    return {'symbol': symbol, 'speed': speed}

@app.post('/latency/region/<region>/<latency>')
def latency_region(region, amount):
    global high_latency_region
    if amount == 'none':
        high_latency_region = None
    elif amount == 'high':
        high_latency_region = region
    return {'region': region, 'amount': amount}

@app.post('/err/db/region/<region>/<amount>')
def err_db_region(region, amount):
    global db_error_region
    if amount == 'none':
        db_error_region = None
    elif amount == 'high':
        db_error_region = region
    return {'region': region, 'amount': amount}

@app.post('/err/model/region/<region>/<amount>')
def err_model_region(region, amount):
    global model_error_region
    if amount == 'none':
        model_error_region = None
    elif amount == 'high':
        model_error_region = region
    return {'region': region, 'amount': amount}
