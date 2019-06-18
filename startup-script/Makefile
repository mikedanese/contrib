TAG=v2
IMAGE=gcr.io/mikedanese-k8s/startup-script

.PHONY: build push

build:
	docker build --pull -t $(IMAGE):$(TAG) .

push: build
	docker push $(IMAGE):$(TAG)
