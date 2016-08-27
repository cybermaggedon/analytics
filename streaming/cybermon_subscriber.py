
import time
import sys
import zmq
import random
import json
import socket
import wye

print "INIT"

# ---------------------------------------------------------------------------

sockets = wye.parse_outputs(sys.argv[1:])

# ---------------------------------------------------------------------------

ctxt = zmq.Context()
skt = ctxt.socket(zmq.SUB)
port = skt.connect("tcp://localhost:5555")
skt.setsockopt(zmq.SUBSCRIBE, "")

# ---------------------------------------------------------------------------

print "RUNNING"
sys.stdout.flush()

def handle(msg):

    for s in sockets["output"]:
        s.send(msg)
    

while True:
    msg = skt.recv()
    handle(msg)

