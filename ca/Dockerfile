FROM fedora:24

RUN dnf install -y openssl
RUN mkdir /ca
COPY create /usr/local/bin/
COPY CONFIG.create /usr/local/etc/

CMD while true; do sleep 1000; done

