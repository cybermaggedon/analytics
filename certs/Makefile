
KEY_SIZE=4096
RAND_COUNT=64
RAND_BLOCK=16
RANDOM_DEVICE=/dev/random
DD=dd iflag=fullblock

CA_VALIDITY=710
CERT_VALIDITY=710

all: CERT.ca CERT.web

#../web/KEY.web ../web/CERT.web ../web/CERT.ca: ../web/%: %
#	cp $? $@

KEY.ca:
	${DD} bs=${RAND_BLOCK} count=${RAND_COUNT} if=${RANDOM_DEVICE} of=RAND
	openssl genrsa -out KEY.ca -rand RAND ${KEY_SIZE}
	rm -f RAND

CERT.ca: KEY.ca CONFIG.ca
	openssl req -key KEY.ca -out CERT.ca -days ${CA_VALIDITY} \
		-x509 -new -config CONFIG.ca
	openssl verify -CAfile CERT.ca CERT.ca

KEY.web:
	${DD} bs=${RAND_BLOCK} count=${RAND_COUNT} if=${RANDOM_DEVICE} of=RAND
	openssl genrsa -out KEY.web -rand RAND ${KEY_SIZE}
	rm -f RAND

REQ.web: KEY.web CONFIG.web
	openssl req -key KEY.web -out REQ.web -new -config CONFIG.web

CERT.web: REQ.web CONFIG.web KEY.ca CERT.ca
	openssl x509 -req -in REQ.web -CAkey KEY.ca \
		-CA CERT.ca -CAcreateserial -CAserial SERIAL \
		-out CERT.web -days ${CERT_VALIDITY} \
		-addtrust serverAuth
	openssl verify -CAfile CERT.ca CERT.web

clean:
	rm -f KEY.*
	rm -f CERT.*
	rm -f REQ.*
	rm -f PKG.*
	rm -f RAND
	rm -f SERIAL

upload:
	kubectl create secret generic ca-cert \
	  --from-file=cert.ca=CERT.ca --from-file=key.ca=KEY.ca
	kubectl create secret generic web-cert \
	  --from-file=cert.web=CERT.web --from-file=key.web=KEY.web \
	  --from-file=cert.ca=CERT.ca

delete:
	-kubectl delete secret ca-cert
	-kubectl delete secret web-cert