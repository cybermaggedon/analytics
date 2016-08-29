#!/usr/bin/env python

import sys
import wye

# URL of wye service
url = "http://localhost:8080"

context = wye.Context(url)

job = context.define_job(name="cybermon",
                         description="Cybermon stream processor")

dnsact = job.define_python_worker("dns-activity", "dns_activity.py")

webact = job.define_python_worker("web-activity", "web_activity.py")

trust = job.define_python_worker("trust-score", "trust_score.py")

fp = job.define_python_worker("fingerprinter", "fingerprinter.py")
fp.connect("output", [(trust, "input")])

src = job.define_python_worker("subscriber", "cybermon_subscriber.py")
src.connect("output", [(webact, "input"), (dnsact, "input"),
                       (fp, "input")])

job_id = job.implement()

sys.stderr.write("Job %s is running.\n" % job_id)

