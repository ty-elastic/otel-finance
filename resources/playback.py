import ndjson
import requests
from datetime import datetime, timezone, timedelta
import os
import json
import gzip
import concurrent.futures
import copy

RECORDED_RESOURCES_PATH = 'recorded'
DAYS_TO_PRELOAD = 1

def get_day_of_week(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.day_of_week':
            return attribute['value']['stringValue']

def overwrite_datasource(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.data_source':
            attribute['value'] = {'stringValue': 'playback'}
            
def check_ts(file_ts, first_file_ts, last_file_ts):
    new_first_file_ts = first_file_ts
    new_last_file_ts = last_file_ts
    if first_file_ts is None or file_ts < first_file_ts:
        new_first_file_ts = file_ts
        #print("SET!!!")
    if last_file_ts is None or file_ts > last_file_ts:
        new_last_file_ts = file_ts
    return new_first_file_ts, new_last_file_ts

def conform_time(*, parent, key, first_file_ts, last_file_ts, trim_last_file_ts, ts_offset, last_ts):
    if key in parent:
        file_ts = int(parent[key])
        
        # too early
        if first_file_ts is not None and file_ts < first_file_ts:
            #print("too early")
            return False, first_file_ts, last_file_ts, last_ts
        # too late
        elif trim_last_file_ts is not None and file_ts > trim_last_file_ts:
            #print("too late")
            return False, first_file_ts, last_file_ts, last_ts
        
        new_first_file_ts, last_file_ts = check_ts(file_ts, first_file_ts, last_file_ts)
        if first_file_ts is None:
            first_file_ts = new_first_file_ts
            #print("SET222")

        file_ts -= first_file_ts
        parent[key] = file_ts+ts_offset
        if parent[key] > last_ts:
            #print("new last ts")
            last_ts = parent[key]
        #print(f"last_ts={last_ts}")
        return True, first_file_ts, last_file_ts, last_ts
    return False, first_file_ts, last_file_ts, last_ts

def conform_resources(*, resources, first_file_ts=None, trim_last_file_ts=None, ts_offset=0, align_to_days=False):
    last_ts = ts_offset
    last_file_ts = None
    first_monday_done = False

    out_data = {}
    out_data['resourceSpans'] = []
    out_data['resourceLogs'] = []
    out_data['resourceMetrics'] = []
    
    uuids = {
        'traceId': {},
        'spanId': {}
    }
    
    last_friday_ts = None

    for resource in resources:
                    
        # if trim_last_file_ts is not None and last_ts > trim_last_file_ts:
        #     return first_file_ts, last_file_ts, last_ts, out_data
            
        # if align_to_days and first_file_ts is not None:
        #     if 'resourceMetrics' in resource:
        #         for metric in resource['resourceMetrics']:
        #             add_metric = True
        #             for scope in metric['scopeMetrics']:
        #                 for scope_metric in scope['metrics']:
        #                     if 'attributes' in scope_metric:
        #                         overwrite_datasource(scope_metric['attributes'])
                            
        #                     #print(scope_metric)
        #                     if 'sum' in scope_metric:
        #                         metricType = 'sum'
        #                     elif 'gauge' in scope_metric:
        #                         metricType = 'gauge'
        #                     elif 'histogram' in scope_metric:
        #                         metricType = 'histogram'
        #                     else:
        #                         print(f'unknown metric type: {scope_metric}')
        #                         return None, None, None, None

        #                     for datapoint in scope_metric[metricType]['dataPoints']:
        #                         if add_metric:
        #                             add_metric, first_file_ts, last_file_ts, last_ts = conform_time(datapoint, 'startTimeUnixNano', first_file_ts, last_file_ts, ts_offset, last_ts, scan_for_ts)
        #                         if add_metric:
        #                             add_metric, first_file_ts, last_file_ts, last_ts = conform_time(datapoint, 'timeUnixNano', first_file_ts, last_file_ts, ts_offset, last_ts, scan_for_ts)
        #             if add_metric:
        #                 out_data['resourceMetrics'].append(metric)

        #     if 'resourceLogs' in resource:
        #         for log in resource['resourceLogs']:
        #             add_log = True
        #             for scope_log in log['scopeLogs']:
        #                 for log_record in scope_log['logRecords']:
        #                     if 'attributes' in log_record:
        #                         overwrite_datasource(log_record['attributes'])
        #                     if add_log:
        #                         add_log, first_file_ts, last_file_ts, last_ts = conform_time(log_record, 'timeUnixNano',  first_file_ts, last_file_ts, ts_offset, last_ts, scan_for_ts)
        #                     if add_log:
        #                         add_log, first_file_ts, last_file_ts, last_ts = conform_time(log_record, 'observedTimeUnixNano',  first_file_ts, last_file_ts, ts_offset, last_ts, scan_for_ts)
        #             if add_log:
        #                 out_data['resourceLogs'].append(log)
                        
        if 'resourceSpans' in resource:
            #print(resource)
            for span in resource['resourceSpans']:
                add_resource_span = False
                for scope in span['scopeSpans']:
                    new_scope_spans = []
                    for scope_span in scope['spans']:

                        if align_to_days:
                            dow = get_day_of_week(scope_span['attributes'])
                            if first_file_ts is None and dow != 'M':
                                print("looking for first monday")
                                continue
                            elif first_file_ts is not None and first_monday_done is False and dow == 'W':
                                print("monday is past")
                                first_monday_done = True
                            elif first_monday_done is True and dow == 'M':
                                print("week is done")
                                last_friday_ts = last_ts
                                first_monday_done = False
                                #return first_file_ts, last_file_ts, last_ts, out_data
                            #print(dow)

                        if 'attributes' in scope_span:
                            overwrite_datasource(scope_span['attributes'])
                        
                        if scope_span['traceId'] not in uuids['traceId']:
                            uuids['traceId'][scope_span['traceId']] = os.urandom(16).hex()
                        scope_span['traceId'] = uuids['traceId'][scope_span['traceId']]
                            
                        if scope_span['spanId'] not in uuids['spanId']:
                            uuids['spanId'][scope_span['spanId']] = os.urandom(8).hex()
                        scope_span['spanId'] = uuids['spanId'][scope_span['spanId']]
                            
                        if 'parentSpanId' in scope_span and scope_span['parentSpanId'] != "":
                            if scope_span['parentSpanId'] not in uuids['spanId']:
                                uuids['spanId'][scope_span['parentSpanId']] = os.urandom(8).hex()
                            scope_span['parentSpanId'] = uuids['spanId'][scope_span['parentSpanId']]

                        add_span, first_file_ts, last_file_ts, last_ts = conform_time(parent=scope_span, key='startTimeUnixNano', 
                                                                                      first_file_ts=first_file_ts, 
                                                                                      last_file_ts=last_file_ts, 
                                                                                      trim_last_file_ts=trim_last_file_ts,
                                                                                      ts_offset=ts_offset, 
                                                                                      last_ts=last_ts)
                        if add_span:
                            add_span, first_file_ts, last_file_ts, last_ts = conform_time(parent=scope_span,key='endTimeUnixNano',
                                                                                        first_file_ts=first_file_ts, 
                                                                                        last_file_ts=last_file_ts, 
                                                                                        trim_last_file_ts=trim_last_file_ts,
                                                                                        ts_offset=ts_offset, 
                                                                                        last_ts=last_ts)
                        if add_span:
                            new_scope_spans.append(scope_span)
                            add_resource_span = True
                        if 'events' in scope_span:
                            new_scope_span_events = []
                            for event in scope_span['events']:
                                add_event, first_file_ts, last_file_ts, last_ts = conform_time(parent=event, key='timeUnixNano',
                                                                                    first_file_ts=first_file_ts, 
                                                                                    last_file_ts=last_file_ts, 
                                                                                    trim_last_file_ts=trim_last_file_ts,
                                                                                    ts_offset=ts_offset, 
                                                                                    last_ts=last_ts)
                                if add_event:
                                    new_scope_span_events.append(event)
                            scope_span['events'] = new_scope_span_events
                    scope['spans'] = new_scope_spans
                    #print(f"first_file_ts={first_file_ts}")
                if add_resource_span:
                    out_data['resourceSpans'].append(span)

    #print('done')
    if align_to_days:
        return first_file_ts, last_friday_ts, last_ts, out_data
    else:
        return first_file_ts, last_file_ts, last_ts, out_data

# def find_first_and_last_ts(file, align_to_days=False):
#     with open(file, encoding='utf-8') as f:
#         resources = ndjson.load(f)
#         first_file_ts, last_file_ts, _, _ = conform_resources(resources=resources, align_to_days=align_to_days)
#         return first_file_ts, last_file_ts

MAX_RECORDS_PER_UPLOAD = 100
UPLOAD_TIMEOUT = 5

def upload_payload(collector_url, signal, payload_type, resource_split):
    payload = {payload_type:resource_split}
    payload = gzip.compress(json.dumps(payload).encode('utf-8'))
    r = requests.post(f"{collector_url}/v1/{signal}", data=payload,
                    headers={'Content-Type':'application/json', 'Content-Encoding':'gzip'}, timeout=UPLOAD_TIMEOUT)
    print(f"{signal}={r.json()}")
    
def upload(executor, collector_url, signal, resources):
    if signal == 'traces':
        payload_type = 'resourceSpans'
    elif signal == 'metrics':
        payload_type = 'resourceMetrics'
    elif signal == 'logs':
        payload_type = 'resourceLogs'
  
    for resource_split in (resources[i:i + MAX_RECORDS_PER_UPLOAD] for i in range(0, len(resources), MAX_RECORDS_PER_UPLOAD)):
        executor.submit(upload_payload, collector_url, signal, payload_type, resource_split)
        #upload_payload(collector_url, signal, payload_type, resource_split)

def load_file(*, file, collector_url, backfill_days=1, first_file_ts=None, trim_last_file_ts=None, align_to_days=False):
    
    # Get the current time
    now = datetime.now(tz=timezone.utc)
    # Subtract one week (7 days)
    ts_offset = now - timedelta(days=backfill_days)
    
    now_ns = int(now.timestamp() * 1e9)
    ts_offset_ns = int(ts_offset.timestamp() * 1e9)
    
    with open(file, encoding='utf-8') as f:
        resources_file = ndjson.load(f)
 
        first_file_ts, trim_last_file_ts, last_ts, trimmed_resources = conform_resources(resources=resources_file, align_to_days=align_to_days, first_file_ts=first_file_ts, trim_last_file_ts=trim_last_file_ts)
        #print(resources_trimmed)
        #return
        #print(trimmed_resources)
        #return
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        
            while ts_offset_ns < now_ns:
                resources = copy.deepcopy(trimmed_resources)
                #print(resources)

                #executor = None

                print(f"> {file} loop {(now_ns - ts_offset_ns)/1e9} / {datetime.fromtimestamp(ts_offset_ns/1e9).strftime('%c')}")
                #print(f"ts_offset_ns={ts_offset_ns}")
                _, _, ts_offset_ns, out_data = conform_resources(resources=[resources], first_file_ts=0, ts_offset=ts_offset_ns, trim_last_file_ts=trim_last_file_ts)
                #print(f"ts_offset_ns={ts_offset_ns}")
                
                if len(out_data['resourceSpans']) > 0:
                    upload(executor, collector_url, 'traces', out_data['resourceSpans'])
                if len(out_data['resourceMetrics']) > 0:
                    upload(executor, collector_url, 'metrics', out_data['resourceMetrics'])
                if len(out_data['resourceLogs']) > 0:
                    upload(executor, collector_url, 'logs', out_data['resourceLogs'])

        executor.shutdown()
            
      
def load():
    first_file_ts = None
    last_file_ts = None
    
    for file in os.listdir(os.path.join(RECORDED_RESOURCES_PATH, "apm")):
        if file.endswith(".json"):
            # if first_file_ts is None and last_file_ts is None:
            #     #first_file_ts, last_file_ts = find_first_and_last_ts(file=os.path.join(RECORDED_RESOURCES_PATH, "apm", file), align_to_days=True)
            #     print(f'first_file_ts={first_file_ts}, last_file_ts={last_file_ts}')
            #     #return
            load_file(file=os.path.join(RECORDED_RESOURCES_PATH, "apm", file), collector_url=os.environ['OTEL_EXPORTER_OTLP_ENDPOINT_PLAYBACK_APM'], 
                      backfill_days=DAYS_TO_PRELOAD, align_to_days=True)
            break
            
    # for file in os.listdir(os.path.join(RECORDED_RESOURCES_PATH, "elasticsearch")):
    #     if file.endswith(".json"):
    #         load_file(file=os.path.join(RECORDED_RESOURCES_PATH, "elasticsearch", file), collector_url=os.environ['OTEL_EXPORTER_OTLP_ENDPOINT_PLAYBACK_ELASTICSEARCH'], 
    #                   first_file_ts=first_file_ts, last_file_ts=last_file_ts, backfill_days=DAYS_TO_PRELOAD)

load()
