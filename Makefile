.PHONY: test integration_test build upload

test:
	pytest tests

integration_test:
	pytest -m 'integration' tests

build:
	rm dist/*
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*
