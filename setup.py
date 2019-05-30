# -*- coding: utf-8 -*-
import os

from distutils.core import setup
from setuptools import find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'rb') as readme:
    readme_text = readme.read().decode('utf-8')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bootstrap-pagination',
    version='1.7.1',
    keywords="django bootstrap pagination templatetag",
    author=u'Jason McClellan<jason@jasonmcclellan.io>, Koert van der Veer<koert@ondergetekende.nl>',
    author_email='jason@jasonmccllelan.io',
    packages=find_packages(),
    url='https://github.com/jmcclell/django-bootstrap-pagination',
    license='MIT licence, see LICENCE',
    description='Render Django Page objects as Bootstrap 3.x/4.x Pagination compatible HTML',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Framework :: Django",
        "Framework :: Django :: 1.4",
        "Framework :: Django :: 1.5",
        "Framework :: Django :: 1.6",
        "Framework :: Django :: 1.7",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ]
)
