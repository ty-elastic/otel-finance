from flask import Flask, request, abort
import logging
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
import errors
import case
import space

aliases_created = False

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

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

@app.get('/status/playback')
def status_playback():
    global aliases_created
    if aliases_created:
        return {'result': 'success'}
    else:
        abort(404, description="not ready")

@app.get('/status/alerts')
def status_alert():
    active = slo.alerts_active()
    if active:
        return {'result': 'success'}
    else:
        abort(404, description="not ready")

def init():
    print("resetting initial assets...")

    if os.environ['DELETE_DATA'] == 'true':
        playback.delete_all()

    if os.environ['BACKLOAD_DATA'] == 'true':
        start_loading_thread()

    space.load_all()
    kibana.set_default_dataview("logs-*")
    
    slo.delete_all()

    alias.load()
    assistant.load()
    context.load()
    kibana.load()
    case.load_all()
    if os.environ['SOLVE_ALL'] == 'true':
        slo.load_all()


def maintenance_loop():
    global aliases_created
    print("START maintenance_loop")
   
    if os.environ['ERRORS'] == 'true':
        errors_started = False
    else:
        errors_started = True
    while True:
        if not aliases_created:
            aliases_created = alias.load()
        if os.environ['ERRORS'] == 'true' and not errors_started:
            errors_started = errors.load()
        time.sleep(1)

        if errors_started and aliases_created:
            break

def loading():
    #time.sleep(1)
    print("START loading")
    try:
        playback.load()
    except Exception as inst:
        print(inst)


def start_maintenance_thread():
    thread = threading.Thread(target=maintenance_loop, daemon=False)
    thread.start()

def start_loading_thread():
    thread = threading.Thread(target=loading, daemon=False)
    thread.start()

logging.info("starting up...")
init()
start_maintenance_thread()
