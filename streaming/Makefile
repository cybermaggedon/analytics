
VERSION=0.69

container:
	docker build -t gcr.io/trust-networks/analytics:${VERSION} .


push:
	gcloud docker -- push gcr.io/trust-networks/analytics:${VERSION}

