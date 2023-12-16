style:
	black src tests
	ruff --fix src tests

test:
	python -m django test --settings=tests.settings

coverage:
	coverage erase
	coverage run -m django test --settings=tests.settings
	coverage html

clean:
	rm -rf .coverage dist docs/_build htmlcov src/django_sesame.egg-info
