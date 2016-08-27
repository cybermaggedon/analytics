#!/usr/bin/env python

import sys
import wye

url = "http://localhost:8080"

context = wye.Context(url)

job = context.define_job(name="cybermon",
                         description="Cybermon stream processor")

dnsact = job.define_python_worker("dns-activity", "dns_activity.py")

webact = job.define_python_worker("web-activity", "web_activity.py")

src = job.define_python_worker("subscriber", "cybermon_subscriber.py",
                               {
                                   "output": [
                                       (webact, "input"),
                                       (dnsact, "input")
                                   ]
                               })

job_id = job.implement()

sys.stderr.write("Job %s is running.\n" % job_id)

