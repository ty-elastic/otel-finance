import requests
import os
import json
from pathlib import Path

TIMEOUT = 10

SLO_RESOURCES_PATH  = 'slo'

def delete_slo(id):
    res = requests.delete(f"{os.environ['KIBANA_URL']}/api/observability/slos/{id}",
                                    timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    print(res)

def delete_all():
    slos = requests.get(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    if 'results' in slos.json():
        for slo in slos.json()['results']:
            delete_slo(slo['id'])
    else:
        print(slos)

def slo_exists(name):
    slos = requests.get(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    if 'results' in slos.json():
        for slo in slos.json()['results']:
            if slo['name'] == name:
                return slo['id']
    return None
               
def delete_alert(id):
    res = requests.delete(f"{os.environ['KIBANA_URL']}/api/alerting/rule/{id}",
                                    timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    print(res)    
         
def alert_exists(name):
    rules = requests.get(f"{os.environ['KIBANA_URL']}/api/alerting/rules/_find",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    for rule in rules.json()['data']:
        print(rule)
        if rule['name'] == name:
            return rule['id']
    return None


def load(slo_name):
    slo_ids = {}
    
    file = f"{slo_name}.json"
        
    with open(os.path.join(SLO_RESOURCES_PATH, "slo", file), "rt", encoding='utf8') as f:
        body = json.load(f)

        id = slo_exists(slo_name)
        if id is not None:
            print('found, deleting old slo')
            delete_slo(id)
            
        resp = requests.post(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                json=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                headers={"kbn-xsrf": "reporting"})
        slo_ids[slo_name] = resp.json()['id']
        print(slo_ids)
        print(resp.json()) 

    if os.path.exists(os.path.join(SLO_RESOURCES_PATH, "alert", file)):
        with open(os.path.join(SLO_RESOURCES_PATH, "alert", file), "rt", encoding='utf8') as f:
            body = json.load(f)
            body['params']['sloId'] = slo_ids[slo_name]
            
            id = alert_exists(body['name'])
            print(id)
            if id is not None:
                print('found, deleting old alert')
                delete_alert(id)

            resp = requests.post(f"{os.environ['KIBANA_URL']}/api/alerting/rule",
                                    json=body, timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting"})
            print(resp.json())  
                    
                
def load_all():
    for file in os.listdir(os.path.join(SLO_RESOURCES_PATH, "slo")):
        if file.endswith(".json"):
            filename = Path(file).stem
            load(filename)
                   
#load('trader_availability')