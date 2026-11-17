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
	python3 -m compileall -q app lab labs scripts tests
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

.PHONY: test-new browser http http-vulnerable sast fs-scan zap
test-new:
	python3 -m unittest discover -s tests -p test_extended_labs.py -v
browser:
	python3 -m unittest discover -s tests -p browser_labs.py -v
http:
	python3 -m labs.web --port 8081
http-vulnerable:
	python3 -m labs.web --port 8081 --vulnerable --enable-vulnerable-labs
sast:
	python3 -m scripts.sast
fs-scan:
	python3 -m scripts.fs_scan
zap:
	python3 -m scripts.zap
