.POONY: build
build: install lint test
	poetry build

.POONY: publish
publish: build
	poetry publish

.POONY: lint
lint:
	pre-commit run

.POONY: install
install:
	poetry install --sync

.POONY: grpcgen
grpcgen:
	poetry run ./scripts/codegen_grpc

.POONY: test
test:
	poetry run tox

.POONY: cov
cov:
	poetry run pytest --cov=easyflake --cov-report=term --cov-report=html
