FROM cybermaggedon/wye:0.01
ENV BINDING=tcp://localhost:5555
COPY bigquery.py /wye/
COPY cybermon_subscriber.py /wye/
COPY dns_activity.py /wye/
COPY elasticsearch.py /wye/
COPY gaffer.py /wye/
COPY web_activity.py /wye/
COPY cassandra.py /wye/
COPY cyber.py /wye/
COPY fingerprinter.py /wye/
COPY trust_score.py /wye/
COPY run.sh /wye/
CMD /wye/run.sh
