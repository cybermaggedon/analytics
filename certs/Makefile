
KEY_SIZE=4096
RAND_COUNT=64
RAND_BLOCK=16
RANDOM_DEVICE=/dev/random
DD=dd iflag=fullblock

CA_VALIDITY=710
CERT_VALIDITY=710

all: cert.ca cert.web

#../web/KEY.web ../web/cert.web ../web/cert.ca: ../web/%: %
#	cp $? $@

key.ca:
	${DD} bs=${RAND_BLOCK} count=${RAND_COUNT} if=${RANDOM_DEVICE} of=rand
	openssl genrsa -out $@ -rand rand ${KEY_SIZE}
	rm -f rand

cert.ca: key.ca config.ca
	openssl req -key key.ca -out $@ -days ${CA_VALIDITY} \
		-x509 -new -config config.ca
	openssl verify -CAfile $@ $@

key.web:
	${DD} bs=${RAND_BLOCK} count=${RAND_COUNT} if=${RANDOM_DEVICE} of=rand
	openssl genrsa -out $@ -rand rand ${KEY_SIZE}
	rm -f rand

req.web: key.web config.web
	openssl req -key key.web -out $@ -new -config config.web

cert.web: req.web config.web key.ca cert.ca
	openssl x509 -req -in req.web -CAkey key.ca \
		-CA cert.ca -CAcreateserial -CAserial serial \
		-out $@ -days ${CERT_VALIDITY}
#		-addtrust serverAuth
	openssl verify -CAfile cert.ca $@

clean:
	rm -f key.*
	rm -f cert.*
	rm -f req.*
	rm -f pkg.*
	rm -f rand
	rm -f serial

upload:
	kubectl create secret generic ca-cert \
	  --from-file=cert.ca --from-file=key.ca
	kubectl create secret generic web-cert \
	  --from-file=cert.web --from-file=key.web --from-file=cert.ca

delete:
	-kubectl delete secret ca-cert
	-kubectl delete secret web-cert
