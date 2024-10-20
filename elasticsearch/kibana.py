from flask import Flask, request
import logging
import requests
import random
import time
import os
import threading
from elasticsearch import Elasticsearch
import requests

KIBANA_RESOURCES_PATH = 'kibana'
TIMEOUT = 10

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