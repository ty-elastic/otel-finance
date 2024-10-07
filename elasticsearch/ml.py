from elasticsearch import Elasticsearch
import os
from pathlib import Path
import json
import time

def load_trained(*, replace=False):
    with Elasticsearch(os.environ['ELASTICSEARCH_URL'], basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD'])) as client:

        inference_processors = []

        for file in os.listdir("ml/trained/job"):
            with open(os.path.join("ml/trained/job", file), 'r') as job:
                filename = Path(file).stem
                json_job = json.load(job)

                try:
                    client.ml.put_data_frame_analytics(id=filename, body=json_job)
                except Exception as inst:
                    print(inst)

                try:
                    client.ml.start_data_frame_analytics(id=filename)
                except Exception as inst:
                    print(inst)
                
                for _ in range(5):
                    time.sleep(2)
                    
                    result = client.ml.get_trained_models(model_id=f"{filename}*")
                    if len(result['trained_model_configs']) == 0:
                        continue
                    
                    model = result['trained_model_configs'][0]
                        
                    with open(os.path.join("ml/trained/pipeline", file), 'r') as pipeline:
                        raw_pipeline = pipeline.read()
                        raw_pipeline = raw_pipeline.replace("{{ MODEL_ID }}", model['model_id'])
                        json_pipeline = json.loads(raw_pipeline)
                        
                        print(json_pipeline)

                        res = client.ingest.put_pipeline(id=f"ml-inference-{model['model_id']}", body=json_pipeline)
                        
                        inference_processors.append({
                                    "pipeline": {
                                        "name": f"ml-inference-{model['model_id']}",
                                        "ignore_missing_pipeline": True,
                                        "ignore_failure": True
                                    }
                                })
                    break
                        
        body = {
            "processors": inference_processors
        }
        print(body)
        res = client.ingest.put_pipeline(id="traces-apm@custom", body=body)
        print(res)


def load_anomaly(*, replace=False):
    with Elasticsearch(os.environ['ELASTICSEARCH_URL'], basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD'])) as client:

        for file in os.listdir("ml/anomaly/job"):
            with open(os.path.join("ml/anomaly/job", file), 'r') as job:
                filename = Path(file).stem
                json_job = json.load(job)

                if replace:
                    client.ml.stop_datafeed(datafeed_id=json_job['datafeed_config']['datafeed_id'])
                    client.ml.close_job(job_id=filename)
                    client.ml.delete_job(job_id=filename, delete_user_annotations=True)

                try:
                    client.ml.put_job(job_id=filename, body=json_job)
                except Exception as inst:
                    print(inst)
                    
                try:
                    client.ml.open_job(job_id=filename)
                except Exception as inst:
                    print(inst)
  
                try:
                    client.ml.start_datafeed(datafeed_id=json_job['datafeed_config']['datafeed_id'])
                except Exception as inst:
                    print(inst)
                    
load_anomaly()