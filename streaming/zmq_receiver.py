
import time
import sys
import zmq
import random
import json
import socket
import wye
import os

# ---------------------------------------------------------------------------

print "INIT"
ctxt = zmq.Context()
skt = ctxt.socket(zmq.PULL)
skt.bind("tcp://*:5555")
sys.stdout.write("RUNNING\n")
sys.stdout.flush()

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

