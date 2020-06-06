# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime


# -- Project information -----------------------------------------------------

project = 'django-sesame'
copyright = '2012-{}, Aymeric Augustin'.format(datetime.date.today().year)
author = 'Aymeric Augustin'

# The full version, including alpha/beta/rc tags
release = '1.8'


# -- General configuration ---------------------------------------------------

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build']

# Workaround for https://github.com/readthedocs/readthedocs.org/issues/2569.
master_doc = 'index'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = ['custom.css']

html_sidebars = {'**': []}
