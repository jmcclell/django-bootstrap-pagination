# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


with open('README.rst', 'rb') as readme:
    readme_text = readme.read().decode('utf-8')

setup(
    name='django-bootstrap-pagination',
    version='1.5.1',
    keywords="django bootstrap pagination templatetag",
    author=u'Jason McClellan',
    author_email='jason@jasonmccllelan.net',
    packages=find_packages(),
    url='https://github.com/jmcclell/django-bootstrap-pagination',
    license='MIT licence, see LICENCE',
    description='Render Django Page objects as Bootstrap 3.x Pagination compatible HTML',
    long_description=readme_text,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ]
)
