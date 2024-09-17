import random
from app import app

def sim_errors(*, day_of_week, symbol):
    
    latency_model = 0
    error_model = False
    error_db = False

    if day_of_week == 'Tu':
        if symbol == 'ERR':
            error_db = True
    elif day_of_week == 'W':
        latency_model = random.randint(50, 60) / 100.0
    elif day_of_week == 'Th' or day_of_week == 'F':
        if symbol == 'ERR':
            error_model = True

    return latency_model, error_model, error_db

market_data_seed = [random.randint(10, 25), random.randint(25, 75), random.randint(75, 100)]
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
        pr_volume = random.randint(-100, 0)
    elif day_of_week == 'M':
        pr_volume = random.randint(-100, 25)
    elif day_of_week == 'Tu':
        pr_volume = random.randint(-75, 50)
    elif day_of_week == 'W':
        pr_volume = random.randint(-50, 50)
    elif day_of_week == 'Th':
        pr_volume = random.randint(-50, 75)
    elif day_of_week == 'F':
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
    shares = 0
    if symbol == 'OD2':
        action = 'buy'
        shares = random.randint(90, 100)
    elif pr_volume <= -25:
        action = 'sell'
        if pr_volume <= -75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)
    elif pr_volume >= 25:
        action = 'buy'
        if pr_volume >= 75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)

    return action, shares
    