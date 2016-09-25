#!/usr/bin/env python

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator
import sys
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

# Start an authenticator for this context.
auth = ThreadAuthenticator(ctxt)
auth.start()
auth.configure_curve(domain='*', location=os.getenv("CURVE_PUBLIC"))

############################################################################

server = ctxt.socket(zmq.PUB)

server_secret_file = os.getenv("CURVE_PRIVATE") + "/publisher.private"
server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
server.curve_secretkey = server_secret
server.curve_publickey = server_public
server.curve_server = True
server.bind('tcp://*:5556')

############################################################################

while True:
    try:
        msg = skt.recv()
        server.send(msg)
    except Exception, e:
        sys.stderr.write("elasticsearch: Exception: %s\n" % str(e))
	sys.stderr.flush()
        time.sleep(0.1)

