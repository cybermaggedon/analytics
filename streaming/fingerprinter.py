#!/usr/bin/env python

import zmq
import json
import sys
import requests
import md5
import time

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import googleapiclient.errors

# Don't forget to update schema below.
wanted_http_headers = {
    'Accept': True,
    'Accept-Charset': True,
    'Accept-Language': True,
    'Access-Control-Allow-Origin': True,
    'Authorization': True,
    'Connection': True,
    'Content-Encoding': True,
    'Content-Language': True,
    'Content-Location': True,
    'Content-Type': True,
    'Cookie': True,
    'Date': True,
    'ETag': True,
    'Forwarded': True,
    'Host': True,
    'Link': True,
    'Location': True,
    'Origin': True,
    'Proxy-Authorization': True,
    'Referer': True,
    'Server': True,
    'Set-Cookie': True,
    'Upgrade': True,
    'User-Agent': True,
    'Via': True,
    'WWW-Authenticate': True,
    'X-Forwarded-For': True,
    'X-Forwarded-Host': True
}

trust_time = 86400

############################################################################

binding = "tcp://localhost:5555"
private = "private.json"
project = None
dataset = "cyberprobe"
table = "fingerprint"

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
    print project

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
    print "Table %s exists." % table
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
                    "name": "host",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "time",
                    "mode": "REQUIRED",
                    "type": "TIMESTAMP"
                },
                {
                    "name": "device",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "fingerprint",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "trust",
                    "mode": "REQUIRED",
                    "type": "FLOAT"
                }
            ]
        }
    }

    try: 
        table_info = tables.insert(projectId=project, datasetId=dataset,
                                   body=body).execute(http)
        print "Table %s created." % table
    except googleapiclient.errors.HttpError, e:
        print "Table creation failed."
        print e
        sys.exit(0)

############################################################################


# Construct query
query = """
SELECT host, time, device, fingerprint
FROM [%s.%s]
""" % (dataset, table)

# Query body
body = {
    "kind": "bigquery#queryRequest",
    "query": query,
    "timeoutMs": 1000
}

# Run query
job = jobs.query(projectId=project, body=body).execute(http)


# Get JobID
jobid = job["jobReference"]

# Not very helpful response.
if job.has_key("errors") and len(job["errors"]) != 0:
    sys.stderr.write("There were errors\n")
    sys.exit(1)

# If Job is complete...
if job["jobComplete"]:
    # ... use schema and data from queryResult...
    schema = job["schema"]
    rows = job.get("rows",[])
else:

    # ...loop until we have results...
    sys.stderr.write("Waiting...\n")

    while True:

        # Get query results
        job = jobs.getQueryResults(jobId=jobid["jobId"],
                                   projectId=jobid["projectId"],
                                   timeoutMs=1000).execute(http)

        # If job complete...
        if job["jobComplete"]:

            # We have the results in the response.
            schema = job["schema"]
            rows = job.get("rows",[])
            break

        # Job not complete, loop round.
        sys.stderr.write("Waiting...\n")

if rows == None:
    sys.stderr.write("Failed to get rows.\n")
    sys.exit(1)

fingerprints={}

for row in rows:
    row = row["f"]
    host = row[0]["v"]
    tm = float(row[1]["v"])
    device = row[2]["v"]
    fingerprint = row[3]["v"]
    if not fingerprints.has_key(device):
        fingerprints[device] = {}
    if not fingerprints[device].has_key(host):
        fingerprints[device][host] = {}
    if not fingerprints[device][host].has_key(fingerprint):
        fingerprints[device][host][fingerprint] = {
            'oldest': tm,
            'newest': tm
        }
    else:
        if tm < fingerprints[device][host][fingerprint]['oldest']:
            fingerprints[device][host][fingerprint]['oldest'] = tm
        if tm > fingerprints[device][host][fingerprint]['newest']:
            fingerprints[device][host][fingerprint]['newest'] = tm

trust = {}

############################################################################

