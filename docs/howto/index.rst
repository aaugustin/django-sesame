User guide
==========

.. toctree::
    :hidden:

    max-age
    outside-views
    per-view
    scope
    faq

Requirements
------------

django-sesame is tested with:

- Django 3.2 (LTS) and 4.0
- Python ≥ 3.6

It builds upon ``django.contrib.auth``. It supports custom user models,
provided they have ``password`` and ``last_login`` fields. Most custom user
models inherit these fields from ``AbstractBaseUser``.

django-sesame is released under the BSD license, like Django itself.
