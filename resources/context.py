import os
import requests
from pathlib import Path
import json
import datetime

INDICES_RESOURCES_PATH = 'context/docs'
KNOWLEDGE_RESOURCES_PATH = 'context/knowledge'

TIMEOUT = 480
             
def load_index(index):

    with open(os.path.join("context", "index.json"), "rt", encoding='utf8') as f:
        content = f.read()
        new_content = content.replace('{{name}}', index)
        body = json.loads(new_content)
        resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}",
                                json=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                headers={"kbn-xsrf": "reporting"})
        print(resp.json())
        
def load_pipelines(index):
    pipelines_path = os.path.join("context", 'pipelines')
    
    for file in os.listdir(pipelines_path):
        if file.endswith(".json"):
            with open(os.path.join(pipelines_path, file), "rt", encoding='utf8') as f:
                content = f.read()
                new_content = content.replace('{{name}}', index)
                body = json.loads(new_content)
                filename = Path(file).stem
                filename = filename.replace('{{name}}', index)

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_ingest/pipeline/{filename}",
                                     json=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                        headers={"kbn-xsrf": "reporting"})
                print(resp.json())    
        

def load_docs(docs_path, index):
    #docs_path = os.path.join(parent, 'docs')    
    
    for file in os.listdir(docs_path):
        if file.endswith(".json"):
            with open(os.path.join(docs_path, file), "rt", encoding='utf8') as f:
                content = f.read()
                new_content = content.replace('{{@timestamp}}', datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")) # "2024-09-18T02:41:45Z"
                body = json.loads(new_content)

                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}/_doc/{filename}?pipeline={index}",
                                     json=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
                print(resp.json())  


def create_connector(name, index, service_type):
    body = {
        "index_name": index,
        "name": name,
        "service_type": service_type
        }

    print("create connector")
    resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_connector/{name}",
                            json=body, timeout=TIMEOUT,
                            auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                            headers={"kbn-xsrf": "reporting"})
    print(resp.json())  
    
    
    
    
def load_indices():
    for index in os.listdir(INDICES_RESOURCES_PATH):
        print(f"working on index {index}")
        if index.startswith("."):
            continue
        load_index(index)
        load_pipelines(index)
        load_docs(os.path.join(INDICES_RESOURCES_PATH, index), index)
        if index.find('github') == -1:
            create_connector(index, index, "custom")
        else:
            create_connector(index, index, "github")
      
#load_indices()  

def load_elser():
    body = {
        "service": "elasticsearch",
        "service_settings": {
            "model_id": ".elser_model_2_linux-x86_64",
            "num_allocations": 1,
            "num_threads": 1
        }
    }
    
    resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_inference/sparse_embedding/elser_model_2_linux-x86_64",
                            json=body, timeout=TIMEOUT,
                            auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                            headers={"kbn-xsrf": "reporting"})
    print(resp.json())  
    

def setup_knowledge():
    print(os.environ['KIBANA_URL'])

    resp = requests.get(f"{os.environ['KIBANA_URL']}/internal/observability_ai_assistant/kb/status",
                                     timeout=TIMEOUT,
                                     headers={"kbn-xsrf": "reporting"},
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
    print(f"setting up knowledgebase: {resp.json()}")


    resp = requests.post(f"{os.environ['KIBANA_URL']}/internal/observability_ai_assistant/kb/setup",
                                     timeout=TIMEOUT,
                                     headers={"kbn-xsrf": "reporting"},
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
    print(f"setting up knowledgebase: {resp}")

# def load_knowledge():
#     print(os.environ['KIBANA_URL'])

#     resp = requests.get(f"{os.environ['KIBANA_URL']}/internal/observability_ai_assistant/kb/status",
#                                      timeout=TIMEOUT,
#                                      headers={"kbn-xsrf": "reporting"},
#                                      auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
#     print(f"setting up knowledgebase: {resp.json()}")


#     resp = requests.post(f"{os.environ['KIBANA_URL']}/internal/observability_ai_assistant/kb/setup",
#                                      timeout=TIMEOUT,
#                                      headers={"kbn-xsrf": "reporting"},
#                                      auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
#     print(f"setting up knowledgebase: {resp}")

    
#     for file in os.listdir(KNOWLEDGE_RESOURCES_PATH):
#         if file.endswith(".json"):
#             with open(os.path.join(KNOWLEDGE_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
#                 body = json.load(f)
#                 filename = Path(file).stem
#                 resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/.kibana-observability-ai-assistant-kb-000001/_doc/{filename}?pipeline=.kibana-observability-ai-assistant-kb-ingest-pipeline",
#                                      json=body, timeout=TIMEOUT,
#                                      auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']))
#                 print(f"loading knowledge {filename}: {resp.json()}")  

#load_knowledge()

def load():
    load_elser()
    setup_knowledge()
    load_indices()

#load_knowledge()

#load()