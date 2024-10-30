import ndjson
import requests
import time
from datetime import datetime, timezone, timedelta
import os
import json
import gzip
import concurrent.futures
import copy
import sys

RECORDED_RESOURCES_PATH = 'recorded'
HOURS_TO_PRELOAD = 6

def get_day_of_week(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.day_of_week':
            return attribute['value']['stringValue']

def overwrite_datasource(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.data_source':
            attribute['value'] = {'stringValue': 'playback'}

def check_ts_for_key(parent, key, first_file_ts, last_file_ts):
    if key in parent:
        file_ts = int(parent[key])
        if first_file_ts is None or file_ts < first_file_ts:
            first_file_ts = file_ts
        if last_file_ts is None or file_ts > last_file_ts:
            last_file_ts = file_ts
    return first_file_ts, last_file_ts

def find_trim_points(*, resources, align_to_week=False):
    first_file_ts = None
    last_file_ts = None
    monday_done = False
    rewind_last_file_ts = None

    for resource in resources:
        if 'resourceSpans' in resource:
            for span in resource['resourceSpans']:
                for scope in span['scopeSpans']:
                    for scope_span in scope['spans']:

                        if align_to_week:
                            dow = get_day_of_week(scope_span['attributes'])
                            if first_file_ts is None and dow != 'M':
                                #print("looking for first monday")
                                continue
                            elif first_file_ts is not None and monday_done is False and dow == 'W':
                                print("monday is past")
                                monday_done = True
                            elif monday_done is True and dow == 'M':
                                print("week is done")
                                rewind_last_file_ts = last_file_ts
                                monday_done = False
                                #return first_file_ts, last_file_ts
                            
                        first_file_ts, last_file_ts = check_ts_for_key(parent=scope_span, key='startTimeUnixNano',
                                                                               first_file_ts=first_file_ts, 
                                                                                last_file_ts=last_file_ts)
                        first_file_ts, last_file_ts = check_ts_for_key(parent=scope_span, key='endTimeUnixNano',
                                                                               first_file_ts=first_file_ts, 
                                                                                last_file_ts=last_file_ts)

    if rewind_last_file_ts is not None:
        return first_file_ts, rewind_last_file_ts
    else:
        return first_file_ts, last_file_ts

def conform_time(*, parent, key, trim_first_file_ts, trim_last_file_ts, ts_offset, last_ts, type):
    if key in parent:
        file_ts = int(parent[key])
        
        # too early
        if file_ts < trim_first_file_ts:
            # if type == 'metric':
            #     print(f"{type} too early {file_ts}/{trim_first_file_ts}, {(trim_first_file_ts-file_ts)/1e9}")
            return True, False, last_ts
        # too late
        elif trim_last_file_ts is not None and file_ts > trim_last_file_ts:
            # if type == 'metric':
            #     print(f"{type} too late {file_ts}/{trim_last_file_ts}, {(file_ts-trim_last_file_ts)/1e9}")
            return True, False, last_ts
        
        file_ts -= trim_first_file_ts
        parent[key] = file_ts+ts_offset
        if parent[key] > last_ts:
            last_ts = parent[key]
        return True, True, last_ts
    # else:
    #     print(f"key {key} not found for {type}, {parent}")
    return False, False, last_ts

def conform_resources(*, resources, trim_first_file_ts=0, trim_last_file_ts=None, ts_offset=0):
    last_ts = ts_offset

    out_data = {}
    out_data['resourceSpans'] = []
    out_data['resourceLogs'] = []
    out_data['resourceMetrics'] = []
    
    uuids = {
        'traceId': {},
        'spanId': {}
    }
    
    for resource in resources:

        if 'resourceMetrics' in resource:
            for metric in resource['resourceMetrics']:
                add_resource_metric = False
                for scope in metric['scopeMetrics']:
                    for scope_metric in scope['metrics']:
                        if 'attributes' in scope_metric:
                            overwrite_datasource(scope_metric['attributes'])
                        
                        if 'sum' in scope_metric:
                            metricType = 'sum'
                        elif 'gauge' in scope_metric:
                            metricType = 'gauge'
                        elif 'histogram' in scope_metric:
                            metricType = 'histogram'
                        else:
                            print(f'unknown metric type: {scope_metric}')
                            return None, None, None, None

                        new_datapoints = []
                        for datapoint in scope_metric[metricType]['dataPoints']:
                            found1, add_metric1, last_ts = conform_time(parent=datapoint, key='timeUnixNano', 
                                                                trim_first_file_ts=trim_first_file_ts, 
                                                                trim_last_file_ts=trim_last_file_ts,
                                                                ts_offset=ts_offset, last_ts=last_ts,
                                                                type='metric')
                            found2, add_metric2, last_ts = conform_time(parent=datapoint, key='startTimeUnixNano',
                                                                trim_first_file_ts=trim_first_file_ts, 
                                                                trim_last_file_ts=trim_last_file_ts,
                                                                ts_offset=ts_offset, last_ts=last_ts,
                                                                type='metric')

                            if (found1 and add_metric1 and found2 and add_metric2) or (not found1 and add_metric2) or (not found2 and add_metric1):
                                new_datapoints.append(datapoint)
                                add_resource_metric = True
                        scope_metric[metricType]['dataPoints'] = new_datapoints
                if add_resource_metric:
                    out_data['resourceMetrics'].append(metric)

        if 'resourceLogs' in resource:
            for log in resource['resourceLogs']:
                add_resource_log = False
                for scope_log in log['scopeLogs']:
                    new_scope_log_records = []
                    for log_record in scope_log['logRecords']:
                        if 'attributes' in log_record:
                            overwrite_datasource(log_record['attributes'])
                        found1, add_log1, last_ts = conform_time(parent=log_record, key='timeUnixNano',
                                                                trim_first_file_ts=trim_first_file_ts, 
                                                                trim_last_file_ts=trim_last_file_ts,
                                                                ts_offset=ts_offset, last_ts=last_ts,
                                                                type='log')

                        found2, add_log2, last_ts = conform_time(parent=log_record, key='observedTimeUnixNano',
                                                            trim_first_file_ts=trim_first_file_ts, 
                                                            trim_last_file_ts=trim_last_file_ts,
                                                            ts_offset=ts_offset, last_ts=last_ts,
                                                            type='log')
                        if (found1 and add_log1 and found2 and add_log2) or (not found1 and add_log2) or (not found2 and add_log1):
                            add_resource_log = True
                            new_scope_log_records.append(log_record)
                    scope_log['logRecords'] = new_scope_log_records
                if add_resource_log:
                    out_data['resourceLogs'].append(log)
                        
        if 'resourceSpans' in resource:
            for span in resource['resourceSpans']:
                add_resource_span = False
                for scope in span['scopeSpans']:
                    new_scope_spans = []
                    for scope_span in scope['spans']:
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

                        found1, add_span1, last_ts = conform_time(parent=scope_span, key='startTimeUnixNano', 
                                                                trim_first_file_ts=trim_first_file_ts, 
                                                                trim_last_file_ts=trim_last_file_ts,
                                                                ts_offset=ts_offset, last_ts=last_ts,
                                                                type='span')
                        found2, add_span2, last_ts = conform_time(parent=scope_span,key='endTimeUnixNano',
                                                            trim_first_file_ts=trim_first_file_ts, 
                                                            trim_last_file_ts=trim_last_file_ts,
                                                            ts_offset=ts_offset, last_ts=last_ts,
                                                            type='span')
                        if 'events' in scope_span:
                            new_scope_span_events = []
                            for event in scope_span['events']:
                                _, add_event, last_ts = conform_time(parent=event, key='timeUnixNano',
                                                                trim_first_file_ts=trim_first_file_ts, 
                                                                trim_last_file_ts=trim_last_file_ts,
                                                                ts_offset=ts_offset, last_ts=last_ts,
                                                                type='span')
                                if add_event:
                                    new_scope_span_events.append(event)
                            scope_span['events'] = new_scope_span_events
                                    
                        if (found1 and add_span1 and found2 and add_span2) or (not found1 and add_span2) or (not found2 and add_span1):
                            new_scope_spans.append(scope_span)
                            add_resource_span = True
                    scope['spans'] = new_scope_spans
                if add_resource_span:
                    out_data['resourceSpans'].append(span)

    return last_ts, out_data

MAX_RECORDS_PER_UPLOAD = 50
MAX_MB_PER_UPLOAD = 4
UPLOAD_TIMEOUT = 5
GROUPED_TIME_MINS = 60

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
    
    i = 0
    max_records_per_upload = MAX_RECORDS_PER_UPLOAD
    while i < len(resources):
        while len(json.dumps(resources[i:i + max_records_per_upload])) > (MAX_MB_PER_UPLOAD*1024*1024) and max_records_per_upload > 10:
            max_records_per_upload -= 10
            print(f"max_records_per_upload={max_records_per_upload}")  
        executor.submit(upload_payload, collector_url, signal, payload_type, resources[i:i + max_records_per_upload])
        i += max_records_per_upload

def load_file(*, file, collector_url, backfill_hours=24, trim_first_file_ts=None, trim_last_file_ts=None, align_to_days=False):
    start = time.time()
    
    with open(file, encoding='utf-8') as f:
        print(f"read {file}")
        resources_file = ndjson.load(f)
        
        if trim_first_file_ts is None or trim_last_file_ts is None:
            trim_first_file_ts, trim_last_file_ts = find_trim_points(resources=resources_file, align_to_week=align_to_days)
            print(f"found trim points for {file}, {trim_first_file_ts}, {trim_last_file_ts}")
 
        print(f"conforming")
        _, trimmed_resources = conform_resources(resources=resources_file, 
                                                 trim_first_file_ts=trim_first_file_ts, 
                                                 trim_last_file_ts=trim_last_file_ts)

        print('grouping data...')
        grouped_data = {'resourceSpans': [], 'resourceMetrics': [], 'resourceLogs': []}
        group_data_offset = 0
        # mux 1 hour of data in memory
        while group_data_offset < GROUPED_TIME_MINS*60*1e9:
            resources = copy.deepcopy(trimmed_resources)
            group_data_offset, out_data = conform_resources(resources=[resources], ts_offset=group_data_offset)
            print(group_data_offset)
            if len(out_data['resourceSpans']) > 0:
                grouped_data['resourceSpans'] = grouped_data['resourceSpans'] + out_data['resourceSpans']
            if len(out_data['resourceMetrics']) > 0:
                grouped_data['resourceMetrics'] = grouped_data['resourceMetrics'] + out_data['resourceMetrics']
            if len(out_data['resourceLogs']) > 0:
                grouped_data['resourceLogs'] = grouped_data['resourceLogs'] + out_data['resourceLogs']
        #grouped_data = trimmed_resources
        print("done grouping")
        
        # Get the current time
        now = datetime.now(tz=timezone.utc)
        # Subtract one week (7 days)
        ts_offset = now - timedelta(hours=backfill_hours)
        
        now_ns = int(now.timestamp() * 1e9)
        ts_offset_ns = int(ts_offset.timestamp() * 1e9)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        
            while ts_offset_ns < now_ns:
                resources = copy.deepcopy(grouped_data)

                print(f"> {file} loop {(now_ns - ts_offset_ns)/1e9} / {datetime.fromtimestamp(ts_offset_ns/1e9).strftime('%c')}")
                ts_offset_ns, out_data = conform_resources(resources=[resources], ts_offset=ts_offset_ns)

                if len(out_data['resourceSpans']) > 0:
                    upload(executor, collector_url, 'traces', out_data['resourceSpans'])
                if len(out_data['resourceMetrics']) > 0:
                    upload(executor, collector_url, 'metrics', out_data['resourceMetrics'])
                if len(out_data['resourceLogs']) > 0:
                    upload(executor, collector_url, 'logs', out_data['resourceLogs'])

        executor.shutdown()
        
        end = time.time()
        print(f'duration={end-start}')
        
        return trim_first_file_ts, trim_last_file_ts
            
      
def load():
    trim_first_file_ts = None
    trim_last_file_ts = None
    
    if os.path.exists(os.path.join(RECORDED_RESOURCES_PATH, "apm")):
        for file in os.listdir(os.path.join(RECORDED_RESOURCES_PATH, "apm")):
            if file.endswith(".json"):
                print(f"loading {file}")
                trim_first_file_ts, trim_last_file_ts = load_file(file=os.path.join(RECORDED_RESOURCES_PATH, "apm", file), collector_url=os.environ['OTEL_EXPORTER_OTLP_ENDPOINT_PLAYBACK_APM'], 
                        backfill_hours=HOURS_TO_PRELOAD, align_to_days=True)
                print(f"trim_first_file_ts={trim_first_file_ts}, trim_last_file_ts={trim_last_file_ts}")

    if os.path.exists(os.path.join(RECORDED_RESOURCES_PATH, "elasticsearch")):
        for file in os.listdir(os.path.join(RECORDED_RESOURCES_PATH, "elasticsearch")):
            if file.endswith(".json"):
                print(f"loading {file}")
                load_file(file=os.path.join(RECORDED_RESOURCES_PATH, "elasticsearch", file), collector_url=os.environ['OTEL_EXPORTER_OTLP_ENDPOINT_PLAYBACK_ELASTICSEARCH'], 
                        trim_first_file_ts=trim_first_file_ts, trim_last_file_ts=trim_last_file_ts, backfill_hours=HOURS_TO_PRELOAD)

    print('done')
#load()
