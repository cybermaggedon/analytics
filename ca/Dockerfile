FROM fedora:24

RUN dnf install -y openssl
RUN mkdir /ca
COPY create /ca/
COPY CONFIG.create /ca/

CMD while true; do sleep 1000; done

