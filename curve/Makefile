
all: certs
	-kubectl delete secret analytics-curve-publisher-private
	-kubectl delete secret analytics-curve-client-keys
	kubectl create secret generic analytics-curve-publisher-private \
	  --from-file=publisher.private=publisher.key_secret
	kubectl create secret generic analytics-curve-client-keys \
	  --from-file=dev-client.key

certs:
	./make_certs

