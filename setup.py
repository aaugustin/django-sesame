from __future__ import unicode_literals

import codecs
import os.path

import setuptools

root_dir = os.path.abspath(os.path.dirname(__file__))

description = ("URL-based authentication, an application that provides "
               "one-click login via specially crafted URLs")

with codecs.open(os.path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='django-sesame',
    version='1.6',
    description=description,
    long_description=long_description,
    url='https://github.com/aaugustin/django-sesame',
    author='Aymeric Augustin',
    author_email='aymeric.augustin@m4x.org',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=[
        'sesame',
    ],
)
