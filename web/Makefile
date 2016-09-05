
VERSION=mvp2l

container:
	docker build -t web .
#	docker build -t gcr.io/trust-networks/web:${VERSION} .


push:
	gcloud docker push gcr.io/trust-networks/web:${VERSION}