def handle(msg):

    if msg["action"] != "http_request":
       return

    id = msg["id"]
    device = msg["device"]

    observation = {
        "id": id,
        "action": msg["action"],
        "device": msg["device"],
        "time": msg["time"]
        }

    if msg.has_key("method"):
        observation["method"] = msg["method"]
    if msg.has_key("url"):
        observation["url"] = msg["url"]
    if msg.has_key("command"):
        observation["command"] = msg["command"]
    if msg.has_key("status"):
        observation["status"] = msg["status"]
    if msg.has_key("code"):
        observation["code"] = int(msg["code"])
    if msg.has_key("payload"):
        observation["size"] = len(msg["payload"])
    if msg.has_key("body"):
        observation["size"] = len(msg["body"])
    if msg.has_key("from"):
        observation["from"] = msg["from"]
    if msg.has_key("to"):
        observation["to"] = msg["to"]
    if msg.has_key("header"):
        observation["header"] = {}
        for k in msg["header"]:
            nk = k.replace("-", "").lower()
            if wanted_http_headers.has_key(k):
                observation["header"][nk] = msg["header"][k]
    if msg.has_key("type"):
        observation["type"] = msg["type"]
    if msg.has_key("queries"):
        observation["queries"] = msg["queries"]
    if msg.has_key("answers"):
        if len(msg["answers"]) > 0:
            observation["answers"] = msg["answers"]

    if msg.has_key("src"):
        for v in msg["src"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if cls == "ipv4":
                observation[cls + "_src"] = addr

            if cls == "tcp" or cls == "udp":
                observation[cls + "_src"] = int(addr)

    if msg.has_key("dest"):
        for v in msg["dest"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if cls == "ipv4":
                observation[cls + "_dest"] = addr

            if cls == "tcp" or cls == "udp":
                observation[cls + "_dest"] = int(addr)

    if observation.has_key("header"):
        header = observation["header"]
    else:
        return

    if header.has_key("host"):
        host = header["host"]
    else:
        return

    # Create a fingerprint from a bunch of header fields.
    fingerprint = [
        { "host": host },
        { "useragent": header.get("useragent","") },
        { "location": header.get("location","") },
        { "origin": header.get("origin","") },
        { "accept": header.get("accept","") },
        { "acceptcharset": header.get("acceptcharset","") },
        { "acceptlanguage": header.get("acceptlanguage","") },
        { "connection": header.get("connection","") }
    ]

    # Hash to fingerprint value.
    fingerprint = md5.new(json.dumps(fingerprint)).hexdigest()

    # FIXME: Can't be bothered to convert, just use current time.

    if not fingerprints.has_key(device):
        fingerprints[device] = {}
    if not fingerprints[device].has_key(host):
        fingerprints[device][host] = {}
    if not fingerprints[device][host].has_key(fingerprint):
        fingerprints[device][host][fingerprint] = {
            'oldest': time.time(), 'newest': time.time()
        }
    else:
        fingerprints[device][host][fingerprint]['newest'] = time.time()

    # Work out age of this fingerprint, i.e. difference between now, and the
    # time it was first seen.
    age = fingerprints[device][host][fingerprint]['newest'] - \
          fingerprints[device][host][fingerprint]['oldest']

    # Work out a score, newer fingerprints = 0, older fingerprints = 1
    score = age / trust_time
    if score < 0: score = 0
    if score > 1: score = 1

    # Initialise trust score at zero if not known.
    if not trust.has_key(device):
        trust[device] = {}
    if not trust[device].has_key(host):
        trust[device][host] = 0.0

    # New trust score is average of current trust score, and the score we
    # just worked out.
    trust[device][host] = (trust[device][host] + score) / 2

    # print device, host, trust[device][host]

    # Store in BigQuery
    obj = {
        "device": device,
        "host": host,
        "time": msg["time"],
        "fingerprint": fingerprint,
        "trust": trust[device][host]
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
            print json.dumps(obs)
            print json.dumps(result)
    except googleapiclient.errors.HttpError, e:
        print "Table insert failed."
        print e
    except:
        pass

############################################################################

while True:
    msg = skt.recv()
    handle(json.loads(msg))

