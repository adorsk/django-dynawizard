export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH := $(shell pwd)

clean:
	git clean -Xfd

test:
	@flake8 --ignore=W801,E128,E501,W402 dynawizard
	@ coverage run `which django-admin.py` test tests
	@coverage report

.PHONY: clean test
