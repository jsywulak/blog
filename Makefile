.PHONY: all deploy deploy-networking deploy-website test destroy destroy-networking destroy-website

all: deploy test

deploy: deploy-networking deploy-website

deploy-networking:
	aws cloudformation deploy --template-file infra/networking.yml --stack-name blog-networking

deploy-website:
	aws cloudformation deploy \
		--template-file infra/website.yml \
		--stack-name blog-website \
		--parameter-overrides HostedZoneId=$(HOSTED_ZONE_ID)

test:
	behave

destroy: destroy-website destroy-networking

destroy-networking:
	aws cloudformation delete-stack --stack-name blog-networking

destroy-website:
	aws cloudformation delete-stack --stack-name blog-website
