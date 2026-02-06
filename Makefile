.PHONY: all deploy deploy-website deploy-content test destroy destroy-website empty-website-bucket

all: deploy test

deploy: deploy-website deploy-content

deploy-website:
	$(eval HOSTED_ZONE_ID := $(shell aws route53 list-hosted-zones-by-name --dns-name jsywulak.com --query "HostedZones[?Name=='jsywulak.com.'].Id" --output text | sed 's|/hostedzone/||'))
	aws cloudformation deploy \
		--template-file infra/website.yml \
		--stack-name blog-website \
		--parameter-overrides HostedZoneId=$(HOSTED_ZONE_ID)
	aws cloudformation wait stack-create-complete --stack-name blog-website || \
		aws cloudformation wait stack-update-complete --stack-name blog-website

deploy-content:
	aws s3 sync site/ s3://jsywulak.com/

test:
	behave

destroy: destroy-website

empty-website-bucket:
	aws s3 rm s3://jsywulak.com --recursive
	aws s3 rb s3://jsywulak.com

destroy-website: empty-website-bucket
	aws cloudformation delete-stack --stack-name blog-website
	aws cloudformation wait stack-delete-complete --stack-name blog-website
