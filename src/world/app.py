from flask import Flask, request
import logging
import requests
import random
import time
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

def generate_trade(*, symbol, day_of_week):
    try:
        trade_response = requests.post(f"http://{os.environ['DECIDER_HOST']}:9001/decide", params={'symbol': symbol, 'day_of_week': day_of_week})
        trade_response.raise_for_status()
    except Exception as inst:
        print(inst)

DAYS_OF_WEEK = ['M','Tu', 'W', 'Th', 'F']

latency_upper_bound = 50
error_rate = 10

def generate_trades():
    symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC', 'OD1', 'OD2']
    idx_of_week = 0
    
    while True:
        idx_of_week = (idx_of_week + 1) % len(DAYS_OF_WEEK)
        trades_per_day = random.randint(0, 100)
        for i in range(trades_per_day):
            symbol = symbols[random.randint(0, len(symbols)-1)]
            if random.randint(0, 100) > (100-error_rate):
                symbol = 'ERR'
            print(f"trading for {symbol} on {DAYS_OF_WEEK[idx_of_week]}, count={i}")
            generate_trade(symbol=symbol, day_of_week=DAYS_OF_WEEK[idx_of_week])
            latency = float(random.randint(0, latency_upper_bound)) / 1000.0
            time.sleep(latency)

@app.post('/tput/fast')
def tput_fast():
    global latency_upper_bound
    latency_upper_bound = 1
    return {'KERNEL': 'OK'}
    
@app.post('/tput/default')
def tput_default():
    global latency_upper_bound
    latency_upper_bound = 50
    return {'KERNEL': 'OK'}
    
@app.post('/err/high')
def err_high():
    global latency_upper_bound
    error_rate = 75
    return {'KERNEL': 'OK'}
    
@app.post('/err/default')
def err_default():
    global latency_upper_bound
    error_rate = 10
    return {'KERNEL': 'OK'}
