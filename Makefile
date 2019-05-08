export PYTHONPATH:=.:$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE:=sesame.test_settings

style:
	isort --recursive sesame
	black sesame
	flake8 sesame

test:
	django-admin test sesame

coverage:
	coverage erase
	coverage run `which django-admin` test sesame
	coverage html

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf *.egg-info .coverage build dist docs/_build htmlcov MANIFEST
