.PHONY: all deploy deploy-website test destroy destroy-website

all: deploy test

deploy: deploy-website

deploy-website:
	aws cloudformation deploy \
		--template-file infra/website.yml \
		--stack-name blog-website \
		--parameter-overrides HostedZoneId=$(HOSTED_ZONE_ID)

test:
	behave

destroy: destroy-website

destroy-website:
	aws cloudformation delete-stack --stack-name blog-website
