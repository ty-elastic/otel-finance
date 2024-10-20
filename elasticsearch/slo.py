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

SLO_RESOURCES_PATH  = 'slos'

def load_slos():

    for file in os.listdir(SLO_RESOURCES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(SLO_RESOURCES_PATH, file), "rt", encoding='utf8') as f:
                body = f.read()

                resp = requests.post(f"{os.environ['KIBANA_URL']}/api/observability/slos",
                                     data=body, timeout=TIMEOUT,
                                     auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                     headers={"kbn-xsrf": "reporting", "Content-Type": "application/json"})
                print(resp.json())  

#load_slos()