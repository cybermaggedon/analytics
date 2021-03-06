#!/usr/bin/env python

import zmq
import json
import sys
import requests
import socket
import os
import time

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
    
es_index = os.getenv("ELASTICSEARCH_INDEX", "cyberprobe")
es_object = os.getenv("ELASTICSEARCH_OBJECT", "observation")

if len(sys.argv) < 2:
    es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
else:
    es_url = sys.argv[1]

ttl = "28d"

############################################################################

def init():

    mapping = {
        es_object: {
            "properties": {
                "id": { "type": "keyword" },
                "time": { "type": "date" },
                "url": { "type": "keyword" },
                "queries": { "type": "keyword" },
                "action": { "type": "keyword" },
                "device": { "type": "keyword" },
                "type": {"type": "keyword" },
                "method": {"type": "keyword" },
                "src": {
                    "properties": {
                        "ipv4": { "type": "ip" },
                        "tcp": { "type": "integer"},
                        "udp": { "type": "integer"}
                    }
                },
                "dest": {
                    "properties": {
                        "ipv4": { "type": "ip" },
                        "tcp": { "type": "integer"},
                        "udp": { "type": "integer"}
                    }
                },
                "answers": {
                    "properties": {
                        "name": {
                            "type": "keyword"
                        },
                        "address": {
                            "type": "keyword"
                        }
                    }
                },
                "header": {
                    "properties": {
                        "User-Agent": { "type": "keyword" },
                        "Host": { "type": "keyword" },
                        "Content-Type": { "type": "keyword" },
                        "Server": { "type": "keyword" },
                        "Connection": { "type": "keyword" }
                    }
                }
            }
        }
    }

    u = "%s/%s" % (es_url, es_index)

    while True:
        try: 
            r = requests.put(u)
            if r.status_code != 201 and r.status_code != 200 and r.status_code != 400:
                sys.stderr.write("elasticsearch: Error sending.\n")
                sys.stderr.write("elasticsearch: HTTP code: " + str(r.status_code) + "\n")
            sys.stderr.write("elasticsearch: Index create: %d\n" % r.status_code)
            break
        except Exception, e:
            sys.stderr.write("elasticsearch: Exception: %s\n" % str(e))
            time.sleep(1)

    u = "%s/%s/_mapping/%s" % (es_url, es_index, es_object)

    while True:
        try: 
            r = requests.put(u, data=json.dumps(mapping),
                             headers={"Content-Type": "application/json"})
            if r.status_code != 201 and r.status_code != 200 and r.status_code != 400:
                sys.stderr.write("elasticsearch: Error sending to ElasticSearch\n")
                sys.stderr.write("elasticsearch: HTTP code: " + str(r.status_code) + "\n")
            sys.stderr.write("elasticsearch: Mapping put: %d\n" % r.status_code)
            break
        except Exception, e:
            sys.stderr.write("elasticsearch: Exception: %s\n" % str(e))
            time.sleep(1)


def output(obs, id):

    u = "%s/%s/%s/%s?ttl=%s" % (es_url, es_index, es_object, id, ttl)

    while True:
        try: 
            r = requests.put(u, data=json.dumps(obs),
                             headers={"Content-Type": "application/json"})
            if r.status_code != 201 and r.status_code != 200:
                sys.stderr.write("elasticsearch: Error sending to ElasticSearch\n")
                sys.stderr.write("elasticsearch: HTTP code: " + str(r.status_code) + "\n")
            break
        except Exception, e:
            sys.stderr.write("elasticsearch: Exception: %s\n" % str(e))
            time.sleep(1)

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

init()

while True:
    try:
        msg = skt.recv()
        handle(json.loads(msg))
    except Exception, e:
        sys.stderr.write("elasticsearch: Exception: %s\n" % str(e))
	sys.stderr.flush()
        time.sleep(0.1)

