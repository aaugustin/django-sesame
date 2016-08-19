export PYTHONPATH:=.:$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE:=sesame.test_settings

test:
	django-admin.py test sesame

coverage:
	python -m coverage erase
	python -m coverage run --branch --source=sesame `which django-admin.py` test sesame
	python -m coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage dist docs/_build htmlcov MANIFEST

flake8:
	flake8 sesame

isort:
	isort --check-only --recursive sesame
