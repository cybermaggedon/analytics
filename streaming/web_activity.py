
import time
import sys
import zmq
import socket
import json
import socket
import os

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import googleapiclient.errors

############################################################################

timeout = 120
curation_time = 5

############################################################################

private = os.getenv("KEY", "private.json")
project = os.getenv("BIGQUERY_PROJECT", None)
dataset = os.getenv("BIGQUERY_DATASET","cyberprobe")
table = os.getenv("ACTIVITY_TABLE","activity")

############################################################################

fqdn = socket.getfqdn()
ctxt = zmq.Context()
skt = ctxt.socket(zmq.PULL)
port = skt.bind_to_random_port("tcp://*")
input="tcp://%s:%d" % (fqdn, port)

print "INIT"
print "INPUT:input:%s" % input
print "RUNNING"
sys.stdout.flush()

############################################################################

# Creds
scopes = ['https://www.googleapis.com/auth/bigquery']

credentials = ServiceAccountCredentials.from_json_keyfile_name(private,
                                                               scopes=scopes)

if project == None:
    project = json.loads(open(private,'r').read())['project_id']

http = Http()
http_auth = credentials.authorize(http)
service = build('bigquery', 'v2', http=http_auth)
tables = service.tables()
tabledata = service.tabledata()
jobs = service.jobs()

############################################################################

# Create table if not exists.

try:
    table_info = tables.get(projectId=project, datasetId=dataset,
                            tableId=table).\
                            execute(http)
    found=True
except googleapiclient.errors.HttpError:
    found=False

if found:
    sys.stderr.write("web_activity: Table %s exists.\n" % table)
else:

    body = {
        "tableReference": {
            "projectId": project,
            "datasetId": dataset,
            "tableId": table
        },
        "kind": "bigquery#table",
        "description": "fingerprint table",
        "schema": {
            "fields": [
                {
                    "name": "device",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "host",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "protocol",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "first",
                    "mode": "REQUIRED",
                    "type": "TIMESTAMP"
                },
                {
                    "name": "last",
                    "mode": "REQUIRED",
                    "type": "TIMESTAMP"
                }
            ]
        }
    }

    try: 
        table_info = tables.insert(projectId=project, datasetId=dataset,
                                   body=body).execute(http)
        sys.stderr.write("web_activity: Table %s created.\n" % table)
    except googleapiclient.errors.HttpError, e:
        sys.stderr.write("web_activity: Table creation failed.\n")
        sys.stderr.write("web_activity: %s\n" % str(e))
        sys.exit(0)

############################################################################

activity = {}

############################################################################

def insert_activity(device, host, protocol, first, last):

    # Store in BigQuery
    obj = {
        "device": device,
        "host": host,
        "protocol": protocol,
        "first": first,
        "last": last
    }
    
    body = {
        "kind": "biquery#tableDataInsertAllRequest",
        "rows": [
            {
                "json": obj
            }
        ]
    }

    try:
        result = tabledata.insertAll(projectId=project, datasetId=dataset,
                                     tableId=table, body=body).\
                                     execute(http)
        if result.has_key("insertErrors"):
            sys.stderr.write("web_activity: %s\n" % json.dumps(obs))
            sys.stderr.write("web_activity: %s\n" % json.dumps(result))
    except googleapiclient.errors.HttpError, e:
        sys.stderr.write("web_activity: Table insert failed.\n")
        sys.stderr.write("web_activity: %s\n" % str(e))
    except:
        pass

def curate():
    now = time.time()

    while True:

        changed = False

        for k in activity:
            if (now - activity[k]["lu"]) > timeout:
                first = activity[k]["first"]
                last = activity[k]["last"]
                device = k[0]
                host = k[1]

                insert_activity(device, host, "http", first, last)

                del(activity[k])
                changed=True
                break

        if not changed:
            break

def update(device, host, tm):
    key = (device, host)
    if activity.has_key(key):
        activity[key]["last"] = tm
        activity[key]["lu"] = time.time()
    else:
        activity[key] = {}
        activity[key]["first"] = tm
        activity[key]["last"] = tm
        activity[key]["lu"] = time.time()

def handle(msg):
    if not msg["action"] == "http_request":
        return

    try:
        update(msg["device"], msg["header"]["Host"], msg["time"])
    except:
        # e.g. missing HTTP headers?
        pass

############################################################################

last_curate=time.time()

while True:
    try:
        msg = skt.recv(flags=zmq.NOBLOCK)
        handle(json.loads(msg))
    except zmq.error.Again:
        if (time.time() - last_curate) > curation_time:
            curate()
        time.sleep(0.1)
    except Exception, e:
        sys.stderr.write("web_activity: Exception: %s\n" % str(e))
        time.sleep(1)

