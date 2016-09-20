
all: CERT.ca CERT.web

KEY.ca:
	openssl rand -out RAND 16384
	openssl genrsa -out KEY.ca -rand RAND 4096
	rm -f RAND

CERT.ca: KEY.ca
	openssl req -key KEY.ca -out CERT.ca -days 710 \
		-x509 -new -config CONFIG.ca
	openssl verify -CAfile CERT.ca CERT.ca

KEY.web:
	openssl rand -out RAND 16384
	openssl genrsa -out KEY.web -rand RAND 4096
	rm -f RAND

REQ.web: KEY.web
	openssl req -key KEY.web -out REQ.web -days 710 \
	-new -config CONFIG.web

CERT.web: REQ.web
	openssl x509 -req -in REQ.web -CAkey KEY.ca \
	-CA CERT.ca -CAcreateserial -CAserial SERIAL \
	-out CERT.web
	openssl verify -CAfile CERT.ca CERT.web

clean:
	rm -f KEY.ca CERT.ca
	rm -f KEY.web REQ.web CERT.web
	rm -f RAND
	rm -f SERIAL

