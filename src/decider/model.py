import random
from app import app

MARKET_WINDOW_SIZE = 5
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

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def reset_market_data():
    global market_data
    market_data = {}

def sim_market_data(*, symbol, day_of_week, skew_market_factor=0):
    global market_data
    
    market_factor = 0
    
    if day_of_week == 'M':
        market_factor = random.randint(-100, 25)
    elif day_of_week == 'Tu':
        market_factor = random.randint(-75, 50)
    elif day_of_week == 'W':
        market_factor = random.randint(-50, 50)
    elif day_of_week == 'Th':
        market_factor = random.randint(-25, 75)
    elif day_of_week == 'F':
        market_factor = random.randint(0, 100)
        
    market_factor += skew_market_factor
    market_factor = clamp(market_factor, -100, 100)
    app.logger.info(f"market_factor: {symbol}={market_factor}")
        
    initial_idx = hash(symbol) % len(market_data_seed)
    if symbol not in market_data:
        share_price = market_data_seed[initial_idx]
        market_data[symbol] = StreamingMovingAverage(window_size=MARKET_WINDOW_SIZE)
        app.logger.info(f"initial share price for {symbol}: ${'{0:0.2f}'.format(share_price)}, idx={initial_idx}")
    else:
        current_share_price = market_data[symbol].get()
        share_price = current_share_price + (current_share_price * (float(market_factor) / 100.0))
        share_price = clamp(share_price, random.randint(1, 100), random.randint(900, 1000))

    smoothed_share_price = round(market_data[symbol].process(share_price), 2)
    app.logger.info(f"current market share price for {symbol}: ${'{0:0.2f}'.format(smoothed_share_price)}")

    return market_factor, smoothed_share_price

def sim_decide(*, symbol, market_factor):

    action = 'hold'
    shares = 0
    if market_factor <= -25:
        action = 'sell'
        if market_factor <= -75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)
    elif market_factor >= 25:
        action = 'buy'
        if market_factor >= 75:
            shares = random.randint(50, 100)
        else:
            shares = random.randint(1, 50)

    return action, shares
    