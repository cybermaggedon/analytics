FROM cybermaggedon/wye:0.04
ENV BINDING=tcp://localhost:5555
RUN pip install hdfs
RUN dnf install -y python-devel
RUN dnf install -y gcc redhat-rpm-config
RUN pip install grpcio
RUN pip install google-cloud
COPY bigquery.py /wye/
COPY cassandra_store.py /wye/
COPY receiver.py /wye/
COPY dns_activity.py /wye/
COPY elasticsearch.py /wye/
COPY fingerprinter.py /wye/
COPY gaffer.py /wye/
COPY trust_score.py /wye/
COPY web_activity.py /wye/
COPY run.sh /wye/
COPY publisher.py /wye/
COPY hadoop.py /wye/
COPY googlestorage.py /wye/
COPY cyber.py /wye/
CMD /wye/run.sh
