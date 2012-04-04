test:
	DJANGO_SETTINGS_MODULE=urlauth.tests.settings \
	django-admin.py test urlauth

coverage:
	coverage erase
	DJANGO_SETTINGS_MODULE=urlauth.tests.settings \
	coverage run --branch --source=urlauth `which django-admin.py` test urlauth
	coverage html

clean:
	find . -name '*.pyc' -delete
	rm -rf .coverage dist htmlcov MANIFEST
