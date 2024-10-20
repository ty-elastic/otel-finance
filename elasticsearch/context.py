from flask import Flask, request
import logging
import requests
import random
import time
import os
import threading
from elasticsearch import Elasticsearch
import requests
from pathlib import Path

INDICES_RESOURCES_PATH = 'context/indices'
KNOWLEDGE_RESOURCES_PATH = 'context/knowledge'

TIMEOUT = 10
             
def load_index(parent, index):

    with open(os.path.join(parent, "index.json"), "rt", encoding='utf8') as f:
        body = f.read()
        resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}",
                                data=body, timeout=TIMEOUT,
                                auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
        print(resp.json())
        
def load_pipelines(parent):
    pipelines_path = os.path.join(parent, 'pipelines')
    
    for file in os.listdir(pipelines_path):
        if file.endswith(".json"):
            with open(os.path.join(pipelines_path, file), "rt", encoding='utf8') as f:
                body = f.read()
                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/_ingest/pipeline/{filename}",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']), 
                                        headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
                print(resp.json())    
        

def load_docs(parent, index):
    docs_path = os.path.join(parent, 'docs')    
    
    for file in os.listdir(docs_path):
        if file.endswith(".json"):
            with open(os.path.join(docs_path, file), "rt", encoding='utf8') as f:
                body = f.read()
                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/{index}/_doc/${filename}?pipeline={index}",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"Content-Type": "application/json"})
                print(resp.json())  

def load_indices():
    for index in os.listdir(INDICES_RESOURCES_PATH):
        load_index(os.path.join(INDICES_RESOURCES_PATH, index), index)
        load_pipelines(os.path.join(INDICES_RESOURCES_PATH, index))
        load_docs(os.path.join(INDICES_RESOURCES_PATH, index), index)
        

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
                            headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
    print(resp.json())  
    

def load_knowledge():

    for file in os.listdir(KNOWLEDGE_RESOURCES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(KNOWLEDGE_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                body = f.read()
                filename = Path(file).stem

                resp = requests.put(f"{os.environ['ELASTICSEARCH_URL']}/.kibana-observability-ai-assistant-kb-000001/_doc/${filename}?pipeline=.kibana-observability-ai-assistant-kb-ingest-pipeline",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"Content-Type": "application/json"})
                print(resp.json())  

def load():
    load_elser()
    load_knowledge()
    load_indices()
    
#load()