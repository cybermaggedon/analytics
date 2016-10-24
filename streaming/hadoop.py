#!/usr/bin/env python

import zmq
import json
import sys
import requests
import socket
import os
import time, datetime
import hdfs
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
    
url = os.getenv("HDFS_URL", "http://hdfs:50070")
user = "hdfs"
basedir = "/cyberprobe/"

############################################################################

client = hdfs.client.InsecureClient(url, user=user)

try:
    client.makedirs(basedir)
except Exception, e:
    sys.stderr.write("hadoop: Directory %s creation failed (ignored): %s\n" %
                     (basedir, e))
    sys.stderr.flush()

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

        try:
            client.makedirs(dir)
        except Exception, e:
            sys.stderr.write("hadoop: create %s failed (ignored): %s\n" %
                             (basedir, e))
	    sys.stderr.flush()

        filedata = "\n".join(data)
        path = dir + "/" + u
        
        try:
            with client.write(path, encoding='utf-8') as writer:
                writer.write(filedata)
            print "HDFS write: %s." % path
        except Exception, e:
            sys.stderr.write("hadoop: creation failed for %s (ignored): %s\n" %
                             (path, e))
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
        sys.stderr.write("hadoop: Exception: %s\n" % str(e))
	sys.stderr.flush()
        time.sleep(0.1)

