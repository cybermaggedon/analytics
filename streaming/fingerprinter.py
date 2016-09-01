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

sockets = wye.parse_outputs(sys.argv[1:])

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

def handle(msg):

    if msg["action"] != "http_request":
       return

    id = msg["id"]
    device = msg["device"]
    time = msg["time"]

    if msg.has_key("header"):
        header = {}
        for k in msg["header"]:
            nk = k.replace("-", "").lower()
            if wanted_http_headers.has_key(k):
                header[nk] = msg["header"][k]
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

    msg = { "id": id, "device": device, "protocol": "http", "time": time,
            "fingerprint": fingerprint }
    msg = json.dumps(msg)

    for s in sockets["output"]:
        s.send(msg)

############################################################################

while True:
    try:
        msg = skt.recv()
        handle(json.loads(msg))
    except Exception, e:
        sys.stderr.write("fingerprinter: Exception: %s\n" % str(e))
        time.sleep(1)

