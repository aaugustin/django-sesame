style:
	isort --recursive src tests
	black src tests
	flake8 src tests

test:
	python -m django test --settings=tests.settings

coverage:
	coverage erase
	coverage run -m django test --settings=tests.settings
	coverage html

clean:
	rm -rf .coverage dist django_sesame.egg-info docs/_build htmlcov
