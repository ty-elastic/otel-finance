import requests
import os

TIMEOUT = 10

SLO_RESOURCES_PATH  = 'slo'

def load():

    for file in os.listdir(SLO_RESOURCES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(SLO_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                body = f.read()

                resp = requests.post(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
                print(resp.json())  
