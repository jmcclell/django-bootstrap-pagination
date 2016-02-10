#!/usr/bin/env python
import os
import unittest2

import django


def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    try:
        django.setup()
    except AttributeError:  # Happens before django 1.7
        pass

    loader = unittest2.TestLoader()
    tests = loader.discover('tests')
    testRunner = unittest2.runner.TextTestRunner()
    result = testRunner.run(tests)
    if result.errors or result.failures:
        exit(1)


if __name__ == "__main__":
    runtests()
