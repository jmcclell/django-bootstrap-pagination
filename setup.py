# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-bootstrap-pagination',
    version='0.1.1',
    author=u'Jason McClellan',
    author_email='jason@jasonmccllelan.net',
    packages=find_packages(),
    url='https://github.com/jmcclell/django-bootstrap-pagination',
    license='MIT licence, see LICENCE',
    description='Render Django Page objects as Bootstrap Pagination compatible HTML',
    long_description=open('README.markdown').read(),
    zip_safe=False,
    include_package_data=True
)