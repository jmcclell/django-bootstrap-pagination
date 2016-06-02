import unittest2 as unittest

import lxml.html

try:
    from django.template.loader import get_template_from_string
except ImportError:
    from django.template import Engine
    get_template_from_string = Engine.get_default().from_string

from django.template import Context
import django.http
from django.core.paginator import Paginator

from tests.utils import override_settings


class PagerTestCase(unittest.TestCase):
    def test_example(self):
        template = get_template_from_string("""
            {% load bootstrap_pagination %}
            {% bootstrap_pager page_obj %}
        """)

        objects = ["obj%02x" % idx
                   for idx in range(30)]

        paginator = Paginator(objects, 10)

        c = Context({'page_obj': paginator.page(2),
                     'request': django.http.HttpRequest()})
        html = lxml.html.fragment_fromstring(template.render(c))
        self.assertEqual(html.get('class'), 'pager')

    @override_settings(BOOTSTRAP_VERSION=4)
    def test_bs4(self):
        template = get_template_from_string("""
            {% load bootstrap_pagination %}
            {% bootstrap_pager page_obj %}
        """)

        objects = ["obj%02x" % idx
                   for idx in range(30)]

        paginator = Paginator(objects, 10)

        c = Context({'page_obj': paginator.page(2),
                     'request': django.http.HttpRequest()})
        html = lxml.html.fragment_fromstring(template.render(c))

        self.assertEqual(
            html.cssselect('nav>ul.pager>li>a')[0].text.strip(),
            'Previous Page')
