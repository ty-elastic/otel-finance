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
import alias
import kibana
import slo
import context

app = Flask(__name__)

@app.post('/ml/train')
def ml_train():
    ml.load_trained()
    return None

def init():
    alias.load()
    kibana.load()
    slo.load()
    context.load()

def maintenance_loop():
    aliases_created = False
    while True:
        if not aliases_created:
            aliases_created = alias.load()
        time.sleep(10)

def start_maintenance_thread():
    thread = threading.Thread(target=maintenance_loop)
    thread.start()

init()
start_maintenance_thread()