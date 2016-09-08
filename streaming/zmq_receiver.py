
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
skt = ctxt.socket(zmq.PULL)
skt.bind("tcp://*:5555")
ctrl = os.fdopen(3, 'w')
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
    except Exception, e:
        sys.stderr.write("receiver: exception: %s\n" % (str(e)))
        time.sleep(0.1)

