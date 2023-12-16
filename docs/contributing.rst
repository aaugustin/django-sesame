Contributor guide
=================

Develop
-------

Prepare a development environment:

* Install Poetry_.
* Run ``poetry install --extras ua``.
* Run ``poetry shell`` to load the development environment.

Make changes:

* Make changes to the code, tests, or docs.
* Run ``make style`` and fix errors.
* Run ``make test`` or ``make coverage`` to run the set suite — it's fast!

Iterate until you're happy.

Check quality and submit your changes:

* Install tox_.
* Run ``tox`` to test across Python and Django versions — it's slower.
* Submit a pull request.

.. _Poetry: https://python-poetry.org/
.. _tox: https://tox.readthedocs.io/

Release
-------

Check that the changelog is complete and add the date of the release.

Increment version number X.Y in ``docs/conf.py`` and ``pyproject.toml``.

Commit, tag, and push the change:

.. code-block:: console

    $ git commit -m "Bump version number".
    $ git tag X.Y
    $ git push
    $ git push --tags

Build and publish the new version:

.. code-block:: console

    $ poetry build
    $ poetry publish
