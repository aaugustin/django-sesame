test:
	PYTHONPATH=.:$(PYTHONPATH) \
	DJANGO_SETTINGS_MODULE=sesame.tests.settings \
	django-admin.py test sesame --traceback

coverage:
	coverage erase
	PYTHONPATH=.:$(PYTHONPATH) \
	DJANGO_SETTINGS_MODULE=sesame.tests.settings \
	coverage run --branch --source=sesame `which django-admin.py` test sesame
	coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage dist docs/_build htmlcov MANIFEST
