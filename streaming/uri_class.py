#!/usr/bin/env python

import zmq
import json
import sys
import requests
import md5
import time
import socket
import os
from urlparse import urlparse

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import googleapiclient.errors

############################################################################

private = os.getenv("KEY", "private.json")
project = os.getenv("BIGQUERY_PROJECT", None)
dataset = os.getenv("BIGQUERY_DATASET","cyberprobe")
table = os.getenv("URI_TABLE","uri_classification")

############################################################################

fqdn = socket.getfqdn()
ctxt = zmq.Context()
skt = ctxt.socket(zmq.PULL)
port = skt.bind_to_random_port("tcp://*")

input="tcp://%s:%d" % (fqdn, port)

ctrl = os.fdopen(3, 'w')
ctrl.write("INIT\n")
ctrl.write("INPUT:input:%s\n" % input)
ctrl.write("RUNNING\n")
ctrl.flush()

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
    sys.stderr.write("uri_class: Table %s exists.\n" % table)
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
                    "name": "id",
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
                    "name": "uri",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "classification",
                    "mode": "REQUIRED",
                    "type": "INTEGER"
                }
            ]
        }
    }

    try: 
        table_info = tables.insert(projectId=project, datasetId=dataset,
                                   body=body).execute(http)
        sys.stderr.write("uri_class: Table %s created.\n" % table)
    except googleapiclient.errors.HttpError, e:
        sys.stderr.write("uri_class: Table creation failed.\n")
        sys.stderr.write("uri_class: %s\n" % str(e))
        sys.exit(0)

############################################################################

def handle(msg):

    try:

        sys.stderr.flush()
        id = msg["id"]
        device = msg["device"]
        uri = msg["url"]
        tm = msg["time"]

        o = urlparse(uri)
        host = o.netloc

    except:
        return

    while True:
        try:
            u = "http://url-classifier:8080/" + host
            r = requests.get(u)
            if r.status_code != 200:
                sys.stderr.write("uri_class: Error calling host classifier\n")
                sys.stderr.write("uri_class: %s\n" % u)
                sys.stderr.write("uri_class: HTTP code: " + str(r.status_code) + "\n")
                break
            classif = r.json()["result"]
            break
        except Exception, e:
            sys.stderr.write("uri_class: Exception: %s\n" % str(e))
            time.sleep(1)

    # Store in BigQuery
    obj = {
        "device": device,
        "id": id,
        "host": host,
        "time": tm,
        "uri": uri,
        "classification": classif
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
            sys.stderr.write("uri_class: %s\n" % json.dumps(result))
    except googleapiclient.errors.HttpError, e:
        sys.stderr.write("uri_class: Table insert failed.\n")
        sys.stderr.write("uri_class: %s\n" % str(e))
    except Exception, e:
        sys.stderr.write("uri_class: Exception.\n")
        sys.stderr.write("uri_class: %s\n" % str(e))

############################################################################

while True:
    try:
        msg = skt.recv()
        handle(json.loads(msg))
    except Exception, e:
        sys.stderr.write("uri_class: Exception: %s\n" % str(e))
        sys.stderr.flush()
        time.sleep(0.01)

