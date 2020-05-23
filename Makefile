export PYTHONPATH:=.:$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE:=tests.settings

style:
	isort --recursive sesame tests
	black sesame tests
	flake8 sesame tests

test:
	django-admin test

coverage:
	coverage erase
	coverage run `which django-admin` test
	coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf *.egg-info .coverage build dist docs/_build htmlcov MANIFEST
