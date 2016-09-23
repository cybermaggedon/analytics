
VERSION=0.18

container:
	docker build -t gcr.io/trust-networks/web:${VERSION} .

push:
	gcloud docker push gcr.io/trust-networks/web:${VERSION}

