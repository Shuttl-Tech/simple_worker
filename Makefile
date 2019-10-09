.PHONY: test integration_test build upload

test:
	pytest tests

integration_test:
	pytest -m 'integration' tests

build:
	if [ -d "dist" ]; then rm -Rf dist/*; fi
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

release:
	git tag v$(shell python3 setup.py --version)
	git push origin v$(shell python3 setup.py --version)

bump_version:
	bumpversion --current-version $(shell python3 setup.py --version) patch setup.py

commit_version_update:
	git add setup.py
	git commit -m "Updated version"

bump_commit_upload: bump_version commit_version_update upload

