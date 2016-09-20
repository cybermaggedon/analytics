
PASSWORD=pass

KEY_SIZE=4096
RAND_AMOUNT=16384

CA_VALIDITY=710
CERT_VALIDITY=710

all: CERT.ca CERT.web CERT.mark PKG.mark.p12

KEY.ca:
	openssl rand -out RAND ${RAND_AMOUNT}
	openssl genrsa -out KEY.ca -rand RAND ${KEY_SIZE}
	rm -f RAND

CERT.ca: KEY.ca CONFIG.ca
	openssl req -key KEY.ca -out CERT.ca -days ${CA_VALIDITY} \
		-x509 -new -config CONFIG.ca
	openssl verify -CAfile CERT.ca CERT.ca

KEY.web:
	openssl rand -out RAND ${RAND_AMOUNT}
	openssl genrsa -out KEY.web -rand RAND ${KEY_SIZE}
	rm -f RAND

REQ.web: KEY.web CONFIG.web
	openssl req -key KEY.web -out REQ.web -days ${CERT_VALIDITY} \
	-new -config CONFIG.web

CERT.web: REQ.web CONFIG.web KEY.ca CERT.ca
	openssl x509 -req -in REQ.web -CAkey KEY.ca \
	-CA CERT.ca -CAcreateserial -CAserial SERIAL \
	-out CERT.web
	openssl verify -CAfile CERT.ca CERT.web

KEY.mark:
	openssl rand -out RAND ${RAND_AMOUNT}
	openssl genrsa -out KEY.mark -rand RAND ${KEY_SIZE}
	rm -f RAND

REQ.mark: KEY.mark
	openssl req -key KEY.mark -out REQ.mark -days ${CERT_VALIDITY} \
	-new -config CONFIG.mark

CERT.mark: REQ.mark CONFIG.mark KEY.ca CERT.ca
	openssl x509 -req -in REQ.mark -CAkey KEY.ca \
	-CA CERT.ca -CAcreateserial -CAserial SERIAL \
	-out CERT.mark
	openssl verify -CAfile CERT.ca CERT.mark

PKG.mark.p12: KEY.mark CERT.mark CERT.ca
	openssl pkcs12 -export -passout pass:${PASSWORD} -inkey KEY.mark \
	-name mark -in CERT.mark -caname 'Trust Networks' \
	-certfile CERT.ca -out $@
	openssl pkcs12 -noout -in PKG.mark.p12 -passin pass:${PASSWORD} -info

create:
	openssl rand -out RAND ${RAND_AMOUNT}
	openssl genrsa -out KEY.create -rand RAND ${KEY_SIZE}
	rm -f RAND
	openssl req -key KEY.create -out REQ.create -days ${CERT_VALIDITY} \
	-new -config CONFIG.create
	openssl x509 -req -in REQ.create -CAkey KEY.ca \
	-CA CERT.ca -CAcreateserial -CAserial SERIAL \
	-out CERT.create
	openssl verify -CAfile CERT.ca CERT.create
	openssl pkcs12 -export -passout pass:${PASSWORD} -inkey KEY.create \
	-name create -in CERT.create -caname 'Trust Networks' \
	-certfile CERT.ca -out PKG.create.p12
	openssl pkcs12 -noout -in PKG.create.p12 -passin pass:${PASSWORD} -info

verify:
	openssl verify -CAfile CERT.ca CERT.ca
	openssl verify -CAfile CERT.ca CERT.web
	openssl verify -CAfile CERT.ca CERT.mark
	openssl pkcs12 -noout -in PKG.mark.p12 -passin pass:${PASSWORD} -info

clean:
	rm -f KEY.*
	rm -f CERT.*
	rm -f REQ.*
	rm -f PKG.*
	rm -f RAND
	rm -f SERIAL

