import os
import requests
from pathlib import Path
import json

INDICES_RESOURCES_PATH = 'context/indices'
KNOWLEDGE_RESOURCES_PATH = 'context/knowledge'

TIMEOUT = 10
             
def load_index(parent, index):

    with open(os.path.join(parent, "index.json"), "rt", encoding='utf8') as f:
        body = json.load(f)
        resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}",
                                json=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                headers={"kbn-xsrf": "reporting"})
        print(resp.json())
        
def load_pipelines(parent):
    pipelines_path = os.path.join(parent, 'pipelines')
    
    for file in os.listdir(pipelines_path):
        if file.endswith(".json"):
            with open(os.path.join(pipelines_path, file), "rt", encoding='utf8') as f:
                body = json.load(f)
                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_ingest/pipeline/{filename}",
                                     json=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                        headers={"kbn-xsrf": "reporting"})
                print(resp.json())    
        

def load_docs(parent, index):
    docs_path = os.path.join(parent, 'docs')    
    
    for file in os.listdir(docs_path):
        if file.endswith(".json"):
            with open(os.path.join(docs_path, file), "rt", encoding='utf8') as f:
                body = json.load(f)
                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}/_doc/{filename}?pipeline={index}",
                                     json=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
                print(resp.json())  


def create_github_connector(name, index):
    body = {
        "index_name": index,
        "name": name,
        "service_type": "github"
        }

    print("create github connector")
    resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_connector/{name}",
                            json=body, timeout=TIMEOUT,
                            auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                            headers={"kbn-xsrf": "reporting"})
    print(resp.json())  
    
    
    
    
def load_indices():
    for index in os.listdir(INDICES_RESOURCES_PATH):
        load_index(os.path.join(INDICES_RESOURCES_PATH, index), index)
        load_pipelines(os.path.join(INDICES_RESOURCES_PATH, index))
        load_docs(os.path.join(INDICES_RESOURCES_PATH, index), index)
        create_github_connector(index, index)
      
#load_indices()  

def load_elser():
    body = {
        "service": "elser",
        "service_settings": {
            "num_allocations": 1,
            "num_threads": 1
        }
    }
    
    resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_inference/sparse_embedding/elser_model_2_linux-x86_64",
                            json=body, timeout=TIMEOUT,
                            auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                            headers={"kbn-xsrf": "reporting"})
    print(resp.json())  
    

def load_knowledge():
    
    resp = requests.post(f"{os.environ['KIBANA_URL']}/internal/observability_ai_assistant/kb/setup",
                                     timeout=TIMEOUT,
                                     headers={"kbn-xsrf": "reporting"},
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
    print(f"setting up knowledgebase: {resp}")

    
    for file in os.listdir(KNOWLEDGE_RESOURCES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(KNOWLEDGE_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                body = json.load(f)
                filename = Path(file).stem
                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/.kibana-observability-ai-assistant-kb-000001/_doc/{filename}?pipeline=.kibana-observability-ai-assistant-kb-ingest-pipeline",
                                     json=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
                print(f"loading knowledge {filename}: {resp.json()}")  

#load_knowledge()

def load():
    load_elser()
    load_knowledge()
    load_indices()

#load_knowledge()