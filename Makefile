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

bump_version:
	bumpversion --current-version $(shell python3 setup.py --version) patch setup.py

commit_version_update:
	git add setup.py
	git commit -m "Updated version"

bump_commit_upload: bump_version commit_version_update upload

