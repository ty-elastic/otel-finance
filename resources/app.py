from flask import Flask, request
import time
import threading
import os

import ml
import alias
import kibana
import slo
import context
import assistant
import playback

app = Flask(__name__)
#logging.basicConfig(level=logging.DEBUG)

@app.post('/load/ml/trained')
def load_ml_trained():
    ml.load_trained()
    return None

@app.post('/load/ml/anomaly')
def load_ml_anomaly():
    ml.load_anomaly()
    return None

@app.post('/load/slo/<slo_name>')
def load_slo(slo_name):
    #slo_name = request.args.get('slo_name', default=None, type=str)
    slo.load(slo_name)
    return {'result': 'success'}

@app.post('/reset')
def reset():
    slo.delete_all()
    playback.delete_all()
    return {'result': 'success'}

def init():
    print("resetting initial assets...")
    
    slo.delete_all()
    playback.delete_all()

    alias.load()
    assistant.load()
    context.load()
    kibana.load()
    
def maintenance_loop():
    print("START maintenance_loop")
    aliases_created = False
    while True:
        if not aliases_created:
            aliases_created = alias.load()
        time.sleep(10)

def loading():
    time.sleep(5)
    print("START loading")
    try:
        playback.load()
    except Exception as inst:
        print(inst)
    if os.environ['SOLVE_ALL'] == 'true':
        slo.load_all()

def start_maintenance_thread():
    thread = threading.Thread(target=maintenance_loop, daemon=False)
    thread.start()

def start_loading_thread():
    thread = threading.Thread(target=loading, daemon=False)
    thread.start()

init()
start_maintenance_thread()

if os.environ['BACKLOAD_DATA'] == 'true':
    start_loading_thread()
