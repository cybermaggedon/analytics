
all: CERT.ca CERT.web CERT.mark

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

KEY.mark:
	openssl rand -out RAND 16384
	openssl genrsa -out KEY.mark -rand RAND 4096
	rm -f RAND

REQ.mark: KEY.mark
	openssl req -key KEY.mark -out REQ.mark -days 710 \
	-new -config CONFIG.mark

CERT.mark: REQ.mark
	openssl x509 -req -in REQ.mark -CAkey KEY.ca \
	-CA CERT.ca -CAcreateserial -CAserial SERIAL \
	-out CERT.mark
	openssl verify -CAfile CERT.ca CERT.mark

clean:
	rm -f KEY.*
	rm -f CERT.*
	rm -f REQ.*
	rm -f RAND
	rm -f SERIAL

