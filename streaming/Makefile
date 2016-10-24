
VERSION=0.59

container:
	docker build -t gcr.io/trust-networks/analytics:${VERSION} .


push:
	gcloud docker -- push gcr.io/trust-networks/analytics:${VERSION}

