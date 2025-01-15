import os
import requests

KIBANA_RESOURCES_PATH = 'kibana'
TIMEOUT = 10

def set_default_dataview(dataview_id):
    body = {
        "force": True,
        "data_view_id": dataview_id
    }

    resp = requests.post(f"{os.environ['KIBANA_URL']}/api/data_views/default",
                            json=body, timeout=TIMEOUT,
                            auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                            headers={"kbn-xsrf": "reporting"},
                            params={'compatibilityMode': True})
    print(resp.json())

#set_default_dataview('logs-*')

def load():

    for file in os.listdir(KIBANA_RESOURCES_PATH):
        if file.endswith(".ndjson"):
            with open(os.path.join(KIBANA_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                dashboards = f.read()
                resp = requests.post(f"{os.environ['KIBANA_URL']}/api/saved_objects/_import",
                                     files={"file": ("export.ndjson", dashboards)}, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                     headers={"kbn-xsrf": "reporting"},
                                     params={'compatibilityMode': True, 'overwrite': True})
                print(resp.json())