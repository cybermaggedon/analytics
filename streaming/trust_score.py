#!/usr/bin/env python

import zmq
import json
import sys
import requests
import md5
import time
import socket

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import googleapiclient.errors

############################################################################

trust_time = 86400

############################################################################

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
                    "name": "device",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "protocol",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
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
SELECT device, protocol, host, time, fingerprint, trust
FROM [%s.%s]
LIMIT 100000
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
trust = {}

for row in rows:
    row = row["f"]
    device = row[0]["v"]
    protocol = row[1]["v"]
    host = row[2]["v"]
    tm = float(row[3]["v"])
    fingerprint = row[4]["v"]
    tr = row[5]["v"]

    fkey = (device, protocol, host, fingerprint)

    if not fingerprints.has_key(fkey):
        fingerprints[fkey] = {
            'oldest': tm,
            'newest': tm
        }
    else:
        if tm < fingerprints[fkey]['oldest']:
            fingerprints[fkey]['oldest'] = tm
        if tm > fingerprints[fkey]['newest']:
            fingerprints[fkey]['newest'] = tm

    tkey = (device, protocol, host)

    if not trust.has_key(tkey):
        trust[tkey] = tr
    else:
        if tr > trust[tkey]:
            trust[tkey] = tr

############################################################################

def handle(msg):

    try:
        id = msg["id"]
        device = msg["device"]
        host = msg["host"]
        protocol = msg["protocol"]
        fingerprint = msg["fingerprint"]
    except:
        return

    # FIXME: Can't be bothered to convert, just use current time.

    fkey = (device, protocol, host, fingerprint)
    
    if not fingerprints.has_key(fkey):
        fingerprints[fkey] = {
            'oldest': time.time(), 'newest': time.time()
        }
    else:
        fingerprints[fkey]['newest'] = time.time()

    # Work out age of this fingerprint, i.e. difference between now, and the
    # time it was first seen.
    age = fingerprints[fkey]['newest'] - fingerprints[fkey]['oldest']

    # Work out a score, newer fingerprints = 0, older fingerprints = 1
    score = age / trust_time
    if score < 0: score = 0
    if score > 1: score = 1

    # Initialise trust score at zero if not known.
    tkey = (device, protocol, host)
    if not trust.has_key(tkey):
        trust[tkey] = 0.0

    # New trust score is average of current trust score, and the score we
    # just worked out.
    trust[tkey] = (tkey + score) / 2

    # Store in BigQuery
    obj = {
        "device": device,
        "protocol": protocol,
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
    try:
        msg = skt.recv()
        handle(json.loads(msg))
    except:
        time.sleep(0.1)

