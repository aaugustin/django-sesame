import pathlib

import setuptools

root_dir = pathlib.Path(__file__).parent

description = (
    "URL-based authentication, an application that provides "
    "one-click login via specially crafted URLs"
)

long_description = (root_dir / "README.rst").read_text(encoding="utf-8")

setuptools.setup(
    name="django-sesame",
    version="1.7",
    description=description,
    long_description=long_description,
    url="https://github.com/aaugustin/django-sesame",
    author="Aymeric Augustin",
    author_email="aymeric.augustin@m4x.org",
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["sesame"],
)
