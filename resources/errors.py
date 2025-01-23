import requests
import os
import base64

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

def create_db_errors(customer_id, amount, service):
    try:
        print(f'generating db errors for {customer_id}')

        #customer_id_encoded_string = (base64.b64encode(customer_id.encode('utf-8'))).decode('utf-8')

        resp = requests.post(f"http://monkey:9002/err/db/customer/{customer_id}/{amount}",
                                timeout=TIMEOUT,
                                params={'latency_oneshot': False, 'err_db_service': service})
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
        result = create_db_errors('l.hall', 100, 'recorder-java')
        if result is False:
            return result

    return True
