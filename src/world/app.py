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

DAYS_OF_WEEK = ['M','Tu', 'W', 'Th', 'F']

latency_upper_bound = 50
error_rate = 10

latency_region = None

customers = ['b.smith','l.johnson','j.casey','l.hall','q.bert']
symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC', 'OD1', 'OD2']
regions = ['NA', 'LATAM', "EU"]

def generate_trades():
    global latency_region
    
    idx_of_week = 0
    
    while True:
        idx_of_week = (idx_of_week + 1) % len(DAYS_OF_WEEK)
        region = random.choice(regions)
        if latency_region == region:
            latency = random.randint(50, 60) / 100.0
        else:
            latency = 0
        trades_per_day = random.randint(0, 100)
        for i in range(trades_per_day):
            symbol = random.choice(symbols)
            if random.randint(0, 100) > (100-error_rate):
                symbol = 'ERR'
            customer = random.choice(customers)
            print(f"trading {symbol} for {customer} on {DAYS_OF_WEEK[idx_of_week]}, count={i}")
            error_model = False
            error_db = False    
            generate_trade(customer_id=customer, symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week], region=region, 
                           latency=latency, error_model=error_model, error_db=error_db)
            sleep = float(random.randint(0, latency_upper_bound)) / 1000.0
            time.sleep(sleep)

Thread(target=generate_trades, daemon=False).start()

# @app.post('/tput/fast')
# def tput_fast():
#     global latency_upper_bound
#     latency_upper_bound = 1
#     return {'KERNEL': 'OK'}
    
# @app.post('/tput/default')
# def tput_default():
#     global latency_upper_bound
#     latency_upper_bound = 50
#     return {'KERNEL': 'OK'}
    
# @app.post('/err/high')
# def err_high():
#     global error_rate
#     error_rate = 75
#     return {'KERNEL': 'OK'}
    
# @app.post('/err/default')
# def err_default():
#     global error_rate
#     error_rate = 10
#     return {'KERNEL': 'OK'}

# @app.post('/latency/high')
# def latency_high():
#     global latency
#     latency = True
#     return {'KERNEL': 'OK'}
    
# @app.post('/latency/default')
# def latency_default():
#     global latency
#     latency = False
#     return {'KERNEL': 'OK'}