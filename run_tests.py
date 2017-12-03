#!/usr/bin/env python
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest #python3


import django


def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    try:
        django.setup()
    except AttributeError:  # Happens before django 1.7
        pass

    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    testRunner = unittest.runner.TextTestRunner()
    result = testRunner.run(tests)
    if result.errors or result.failures:
        exit(1)


if __name__ == "__main__":
    runtests()
