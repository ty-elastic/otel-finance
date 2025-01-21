import requests
import os

TIMEOUT = 1

def create_latency(region, amount):
    try:
        print(f'generating latency for {region}')
        resp = requests.post(f"http://monkey:9002/latency/region/{region}/{amount}",
                                timeout=TIMEOUT,
                                params={'latency_oneshot': False})
        print(resp)
        return True
    except Exception as inst:
        return False

def create_db_errors(customer_id, amount):
    try:
        print(f'generating db errors for {customer_id}')
        resp = requests.post(f"http://monkey:9002/err/db/customer/{customer_id}/{amount}",
                                timeout=TIMEOUT,
                                params={'latency_oneshot': False})
        print(resp)
        return True
    except Exception as inst:
        return False

def load():
    result = False

    if os.environ['ERRORS_LATENCY'] == 'true':
        result = create_latency('LATAM', 800)
        if result is False:
            return result

    if os.environ['ERRORS_DB'] == 'true':
        result = create_db_errors('l.hall', 100)
        if result is False:
            return result

    return True
