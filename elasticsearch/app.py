from flask import Flask, request
import logging
import requests
import random
import time
import os
import threading
from threading import Thread
from elasticsearch import Elasticsearch

import ml
import index
import kibana

app = Flask(__name__)

@app.post('/ml/train')
def ml_train():
    ml.load_trained()
    return None

def init():
    kibana.load_resources()

def maintenance_loop():
    indices_created = False
    while True:
        if not indices_created:
            indices_created = index.create_aliases()
        time.sleep(10)

def start_maintenance_thread():
    thread = threading.Thread(target=maintenance_loop)
    thread.start()

init()
start_maintenance_thread()