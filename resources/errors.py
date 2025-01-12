import requests

TIMEOUT = 1

def create_latency(region, amount):
    try:
        print('generating latency')
        resp = requests.post(f"http://monkey:9002/latency/region/{region}/{amount}",
                                timeout=TIMEOUT,
                                params={'latency_oneshot': False})
        print(resp)
        return True
    except Exception as inst:
        return False

def load():
    return create_latency('LATAM', 800)
