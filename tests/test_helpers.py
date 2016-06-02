import django.conf
import django.core.urlresolvers
import django.http

import mock
import unittest2 as unittest

from bootstrap_pagination.templatetags import bootstrap_pagination


class TestHelpers(unittest.TestCase):

    @mock.patch('bootstrap_pagination.templatetags.bootstrap_pagination.'
                'reverse')
    def test_get_page_url_view(self, mock_reverse):
        context = mock.MagicMock()
        context.__contains__.return_value = False
        context.current_app = 'the_current_app'  #
        context.request.current_app = 'the_current_app'
        context.request.GET = {}

        mock_reverse.return_value = "/some_nice_url"
        args = bootstrap_pagination.ArgumentResolver(
            context,
            {
                "url_view_name": 'the_view',
                "url_extra_args": ["arg1"],
                "url_extra_kwargs": {"kwarg": "yes"},
                "url_anchor": "derp"
            }
        )

        url = args.page_url(42)

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
            django.core.urlresolvers.NoReverseMatch(),
            "/some_nice_url"
        ]

        context = mock.MagicMock()
        context.__contains__.return_value = False
        context.current_app = 'the_current_app'
        context.request.current_app = 'the_current_app'
        context.request.GET = {}

        args = bootstrap_pagination.ArgumentResolver(
            context,
            {
                "url_view_name": 'the_view',
                "url_extra_args": ["arg1"],
                "url_extra_kwargs": {"kwarg": "yes"},
                "url_get_params": {"foo": "bar"},
                "url_anchor": "derp"
            }
        )
        url = args.page_url(42)

        self.assertEqual(url, '/some_nice_url?foo=bar#derp')
        mock_reverse.assert_called_with('tests.the_view',
                                        args=['arg1'],
                                        current_app='the_current_app',
                                        kwargs={'kwarg': 'yes',
                                                'page': 42})

    def test_get_page_url_straight(self):
        args = bootstrap_pagination.ArgumentResolver(
            {},
            {
                "current_app": 'the_current_app',
                "url_view_name": None,
                "url_extra_args": ["arg1"],
                "url_extra_kwargs": {"kwarg": "yes"},
                "url_param_name": 'page',
                "url_get_params": django.http.QueryDict("arg2=val"),
                "url_anchor": "derp"
            }
        )

        url = args.page_url(42)

        self.assertIn("arg2=val", url)
        self.assertIn("page=42", url)
        self.assertTrue(url.endswith("#derp"))


if __name__ == '__main__':
    django.conf.settings.configure()
    unittest.main()
