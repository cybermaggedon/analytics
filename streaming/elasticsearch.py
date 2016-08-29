#!/usr/bin/env python

import zmq
import json
import sys
import requests
import socket

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
    
es_index = "cyberprobe"
es_object = "observation"

if len(sys.argv) < 2:
    es_url = "http://localhost:9200/"
else:
    es_url = sys.argv[1]

ttl = "1h"

############################################################################

def init():
    pass

def output(obs, id):
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
    if msg.has_key("text"):
        observation["text"] = msg["text"]
    if msg.has_key("payload"):
        pass
    if msg.has_key("body"):
        pass
    if msg.has_key("from"):
        observation["from"] = msg["from"]
    if msg.has_key("to"):
        observation["to"] = msg["to"]
    if msg.has_key("header"):
        observation["header"] = msg["header"]
    if msg.has_key("type"):
        observation["type"] = msg["type"]
    if msg.has_key("queries"):
        observation["queries"] = msg["queries"]
    if msg.has_key("answers"):
        observation["answers"] = msg["answers"]

    observation["src"] = {}
    observation["dest"] = {}

    if msg.has_key("src"):
        for v in msg["src"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if not observation["src"].has_key(cls):
                observation["src"][cls] = []

            observation["src"][cls].append(addr)

    if msg.has_key("dest"):
        for v in msg["dest"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if not observation["dest"].has_key(cls):
                observation["dest"][cls] = []

            observation["dest"][cls].append(addr)

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

