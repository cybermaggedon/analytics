#!/usr/bin/env python

import zmq
import json
import sys
import requests
import socket

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

private = "private.json"
project = None
dataset = "cyberprobe"
table = "cyberprobe"

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
        "description": "cyberprobe event table",
        "schema": {
            "fields": [
                {
                    "name": "id",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "time",
                    "mode": "REQUIRED",
                    "type": "TIMESTAMP"
                },
                {
                    "name": "action",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "device",
                    "mode": "REQUIRED",
                    "type": "STRING"
                },
                {
                    "name": "udp_src",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "udp_dest",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "tcp_src",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "tcp_dest",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "ipv4_src",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "ipv4_dest",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "type",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "queries",
                    "mode": "REPEATED",
                    "type": "STRING"
                },
                {
                    "name": "answers",
                    "mode": "REPEATED",
                    "type": "RECORD",
                    "fields": [
                        {
                            "name": "name",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "address",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        }
                    ]
                },
                {
                    "name": "method",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "status",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "code",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "size",
                    "mode": "NULLABLE",
                    "type": "INTEGER"
                },
                {
                    "name": "header",
                    "mode": "NULLABLE",
                    "type": "RECORD",
                    "fields": [
                        {
                            "name": "accept",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "acceptcharset",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "acceptlanguage",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "accesscontrolalloworigin",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "authorization",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "connection",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "contentencoding",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "contentlanguage",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "contentlocation",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "contenttype",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "cookie",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "date",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "etag",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "forwarded",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "host",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "link",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "location",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "origin",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "proxyauthorization",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "referer",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "server",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "setcookie",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "upgrade",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "useragent",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "via",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "wwwauthenticate",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "xforwardedfor",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        },
                        {
                            "name": "xforwardedhost",
                            "mode": "NULLABLE",
                            "type": "STRING"
                        }
                    ]
                },
                {
                    "name": "url",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "from",
                    "mode": "NULLABLE",
                    "type": "STRING"
                },
                {
                    "name": "to",
                    "mode": "REPEATED",
                    "type": "STRING"
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

def init():
    pass

def output(obs, id):

    body = {
        "kind": "biquery#tableDataInsertAllRequest",
        "rows": [
            {
                "json": obs
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

    return

    obs = {
        es_object: obs
        }

    u = "%s%s/%s/%s?ttl=%s" % (es_url, es_index, es_object, id, ttl)

    r = requests.put(u, data=json.dumps(obs),
                     headers={"Content-Type": "application/json"})
    if r.status_code != 201:
        print "Error sending to ElasticSearch"
        print "HTTP code: " + str(r.status_code)

############################################################################

def handle(msg):

    id = msg["id"]

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
#    if msg.has_key("text"):
#        observation["text"] = msg["text"]
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
#        observation["header"] = msg["header"]
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

    output(observation, id)

############################################################################

ctxt = zmq.Context()
skt = ctxt.socket(zmq.SUB)
skt.connect(binding)
skt.setsockopt(zmq.SUBSCRIBE, "")

init()

while True:
    msg = skt.recv()
    handle(json.loads(msg))

