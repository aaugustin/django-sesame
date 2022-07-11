# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os.path
import sys

import django.conf

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.join(os.path.abspath(".."), "src"))


# -- Django setup ------------------------------------------------------------

django.conf.settings.configure(
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
    SECRET_KEY="Anyone who finds a URL will be able to log in. Seriously.",
)
django.setup()


# -- Project information -----------------------------------------------------

project = "django-sesame"
copyright = f"2012-{datetime.date.today().year}, Aymeric Augustin and contributors"
author = "Aymeric Augustin"

# The full version, including alpha/beta/rc tags
release = "3.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]
if "spelling" in sys.argv:
    extensions.append("sphinxcontrib.spelling")

intersphinx_mapping = {
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/"
    ),
    "python": (
        "https://docs.python.org/3",
        None,
    ),
}

# Copied from docs/_ext/djangodocs.py in Django.
def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2b8c67",  # green from logo
        "color-brand-content": "#0c4b33",  # darker green
    },
    "dark_css_variables": {
        "color-brand-primary": "#2b8c67",  # green from logo
        "color-brand-content": "#c9f0dd",  # lighter green
    },
    "sidebar_hide_name": True,
}

html_logo = "_static/django-sesame.svg"

html_favicon = "_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
