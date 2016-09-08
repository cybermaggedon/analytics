
import time
import sys
import zmq
import random
import json
import socket
import wye
import os

# ---------------------------------------------------------------------------

ctrl = os.fdopen(3, 'w')
ctrl.write("INIT\n")
sockets = wye.parse_outputs(sys.argv[1:])
ctxt = zmq.Context()
skt = ctxt.socket(zmq.SUB)
bindings = os.getenv("ZMQ_BINDING","tcp://localhost:5555")
for v in bindings.split(","):
    skt.connect(v)
    sys.stderr.write("Connected to %s\n" % v)
skt.setsockopt(zmq.SUBSCRIBE, "")
ctrl.write("RUNNING\n")
ctrl.flush()

# ---------------------------------------------------------------------------

def handle(msg):

    for s in sockets["output"]:
        s.send(msg)
    

while True:
    try:
        msg = skt.recv()
        handle(msg)
    except:
        time.sleep(0.1)

