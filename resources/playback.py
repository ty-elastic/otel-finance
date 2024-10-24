import ndjson
import requests
import time
from datetime import datetime, timezone, timedelta
import os
import json
import gzip
import uuid
import random
import html

def get_day_of_week(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.day_of_week':
            return attribute['value']['stringValue']

def overwrite_datasource(attributes):
    for attribute in attributes:
        if attribute['key'] == 'com.example.data_source':
            attribute['value'] = {'stringValue': 'playback'}
            
        
def conform_time(parent, key, first_ts, ts_offset, last_ts):
    if key in parent:
        ts = int(parent[key])
        if first_ts is None:
            first_ts = ts
            print("SET")
        ts -= first_ts
        if ts >= 0:
            parent[key] = ts+ts_offset
            if ts+ts_offset > last_ts:
                last_ts = ts+ts_offset
            return True, first_ts, last_ts
    return False, first_ts, last_ts



def parse(file, ts_offset=0, align_to_days=False):
    first_ts = None
    last_ts = ts_offset
    first_monday_done = False
    out_data = {}
    out_data['resourceSpans'] = []
    out_data['resourceLogs'] = []
    out_data['resourceMetrics'] = []
    
    uuids = {
        'traceId': {},
        'spanId': {}
    }
    
    with open(file, encoding='utf-8') as f:
        datas = ndjson.load(f)
        for data in datas:

            if 'resourceMetrics' in data:
                for metric in data['resourceMetrics']:
                    add_metric = True
                    for scope in metric['scopeMetrics']:
                        for scope_metric in scope['metrics']:
                            #print(scope_metric)
                            if 'sum' in scope_metric:
                                metricType = 'sum'
                            elif 'gauge' in scope_metric:
                                metricType = 'gauge'
                            elif 'histogram' in scope_metric:
                                metricType = 'histogram'
                            else:
                                print(scope_metric)
                            for datapoint in scope_metric[metricType]['dataPoints']:
                                if add_metric:
                                    add_metric, first_ts, last_ts = conform_time(datapoint, 'startTimeUnixNano', first_ts, ts_offset, last_ts)
                                if add_metric:
                                    add_metric, first_ts, last_ts = conform_time(datapoint, 'timeUnixNano', first_ts, ts_offset, last_ts)
                    if add_metric:
                        out_data['resourceMetrics'].append(metric)
            if 'resourceSpans' in data:
                
                for span in data['resourceSpans']:
                    add_span = True
                    for scope in span['scopeSpans']:
                        for scope_span in scope['spans']:
                            
                            overwrite_datasource(scope_span['attributes'])

                            if align_to_days:
                                dow = get_day_of_week(scope_span['attributes'])
                                if first_ts is None and dow != 'M':
                                    #print("skip non-monday")
                                    continue
                                elif first_ts is not None and first_monday_done is False and dow == 'Tu':
                                    print("monday is done")
                                    first_monday_done = True
                                elif first_monday_done is True and dow == 'M':
                                    print("LOOPED!")
                                    return first_ts, last_ts, out_data
                            
                            if scope_span['traceId'] not in uuids['traceId']:
                                uuids['traceId'][scope_span['traceId']] = os.urandom(16).hex()#random.getrandbits(128)
                                scope_span['traceId'] =  uuids['traceId'][scope_span['traceId']]
                            else:
                                scope_span['traceId'] = uuids['traceId'][scope_span['traceId']]
                                
                            if scope_span['spanId'] not in uuids['spanId']:
                                uuids['spanId'][scope_span['spanId']] = os.urandom(8).hex()
                                scope_span['spanId'] = uuids['spanId'][scope_span['spanId']]
                            else:
                                scope_span['spanId'] = uuids['spanId'][scope_span['spanId']]
                                
                            if scope_span['parentSpanId'] not in uuids['spanId']:
                                uuids['spanId'][scope_span['parentSpanId']] = os.urandom(8).hex()
                                scope_span['parentSpanId'] = uuids['spanId'][scope_span['parentSpanId']]
                            else:
                                scope_span['parentSpanId'] = uuids['spanId'][scope_span['parentSpanId']]

                            if add_span:
                                add_span, first_ts, last_ts = conform_time(scope_span, 'startTimeUnixNano', first_ts, ts_offset, last_ts)
                            if add_span:
                                add_span, first_ts, last_ts = conform_time(scope_span, 'endTimeUnixNano', first_ts, ts_offset, last_ts)
                            if 'events' in scope_span:
                                for event in scope_span['events']:
                                    if add_span:
                                        add_span, first_ts, last_ts = conform_time(event, 'timeUnixNano', first_ts, ts_offset, last_ts)
                    if add_span:
                        out_data['resourceSpans'].append(span)
            if 'resourceLogs' in data:
                for log in data['resourceLogs']:
                    add_log = True
                    for scope_log in log['scopeLogs']:
                        for log_record in scope_log['logRecords']:
                            if add_log:
                                add_log, first_ts, last_ts = conform_time(log_record, 'timeUnixNano', first_ts, ts_offset, last_ts)
                            if add_log:
                                add_log, first_ts, last_ts = conform_time(log_record, 'observedTimeUnixNano', first_ts, ts_offset, last_ts)
                    if add_log:
                        out_data['resourceLogs'].append(log)
        return first_ts, last_ts, out_data

MAX_RECORDS_PER_UPLOAD = 100

def upload(collector_url, signal, resources):
    if signal == 'traces':
        payload_type = 'resourceSpans'
    elif signal == 'metrics':
        payload_type = 'resourceMetrics'
    elif signal == 'logs':
        payload_type = 'resourceLogs'
    for resource_spans_split in (resources[i:i + MAX_RECORDS_PER_UPLOAD] for i in range(0, len(resources), MAX_RECORDS_PER_UPLOAD)):
        payload = {payload_type:resource_spans_split}
        #print(payload)
        payload = gzip.compress(json.dumps(payload).encode('utf-8'))
        r = requests.post(f"{collector_url}/v1/{signal}", data=payload,
                        headers={'Content-Type':'application/json', 'Content-Encoding':'gzip'})
        print(f"{signal}={r.json()}")

def load(file, collector_url, align_to_days):
    
    # Get the current time
    now = datetime.now(tz=timezone.utc)
    # Subtract one week (7 days)
    ts_offset = now - timedelta(days=1)
    
    now_ns = int(now.timestamp() * 1e9)
    ts_offset_ns = int(ts_offset.timestamp() * 1e9)
    
    while ts_offset_ns < now_ns:
        print(f"> loop {(now_ns - ts_offset_ns)/1e9}")
        first_ts, ts_offset_ns, out_data = parse(file, ts_offset_ns, align_to_days)
        print(datetime.fromtimestamp(ts_offset_ns/1e9).strftime('%c'))

        if len(out_data['resourceSpans']) > 0:
            upload(collector_url, 'traces', out_data['resourceSpans'])
        # if len(out_data['resourceMetrics']) > 0:
        #     upload(collector_url, 'metrics', out_data['resourceMetrics'])
        # if len(out_data['resourceLogs']) > 0:
        #     upload(collector_url, 'logs', out_data['resourceLogs'])


load('../recorded/apm.json', 'http://127.0.0.1:4318', True)
#load('../recorded/elasticsearch.json', 'http://127.0.0.1:4319', False)
