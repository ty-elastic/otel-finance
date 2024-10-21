import requests
import os

TIMEOUT = 10

ASSISTANT_RESOURCES_PATH  = 'assistant'

def load():

    if 'OPENAI_KEY' in os.environ:
        with open(os.path.join(ASSISTANT_RESOURCES_PATH, 'openai.json'), "rt", encoding='utf8') as f:
            body = f.read()
            body = body.replace('$OPENAI_URL', os.environ['OPENAI_URL'])
            body = body.replace('$OPENAI_KEY', os.environ['OPENAI_KEY'])    

            resp = requests.post(f"{os.environ['KIBANA_URL']}/api/actions/connector/d7e8a4a5-a2c0-4814-a397-1f0a37313ac9",
                                    data=body, timeout=TIMEOUT,
                                    auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                    headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
            print(resp.json())     
