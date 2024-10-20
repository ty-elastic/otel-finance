from flask import Flask, request
import logging
import requests
import random
import time
import os
import threading
from elasticsearch import Elasticsearch
from pathlib import Path

TIMEOUT = 10

ALIAS_RESOURCES_PATH  = 'alias'

def load_aliases():

    for index in os.listdir(ALIAS_RESOURCES_PATH):
        print(index)
        index_path = os.path.join(ALIAS_RESOURCES_PATH, index)
        print(index_path)
        for file in os.listdir(index_path):
            
            if file.endswith(".json"):
                print(file)
                with open(os.path.join(index_path, file), "rt", encoding='utf8') as f:
                    body = f.read()
                    filename = Path(file).stem
                    print(filename)
                    
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

#load_slos()

load_aliases()

# def create_aliases():
#     with Elasticsearch(os.environ['ELASTICSEARCH_URL'], basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD'])) as client:
#         resp = client.indices.exists(index='traces-apm-default')
#         if resp:
#             print("traces-apm-default found, creating alias")
#             body = {
#                 "filter": {
#                     "term": {
#                     "service.name": "trader"
#                     }
#                 }
#             }
#             resp = client.indices.put_alias(index='traces-apm-default', name='traces-apm-trader', body=body)
#             print(resp)
#             return True
#         else:
#             print("traces-apm-default not yet found...")
#             return False
   