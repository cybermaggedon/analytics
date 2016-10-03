#!/usr/bin/env python

import sys
import wye

# URL of wye service
url = "http://localhost:8080"

context = wye.Context(url)

job = context.define_job(name="cybermon",
                         description="Cybermon stream processor")


trust = job.define_python_worker("trust-score", "trust_score.py")

fp = job.define_python_worker("fingerprinter", "fingerprinter.py")
fp.connect("output", [(trust, "input")])

dnsact = job.define_python_worker("dns-activity", "dns_activity.py")
webact = job.define_python_worker("web-activity", "web_activity.py")
bq = job.define_python_worker("bigquery", "bigquery.py")
es = job.define_python_worker("elasticsearch", "elasticsearch.py")
gaffer = job.define_python_worker("gaffer", "gaffer.py")
cassandra = job.define_python_worker("cassandra", "cassandra_store.py")
hadoop = job.define_python_worker("hadoop", "hadoop.py")
publisher = job.define_python_worker("publisher", "publisher.py")

recv = job.define_python_worker("receiver", "receiver.py")
recv.connect("output",
             [(webact, "input"), (dnsact, "input"), (fp, "input"),
              (bq, "input"), (es, "input"), (cassandra, "input"),
              (hadoop, "input"), (publisher, "input")])

job_id = job.implement()

sys.stderr.write("Job %s is running.\n" % job_id)

