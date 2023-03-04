build: install lint test
	poetry build

publish: build
	poetry publish

lint:
	pre-commit run

install:
	poetry install --sync

grpcgen:
	poetry run ./scripts/codegen_grpc

test:
	poetry run tox
