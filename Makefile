export PYTHONPATH:=.:$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE:=sesame.test_settings

test:
	django-admin.py test sesame

coverage:
	coverage erase
	coverage run --branch --source=sesame `which django-admin.py` test sesame
	coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage dist docs/_build htmlcov MANIFEST
