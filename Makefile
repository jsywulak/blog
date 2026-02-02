.PHONY: all deploy test destroy

all: deploy test

deploy:
	aws cloudformation deploy --template-file infra/networking.yml --stack-name blog-networking

test:
	behave

destroy:
	aws cloudformation delete-stack --stack-name blog-networking
