FROM fedora:24

RUN dnf install -y openssl
RUN mkdir /ca
COPY CERT.ca /ca/
COPY KEY.ca /ca/
COPY create /ca/
# This is a stateless CA. FIXME: Should keep a list of certs issued and serial
# number to avoid dupes.
#COPY SERIAL /ca/
COPY CONFIG.create /ca/

CMD while true; do sleep 1000; done

