
import time
import sys
import zmq
import socket
import json

fqdn = socket.getfqdn()
ctxt = zmq.Context()
skt = ctxt.socket(zmq.PULL)
port = skt.bind_to_random_port("tcp://*")

input="tcp://%s:%d" % (fqdn, port)

print "INIT"
print "INPUT:input:%s" % input
print "RUNNING"
sys.stdout.flush()

activity = {}

timeout = 60
curation_time = 5

last_curate=0

def curate():
    now = time.time()

    while True:

        changed = False

        for k in activity:
            if (now - activity[k]["lu"]) > timeout:
                first = activity[k]["first"]
                last = activity[k]["last"]
                device = k[0]
                host = k[1]
                msg = "WEB %s: %s, %s - %s\n" % (device, host, first, last)
                sys.stderr.write(msg)
                del(activity[k])
                changed=True
                break

        if not changed:
            break

def update(device, host, tm):
    key = (device, host)
    if activity.has_key(key):
        activity[key]["last"] = tm
        activity[key]["lu"] = time.time()
    else:
        activity[key] = {}
        activity[key]["first"] = tm
        activity[key]["last"] = tm
        activity[key]["lu"] = time.time()

def handle(msg):
    if not msg["action"] == "http_request":
        return
    
    try:
        update(msg["device"], msg["header"]["Host"], msg["time"])
    except:
        host = None
    
while True:
    try:
        msg = skt.recv(flags=zmq.NOBLOCK)
        handle(json.loads(msg))
    except zmq.error.Again:
        if (time.time() - last_curate) > curation_time:
            curate()
        time.sleep(0.1)

