
VERSION=0.19

container:
	docker build -t gcr.io/trust-networks/web:${VERSION} .

push:
	gcloud docker push gcr.io/trust-networks/web:${VERSION}

