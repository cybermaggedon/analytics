#!/usr/bin/env python

############################################################################

import zmq
import json
import uuid
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

gaffer = os.getenv("GAFFER_URL", "http://gaffer:8080/example-rest/v1")

############################################################################

cybobj = "http://cyberprobe.sf.net/obj/"
cybprop = "http://cyberprobe.sf.net/prop/"
cybtype = "http://cyberprobe.sf.net/type/"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"

rdftype = rdf + "type"
rdfslabel = rdfs + "label"

session = requests.session()

############################################################################

def add_edge(edges, group, s, d):
    edges.append((group, s, d))

############################################################################

def init():
    pass

def output(obs):

    edges = {}
    edges["elements"] = []

    for v in obs:

        elt = {}
        elt["directed"] = True
        elt["class"] = "gaffer.data.element.Edge"
        elt["group"] = v[0]
        elt["source"] = v[1]
        elt["destination"] = v[2]
        elt["properties"] = { "count": 1 }

        edges["elements"].append(elt)

    while True:
        try:
            r = requests.put(gaffer + "/graph/doOperation/add/elements",
                             data=json.dumps(edges),
                             headers={"Content-Type": "application/json"})

            # Ignore a valid HTTP response.  Errors are probably bugs in my
            # code.
            if r.status_code != 204:
                sys.stderr.write("gaffer: Error sending to %s/graph/doOperation/add/elements\n" %
                                 gaffer)
                sys.stderr.write("gaffer: HTTP code: " + str(r.status_code) + "\n")
            break
        except Exception, e:
            # Keep retrying for transport errors
            sys.stderr.write("gaffer: Could not deliver to Gaffer...\n")
            sys.stderr.write("gaffer: Exception: %s\n" % str(e))
            time.sleep(1)

############################################################################

def handle(msg):

    if msg["action"] == "connected_up":
        return

    if msg["action"] == "connected_down":
        return

    edges = []

    sip = None
    sport = None
    dip = None
    dport = None
    proto = None

    if msg.has_key("src"):
        ip = None
        for v in msg["src"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if cls == "ipv4":
                sip = addr

            if cls == "tcp":
                sport = addr
                proto = "tcp"

            if cls == "udp":
                sport = addr
                proto = "udp"

    if msg.has_key("dest"):
        ip = None
        for v in msg["dest"]:
            if v.find(":") < 0:
                cls = v
                addr = ""
            else:
                cls = v[0:v.find(":")]
                addr = v[v.find(":") + 1:]

            if cls == "ipv4":
                dip = addr

            if cls == "tcp":
                dport = addr
                proto = "tcp"

            if cls == "udp":
                dport = addr
                proto = "udp"

    if sip != None and sport != None and dip != None and dport != None and \
       proto == "tcp":
        src = sip + ":" + sport
        dest = dip + ":" + dport
        add_edge(edges, "tcpflow", src, dest)

    if sip != None and sport != None and dip != None and dport != None and \
       proto == "tcp":
        src = sip + ":" + sport
        dest = dip + ":" + dport
        add_edge(edges, "udpflow", src, dest)

    device = msg["device"]
    if msg.has_key("url") and msg["action"] == "http_request":
        add_edge(edges, "http_request", device, msg["url"])

    if msg.has_key("queries") and msg["action"] == "dns":
        for v in msg["queries"]:
            add_edge(edges, "dns_request", device, v)

    output(edges)

############################################################################

init()

while True:
    try:
        msg = skt.recv()
        handle(json.loads(msg))
    except Exception, e:
        sys.stderr.write("gaffer: Exception: %s\n" % str(e))
	sys.stderr.flush()
        time.sleep(0.1)


