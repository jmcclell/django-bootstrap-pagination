import django.conf
try:
    from django.core.urlresolvers import NoReverseMatch
except ImportError: # Django 2+
    from django.urls import NoReverseMatch
import django.http

import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from bootstrap_pagination.templatetags import bootstrap_pagination


class TestHelpers(unittest.TestCase):
    def test_strToBool(self):
        self.assertTrue(bootstrap_pagination.strToBool('true'))
        self.assertFalse(bootstrap_pagination.strToBool('false'))

    @mock.patch('bootstrap_pagination.templatetags.bootstrap_pagination.'
                'reverse')
    def test_get_page_url_view(self, mock_reverse):
        mock_reverse.return_value = "/some_nice_url"
        url = bootstrap_pagination.get_page_url(
            page_num=42,
            current_app='the_current_app',
            url_view_name='the_view',
            url_extra_args=["arg1"],
            url_extra_kwargs={"kwarg": "yes"},
            url_param_name='page',
            url_get_params=[],
            url_anchor="derp")

        self.assertEqual(url, '/some_nice_url#derp')
        mock_reverse.assert_called_once_with('the_view',
                                             args=['arg1'],
                                             current_app='the_current_app',
                                             kwargs={'kwarg': 'yes',
                                                     'page': 42})

    @mock.patch('bootstrap_pagination.templatetags.bootstrap_pagination.'
                'reverse')
    def test_get_page_url_view_sub(self, mock_reverse):
        mock_reverse.side_effect = [
            NoReverseMatch(),
            "/some_nice_url"
        ]
        url = bootstrap_pagination.get_page_url(
            page_num=42,
            current_app='the_current_app',
            url_view_name='the_view',
            url_extra_args=["arg1"],
            url_extra_kwargs={"kwarg": "yes"},
            url_param_name='page',
            url_get_params=django.http.QueryDict(""),
            url_anchor="derp")

        self.assertEqual(url, '/some_nice_url#derp')
        if django.VERSION < (1, 9, 0):
            sep = '.'
        else:
            sep = ':'

        mock_reverse.assert_called_with('tests' + sep  + 'the_view',
                                        args=['arg1'],
                                        current_app='the_current_app',
                                        kwargs={'kwarg': 'yes',
                                                'page': 42})

    @mock.patch('bootstrap_pagination.templatetags.bootstrap_pagination.'
                'reverse')
    def test_get_page_url_straight(self, mock_reverse):
        mock_reverse.return_value = "/some_nice_url"
        url = bootstrap_pagination.get_page_url(
            page_num=42,
            current_app='the_current_app',
            url_view_name=None,
            url_extra_args=["arg1"],
            url_extra_kwargs={"kwarg": "yes"},
            url_param_name='page',
            url_get_params=django.http.QueryDict("arg2=val"),
            url_anchor="derp")

        self.assertIn("arg2=val", url)
        self.assertIn("page=42", url)
        self.assertTrue(url.endswith("#derp"))


if __name__ == '__main__':
    django.conf.settings.configure()
    unittest.main()
