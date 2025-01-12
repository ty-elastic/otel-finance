
import requests
import os
import json
from pathlib import Path

TIMEOUT = 10

CASE_RESOURCES_PATH  = 'case'

def delete_case(id):
    res = requests.delete(f"{os.environ['KIBANA_URL']}/api/cases?ids={id}",
                                    timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    print(res)

def case_exists(title):
    cases = requests.get(f"{os.environ['KIBANA_URL']}/api/cases/_find",
                                     timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    if 'results' in cases.json():
        for case in cases.json()['cases']:
            if case['title'] == title:
                return case['id']
    return None

def load(case_name):

    file = f"{case_name}.json"
        
    with open(os.path.join(CASE_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
        body = json.load(f)

        id = case_exists(case_name)
        if id is not None:
            print('found, deleting old case')
            delete_case(id)
            
        resp = requests.post(f"{os.environ['KIBANA_URL']}/api/cases",
                                json=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                headers={"kbn-xsrf": "reporting"})
        print(resp.json()) 

def load_all():
    for file in os.listdir(CASE_RESOURCES_PATH):
        if file.endswith(".json"):
            filename = Path(file).stem
            load(filename)

load_all()