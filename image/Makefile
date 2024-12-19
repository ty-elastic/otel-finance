K3S_VERSION ?= latest
ELASTICSEARCH_VERSION ?= 8.17.0
ECK_VERSION ?= 2.15.0

PROJECT_ID ?= $(shell gcloud config get project)

BUILD ?= v1

build:
	packer build -force -var 'project_id=${PROJECT_ID}' -var 'build=${BUILD}' -var 'k3s_version=${K3S_VERSION}' k3s.pkr.hcl
	packer build -force -var 'project_id=${PROJECT_ID}' -var 'build=${BUILD}' -var 'k3s_version=latest' -var 'elastic_stack_version=${ELASTICSEARCH_VERSION}' -var 'elastic_eck_version=${ECK_VERSION}' elastic.pkr.hcl
	packer build -force -var 'project_id=${PROJECT_ID}' -var 'build=${BUILD}' -var 'elastic_stack_version=${ELASTICSEARCH_VERSION}' vscode-elastic.pkr.hcl