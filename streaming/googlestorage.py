#!/usr/bin/env python

import zmq
import json
import sys
import requests
import socket
import os
import time, datetime
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import uuid

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

private = os.getenv("KEY", "private.json")
bucket_name = "trustnetworks"
basedir = "cyberprobe/"

############################################################################

# Creds
credentials = ServiceAccountCredentials.from_json_keyfile_name(private)

############################################################################

client = storage.Client(credentials=credentials)

try:
    client.create_bucket(bucket_name)
except Exception, e:
    sys.stderr.write("googlestorage: Bucket %s create failed (ignored): %s\n" %
                     (bucket_name, e))
    sys.stderr.flush()

bucket = client.get_bucket(bucket_name)

data=[]

count=0
last=time.time()

max_batch=64 * 1024 * 1024
max_time=300

def handle(msg):

    global data, count, last

    data.append(msg)

    count = count + len(msg)

    if (count > max_batch) or ((time.time() - last) > max_time):

        u = str(uuid.uuid4())

        dir = datetime.datetime.utcnow().strftime("%Y-%m-%d/%H-%M")
        dir = basedir + dir

        filedata = "\n".join(data)
        path = dir + "/" + u
        
        try:
            blob = bucket.blob(path)
            blob.upload_from_string(filedata)
            print "Google storage write: %s." % path
        except Exception, e:
            sys.stderr.write("googlestorage: creation failed (ignored): %s\n" %
                             e)
	    sys.stderr.flush()

        data = []
        count = 0
        last = time.time()

############################################################################

while True:
    try:
        msg = skt.recv()
        handle(msg)
    except Exception, e:
        sys.stderr.write("googlestorage: Exception: %s\n" % str(e))
	sys.stderr.flush()
        time.sleep(0.1)

