import requests
import os
import json

TIMEOUT = 10

SLO_RESOURCES_PATH  = 'slo'

def delete(id):
    res = requests.delete(f"{os.environ['KIBANA_URL']}/api/observability/slos/{id}",
                                    timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    print(res)

def clear():
    slos = requests.get(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    for slo in slos.json()['results']:
        delete(slo['id'])
        
def exists(name):
    slos = requests.get(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    for slo in slos.json()['results']:
        if slo['name'] == name:
            return slo['id']
    return None


def load():

    for file in os.listdir(SLO_RESOURCES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(SLO_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                body = f.read()
                
                id = exists(json.loads(body)['name'])
                if id is not None:
                    print('found, deleting old slo')
                    delete(id)

                resp = requests.post(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
                print(resp.json())  
                