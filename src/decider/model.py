import random
from app import app

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

market_data_seed = [random.randint(10, 25), random.randint(25, 75), random.randint(75, 100)]
market_data = {}

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def reset_market_data():
    global market_data
    market_data = {}

def sim_market_data(*, symbol, day_of_week, skew_pr_volume=0):
    global market_data
    
    pr_volume = 0
    
    if day_of_week == 'M':
        pr_volume = random.randint(-100, 25)
    elif day_of_week == 'Tu':
        pr_volume = random.randint(-75, 50)
    elif day_of_week == 'W':
        pr_volume = random.randint(-50, 50)
    elif day_of_week == 'Th':
        pr_volume = random.randint(-50, 75)
    elif day_of_week == 'F':
        pr_volume = random.randint(-25, 100)
        
    pr_volume += skew_pr_volume
    pr_volume = clamp(pr_volume, -100, 100)
    app.logger.info(f"pr_volume: {symbol}={pr_volume}")
        
    initial_idx = hash(symbol) % len(market_data_seed)
    if symbol not in market_data:
        share_price = market_data_seed[initial_idx]
        market_data[symbol] = StreamingMovingAverage(window_size=10)
        app.logger.info(f"initial share price for {symbol}: ${'{0:0.2f}'.format(share_price)}, idx={initial_idx}")
    else:
        current_share_price = market_data[symbol].get()
        share_price = current_share_price + (current_share_price * (float(pr_volume) / 100.0))
        if share_price < 1:
            share_price = market_data_seed[initial_idx] * abs(pr_volume / 100)
            app.logger.info(f"reset market share price for{symbol}: ${'{0:0.2f}'.format(share_price)}")
    
    smoothed_share_price = market_data[symbol].process(share_price)
    app.logger.info(f"current market share price for {symbol}: ${'{0:0.2f}'.format(smoothed_share_price)}")

    return pr_volume, smoothed_share_price

def sim_decide(*, symbol, pr_volume):
    
    action = 'hold'
    shares = 0
    if pr_volume <= -25:
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
    