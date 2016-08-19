export PYTHONPATH:=.:$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE:=sesame.test_settings

test:
	django-admin test sesame

coverage:
	coverage erase
	coverage run --branch --source=sesame `which django-admin` test sesame
	coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf *.egg-info .coverage build dist docs/_build htmlcov MANIFEST

flake8:
	flake8 sesame

isort:
	isort --check-only --recursive sesame
