import os
from elasticsearch import Elasticsearch
from pathlib import Path

TIMEOUT = 10

ALIAS_RESOURCES_PATH  = 'alias'

def load():

    for index in os.listdir(ALIAS_RESOURCES_PATH):
        index_path = os.path.join(ALIAS_RESOURCES_PATH, index)
        for file in os.listdir(index_path):
            
            if file.endswith(".json"):
                with open(os.path.join(index_path, file), "rt", encoding='utf8') as f:
                    body = f.read()
                    filename = Path(file).stem
                    
                    with Elasticsearch(os.environ['ELASTICSEARCH_URL'], basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD'])) as client:
                        resp = client.indices.exists(index=index)
                        if resp:
                            print(f"{index} found, creating alias")
                            resp = client.indices.put_alias(index=index, name=filename, body=body)
                            print(resp)
                            return True
                        else:
                            print(f"{index} not yet found...")
                            return False
