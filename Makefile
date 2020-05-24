style:
	isort --recursive sesame tests
	black sesame tests
	flake8 sesame tests

test:
	python -m django test --settings=tests.settings

coverage:
	coverage erase
	coverage run -m django test --settings=tests.settings
	coverage html

clean:
	rm -rf .coverage dist django_sesame.egg-info docs/_build htmlcov
