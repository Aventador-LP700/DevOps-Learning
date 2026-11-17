.PHONY: help build lab up down report test check clean k8s-up k8s-test k8s-down scan
help:
	@echo 'build lab report up down test check clean k8s-up k8s-test k8s-down scan'
build:
	docker compose build lab
lab: build
	docker compose run --rm lab
report:
	python3 scripts/export_reports.py
up: build
	docker compose up -d --wait app
down:
	docker compose down
test:
	python3 -m unittest discover -s tests -v
check: test
	python3 -m compileall -q app lab scripts tests
	docker compose config --quiet
clean:
	docker compose down --volumes --remove-orphans
k8s-up:
	bash scripts/k8s.sh up
k8s-test:
	bash scripts/k8s.sh test
k8s-down:
	bash scripts/k8s.sh down
scan: build
	bash scripts/scan.sh
