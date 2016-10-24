
VERSION=0.60

container:
	docker build -t gcr.io/trust-networks/analytics:${VERSION} .


push:
	gcloud docker -- push gcr.io/trust-networks/analytics:${VERSION}

