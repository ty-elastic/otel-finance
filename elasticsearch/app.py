from flask import Flask, request
import logging
import requests
import random
import time
import os
from threading import Thread

import ml

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.post('/ml/train')
def ml_train():
    ml.load_trained()
    return None

