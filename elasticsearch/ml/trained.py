from elasticsearch import Elasticsearch
import os
from pathlib import Path
import json

def main():
    with Elasticsearch(os.environ['ELASTICSEARCH_URL'], basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD'])) as client:

        for file in os.listdir("trained"):
            with open(os.path.join("trained", file), 'r') as json_file:
                filename = Path(file).stem
                data = json.load(json_file)

                try:
                    client.ml.put_data_frame_analytics(id=filename, 
                                                 body=data)
                except Exception as inst:
                    print(inst)

                try:
                    client.ml.start_data_frame_analytics(id=filename)
                except Exception as inst:
                    print(inst)
                
                result = client.ml.get_trained_models(model_id=f"{filename}*")
                print(result)
                for model in result['trained_model_configs']:
                    #rest = client.ml.start_trained_model_deployment(model_id=model['model_id'], deployment_id=Path(file).stem, wait_for='fully_allocated')
                    #print(rest)
                    
                    # create pipeline
                    body = {                 
                        "description": f"Uses the pre-trained data frame analytics model {model['model_id']} to infer against the data that is being ingested in the pipeline",
                        "processors": [
                            {
                                "inference": {
                                    "model_id": model['model_id'],
                                    "ignore_failure": True,
                                    "target_field": "ml.inference.labels.com_example_classification_prediction",
                                    "inference_config": {
                                        "classification": {
                                            "num_top_classes": -1,
                                            "top_classes_results_field": "top_classes",
                                            "results_field": "labels.com_example_classification_prediction",
                                            "num_top_feature_importance_values": 0,
                                            "prediction_field_type": "string"
                                        }
                                    }
                                }
                            }
                        ]
                    }
                    res = client.ingest.put_pipeline(id=f"ml-inference-{model['model_id']}", body=body) 
                    print(res)
                    
                    body = {
                        "processors": [
                            {
                                "pipeline": {
                                    "name": f"ml-inference-{model['model_id']}",
                                    "ignore_missing_pipeline": True,
                                    "ignore_failure": True
                                }
                            }
                        ]
                    }
                    res = client.ingest.put_pipeline(id="traces-apm@custom", body=body)
                    print(res)
                    

            
main()