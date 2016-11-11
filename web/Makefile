
VERSION=0.42

container:
	docker build -t gcr.io/trust-networks/web:${VERSION} .

push:
	gcloud docker -- push gcr.io/trust-networks/web:${VERSION}

