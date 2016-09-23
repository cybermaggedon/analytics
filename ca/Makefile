
VERSION=0.11

all: container

container:
	docker build -t gcr.io/trust-networks/ca:${VERSION} .

push:
	gcloud docker push gcr.io/trust-networks/ca:${VERSION}

