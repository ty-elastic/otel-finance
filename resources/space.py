
import requests
import os
import json
from pathlib import Path

TIMEOUT = 10

SPACE_RESOURCES_PATH  = 'space'


def update(space_name):

    file = f"{space_name}.json"
        
    with open(os.path.join(SPACE_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
        body = json.load(f)

        resp = requests.put(f"{os.environ['KIBANA_URL']}/api/spaces/space/{space_name}",
                                json=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                headers={"kbn-xsrf": "reporting"})
        print(resp.json()) 

def load_all():
    for file in os.listdir(SPACE_RESOURCES_PATH):
        if file.endswith(".json"):
            filename = Path(file).stem
            update(filename)

#load_all()