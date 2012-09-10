publish:
	python setup.py sdist upload

lint:
ifndef skip-dependency-checks
	pip install -Ur requirements.lint.txt
endif
	flake8 src/

test:
	python setup.py nosetests

.PHONY: lint publish test
