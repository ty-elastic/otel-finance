import requests
import random
import time
import os

def generate_trade(*, symbol, day_of_week):
    try:
        trade_response = requests.post(f"http://{os.environ['DECIDER_HOST']}:9001/decide", params={'symbol': symbol, 'day_of_week': day_of_week})
        trade_response.raise_for_status()
    except Exception as inst:
        print(inst)

def generate_trades():
    symbols = ['MOT', 'MSI', 'GOGO', 'INTEQ', 'VID', 'ESTC']
    day_of_week = 1
    
    while True:
        day_of_week = ((day_of_week + 1) % 6)
        trades_per_day = random.randint(0, 100)
        for i in range(trades_per_day):
            symbol = symbols[random.randint(0, len(symbols)-1)]
            if random.randint(0, 100) > 80:
                symbol = 'ERR'
            print(f"trading for {symbol} on {day_of_week}, count={i}")
            generate_trade(symbol=symbol, day_of_week=day_of_week)
            latency = float(random.randint(1, 50)) / 100.0
            time.sleep(latency)

if __name__ == '__main__':
    generate_trades()