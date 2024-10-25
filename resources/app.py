from flask import Flask
import time
import threading

import ml
import alias
import kibana
import slo
import context
import assistant
import playback

app = Flask(__name__)

@app.post('/load/ml/trained')
def load_ml_trained():
    ml.load_trained()
    return None

@app.post('/load/ml/anomaly')
def load_ml_anomaly():
    ml.load_anomaly()
    return None

def init():
    alias.load()
    assistant.load()
    context.load()
    kibana.load()
    slo.load()
    playback.load()

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