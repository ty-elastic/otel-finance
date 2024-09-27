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

latency_per_region = {}

high_tput_per_customer = {}
high_tput_per_symbol = {}
high_tput_per_region = {}

db_error_per_region = {}
model_error_per_region = {}

skew_pr_volume_per_symbol = {}

customers = ['b.smith', 'l.johnson', 'j.casey', 'l.hall', 'q.bert']
symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC']
regions = ['NA', 'LATAM', 'EU']

def generate_trade(*, customer_id, symbol, day_of_week, region, latency, error_model, error_db, skew_pr_volume):
    try:
        trade_response = requests.post(f"http://{os.environ['DECIDER_HOST']}:9001/decide", 
                                       params={'symbol': symbol, 
                                               'day_of_week': day_of_week, 
                                               'customer_id': customer_id, 
                                               'latency': latency,
                                               'region': region,
                                               'error_model': error_model,
                                               'error_db': error_db,
                                               'skew_pr_volume': skew_pr_volume},
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

            if region in latency_per_region:
                latency = random.randint(latency_per_region[region]-100, latency_per_region[region]+100) / 1000.0
            else:
                latency = 0

            if region in model_error_per_region:
                error_model = True if random.randint(0, 100) > (100-model_error_per_region[region]) else False
            else:
                error_model = False

            if region in db_error_per_region:
                error_db = True if random.randint(0, 100) > (100-db_error_per_region[region]) else False
            else:
                error_db = False

            if symbol in skew_pr_volume_per_symbol:
                skew_pr_volume = skew_pr_volume_per_symbol[symbol]
            else:
                skew_pr_volume = 0
 
            print(f"trading {symbol} for {customer_id} on {DAYS_OF_WEEK[idx_of_week]} from {region} with latency {latency}, error_model={error_model}, error_db={error_db}, skew_pr_volume={skew_pr_volume}")

            generate_trade(customer_id=customer_id, symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week], region=region,
                        latency=latency, error_model=error_model, error_db=error_db, skew_pr_volume=skew_pr_volume)
            
            if len(high_tput_per_region.keys()) > 0:
                next_region = random.choice(list(high_tput_per_region.keys())) if random.randint(0, 100) > 50 else None
                if next_region is not None:
                    sleep = float(random.randint(1, 10) / 1000)
            
            if len(high_tput_per_customer.keys()) > 0:
                next_customer = random.choice(list(high_tput_per_customer.keys())) if random.randint(0, 100) > 50 else None
                if next_customer is not None:
                    sleep = float(random.randint(1, 10) / 1000)

            if len(high_tput_per_symbol.keys()) > 0:
                next_symbol = random.choice(list(high_tput_per_symbol.keys())) if random.randint(0, 100) > 50 else None
                if next_symbol is not None:
                    sleep = float(random.randint(1, 10) / 1000)

            time.sleep(sleep)

Thread(target=generate_trades, daemon=False).start()

@app.post('/tput/region/<region>/<speed>')
def tput_region(region, speed):
    global high_tput_per_region
    high_tput_per_region[region] = speed
    return high_tput_per_region
@app.delete('/tput/region/<region>')
def tput_region_delete(region):
    if region in high_tput_per_region:
        del high_tput_per_region[region]
    return high_tput_per_region

@app.post('/tput/customer/<customer>/<speed>')
def tput_customer(customer, speed):
    global high_tput_per_customer
    high_tput_per_customer[customer] = speed
    return high_tput_per_customer
@app.delete('/tput/customer/<customer>')
def tput_customer_delete(customer):
    if customer in high_tput_per_customer:
        del high_tput_per_customer[customer]
    return high_tput_per_customer

@app.post('/tput/symbol/<symbol>/<speed>')
def tput_symbol(symbol, speed):
    global high_tput_per_symbol
    high_tput_per_symbol[symbol] = speed
    return high_tput_per_symbol
@app.delete('/tput/symbol/<symbol>')
def tput_symbol_delete(symbol):
    global high_tput_per_symbol
    if symbol in high_tput_per_symbol:
        del high_tput_per_symbol[symbol]
    return high_tput_per_symbol

@app.post('/latency/region/<region>/<amount>')
def latency_region(region, amount):
    global latency_per_region
    latency_per_region[region] = int(amount)
    return latency_per_region    
@app.delete('/latency/region/<region>')
def latency_region_delete(region):
    global latency_per_region
    if region in latency_per_region:
        del latency_per_region[region]
    return latency_per_region    

@app.post('/err/db/region/<region>/<amount>')
def err_db_region(region, amount):
    global db_error_per_region
    db_error_per_region[region] = int(amount)
    return db_error_per_region
@app.delete('/err/db/region/<region>')
def err_db_region_delete(region):
    global db_error_per_region
    if region in db_error_per_region:
        del db_error_per_region[region]
    return db_error_per_region

@app.post('/err/model/region/<region>/<amount>')
def err_model_region(region, amount):
    global model_error_per_region
    model_error_per_region[region] = int(amount)
    return model_error_per_region    
@app.delete('/err/model/region/<region>')
def err_model_region_delete(region):
    global model_error_per_region
    if region in model_error_per_region:
        del model_error_per_region[region]
    return model_error_per_region

@app.post('/pr/symbol/<symbol>/<amount>')
def skew_pr_symbol(symbol, amount):
    global skew_pr_volume_per_symbol
    skew_pr_volume_per_symbol[symbol] = int(amount)
    return skew_pr_volume_per_symbol
@app.delete('/pr/symbol/<symbol>')
def skew_pr_symbol_delete(symbol):
    global skew_pr_volume_per_symbol
    if symbol in skew_pr_volume_per_symbol:
        del skew_pr_volume_per_symbol[symbol]
    return skew_pr_volume_per_symbol
