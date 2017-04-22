import re

import django
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:  # Django 2 detected :)
    from django.urls import reverse, NoReverseMatch
from django.template import Node, Library, TemplateSyntaxError, VariableDoesNotExist
from django.template.loader import get_template
from django.conf import settings
from django.http import QueryDict
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _


# As of django 1.10, template rendering no longer accepts a context, but
# instead accepts only accepts a dict. Up until django 1.8, a context was
# actually required. Fortunately Context takes a single dict parameter,
# so for django >=1.9 we can get away with just passing a unit function.
if django.VERSION < (1, 9, 0):
    from django.template import Context
else:
    def Context(x):
        return x


register = Library()


# Starting from django 1.10 Context object no longer has attribute current_app
# Instead application code could set current_app to HttpRequest object, if so we seek it there
def get_current_app(context):
    try:
        current_app = context.current_app  # django < 1.10 compatible
    except AttributeError:
        try:
            current_app = context.request.current_app
        except AttributeError:
            try:
                current_app = context.request.resolver_match.namespace
            except AttributeError:
                return None
    return current_app


def strToBool(val):
    """
    Helper function to turn a string representation of "true" into
    boolean True.
    """
    if isinstance(val, str):
        val = val.lower()

    return val in ['true', 'on', 'yes', True]


def get_page_url(page_num, current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor):
    """
    Helper function to return a valid URL string given the template tag parameters
    """
    if url_view_name is not None:
        # Add page param to the kwargs list. Overrides any previously set parameter of the same name.
        url_extra_kwargs[url_param_name] = page_num

        try:
            url = reverse(url_view_name, args=url_extra_args, kwargs=url_extra_kwargs, current_app=current_app)
        except NoReverseMatch as e:  # Attempt to load view from application root, allowing the use of non-namespaced view names if your view is defined in the root application
            if settings.SETTINGS_MODULE:

                if django.VERSION < (1, 9, 0):
                    separator  = '.'
                else:
                    separator  = ':' # Namespace separator changed to colon after 1.8

                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + separator + url_view_name, args=url_extra_args, kwargs=url_extra_kwargs, current_app=current_app)
                except NoReverseMatch:
                    raise e # Raise the original exception so the error message doesn't confusingly include something the Developer didn't add to the view name themselves
            else:
                raise e # We can't determine the project name so just re-throw the exception

    else:
        url = ''
        url_get_params = url_get_params or QueryDict(url)
        url_get_params = url_get_params.copy()
        url_get_params[url_param_name] = str(page_num)

    if len(url_get_params) > 0:
        if not isinstance(url_get_params, QueryDict):
            tmp = QueryDict(mutable=True)
            tmp.update(url_get_params)
            url_get_params = tmp
        url += '?' + url_get_params.urlencode()

    if (url_anchor is not None):
        url += '#' + url_anchor

    return url


class BootstrapPagerNode(Node):
    def __init__(self, page, kwargs):
        self.page = page
        self.kwargs = kwargs

    def render(self, context):
        page = self.page.resolve(context)
        kwargs = {}

         # Retrieve variable instances from context where necessary
        for argname, argvalue in self.kwargs.items():
            try:
                kwargs[argname] = argvalue.resolve(context)
            except AttributeError:
                kwargs[argname] = argvalue
            except VariableDoesNotExist:
                kwargs[argname] = None

        previous_label = mark_safe(kwargs.get("previous_label", _("Previous Page")))
        next_label = mark_safe(kwargs.get("next_label", _("Next Page")))
        previous_title = mark_safe(kwargs.get("previous_title", _("Previous Page")))
        next_title = mark_safe(kwargs.get("next_title", _("Next Page")))

        url_view_name = kwargs.get("url_view_name", None)
        if url_view_name is not None:
            url_view_name = str(url_view_name)

        url_param_name = str(kwargs.get("url_param_name", "page"))
        url_extra_args = kwargs.get("url_extra_args", [])
        url_extra_kwargs = kwargs.get("url_extra_kwargs", {})
        url_get_params = kwargs.get("url_get_params", context['request'].GET)
        url_anchor = kwargs.get("url_anchor", None)

        extra_pager_classes = kwargs.get("extra_pager_classes", "")

        previous_page_url = None
        if page.has_previous():
            previous_page_url = get_page_url(page.previous_page_number(), get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        next_page_url = None
        if page.has_next():
            next_page_url = get_page_url(page.next_page_number(), get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        return get_template("bootstrap_pagination/pager.html").render(
            Context({
                'page': page,
                'previous_label': previous_label,
                'next_label': next_label,
                'previous_title': previous_title,
                'next_title': next_title,
                'previous_page_url': previous_page_url,
                'next_page_url': next_page_url,
                'extra_pager_classes': extra_pager_classes,
            }))


class BootstrapPaginationNode(Node):
    """
    Render the Bootstrap pagination bar with the given parameters
    """
    def __init__(self, page, kwargs):
        self.page = page
        self.kwargs = kwargs

    def render(self, context):
        page = self.page.resolve(context)
        kwargs = {}

        # Retrieve variable instances from context where necessary
        for argname, argvalue in self.kwargs.items():
            try:
                kwargs[argname] = argvalue.resolve(context)
            except AttributeError:
                kwargs[argname] = argvalue
            except VariableDoesNotExist:
                kwargs[argname] = None

        # Unpack our keyword arguments, substituting defaults where necessary
        range_length = kwargs.get("range", None)
        if range_length is not None:
            range_length = int(range_length)

        size = kwargs.get("size", None)
        if size is not None:
            size = str(size.lower())
            if size not in ["small", "large"]:
                raise Exception("Optional argument \"size\" expecting one of \"small\", or \"large\"")

        show_prev_next = strToBool(kwargs.get("show_prev_next", "true"))
        previous_label = mark_safe(kwargs.get("previous_label", "&larr;"))
        next_label = mark_safe(kwargs.get("next_label", "&rarr;"))
        show_first_last = strToBool(kwargs.get("show_first_last", "false"))
        first_label = mark_safe(kwargs.get("first_label", "&laquo;"))
        last_label = mark_safe(kwargs.get("last_label", "&raquo;"))
        show_index_range = strToBool(kwargs.get("show_index_range", "false"))

        url_view_name = kwargs.get("url_view_name", None)
        if url_view_name is not None:
            url_view_name = str(url_view_name)

        url_param_name = str(kwargs.get("url_param_name", "page"))
        url_extra_args = kwargs.get("url_extra_args", [])
        url_extra_kwargs = kwargs.get("url_extra_kwargs", {})
        url_get_params = kwargs.get("url_get_params", context['request'].GET)
        url_anchor = kwargs.get("url_anchor", None)

        extra_pagination_classes = kwargs.get("extra_pagination_classes", "")

        # Generage our viewable page range
        page_count = page.paginator.num_pages
        current_page = page.number

        if range_length is None:
            range_min = 1
            range_max = page_count
        else:
            if range_length < 1:
                raise Exception("Optional argument \"range\" expecting integer greater than 0")
            elif range_length > page_count:
                range_length = page_count

            range_length -= 1
            range_min = max(current_page - (range_length // 2), 1)
            range_max = min(current_page + (range_length // 2), page_count)
            range_diff = range_max - range_min
            if range_diff < range_length:
                shift = range_length - range_diff
                if range_min - shift > 0:
                    range_min -= shift
                else:
                    range_max += shift

        page_range = range(range_min, range_max + 1)

        # Generate our URLs (page range + special urls for first, previous, next, and last)
        page_urls = []
        for curpage in page_range:
            if not show_index_range:
                index_range = ""
            elif curpage == page.paginator.num_pages:
                index_range = "%s-%s" % (1 + (curpage - 1) * page.paginator.per_page, len(page.paginator.object_list), )
            else:
                index_range = "%s-%s" % (1 + (curpage - 1) * page.paginator.per_page, curpage * page.paginator.per_page, )

            url = get_page_url(curpage, get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)
            page_urls.append((curpage, index_range, url))

        first_page_url = None
        if current_page >= 1:
            first_page_url = get_page_url(1, get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        last_page_url = None
        if current_page <= page_count:
            last_page_url = get_page_url(page_count, get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        previous_page_url = None
        if page.has_previous():
            previous_page_url = get_page_url(page.previous_page_number(), get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        next_page_url = None
        if page.has_next():
            next_page_url = get_page_url(page.next_page_number(), get_current_app(context), url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params, url_anchor)

        return get_template("bootstrap_pagination/pagination.html").render(
            Context({
                'page': page,
                'size': size,
                'show_index_range': show_index_range,
                'show_prev_next': show_prev_next,
                'show_first_last': show_first_last,
                'previous_label': previous_label,
                'next_label': next_label,
                'first_label': first_label,
                'last_label': last_label,
                'page_urls': page_urls,
                'first_page_url': first_page_url,
                'last_page_url': last_page_url,
                'previous_page_url': previous_page_url,
                'next_page_url': next_page_url,
                'extra_pagination_classes': extra_pagination_classes,
            }))


@register.tag
def bootstrap_paginate(parser, token):
    """
    Renders a Page object as a Twitter Bootstrap styled pagination bar.
    Compatible with Bootstrap 3.x and 4.x only.

    Example::

        {% bootstrap_paginate page_obj range=10 %}


    Named Parameters::

        range - The size of the pagination bar (ie, if set to 10 then, at most,
                10 page numbers will display at any given time) Defaults to
                None, which shows all pages.


        size - Accepts "small", and "large". Defaults to
                    None which is the standard size.

        show_prev_next - Accepts "true" or "false". Determines whether or not
                        to show the previous and next page links. Defaults to
                        "true"


        show_first_last - Accepts "true" or "false". Determines whether or not
                          to show the first and last page links. Defaults to
                          "false"

        previous_label - The text to display for the previous page link.
                         Defaults to "&larr;"

        next_label - The text to display for the next page link. Defaults to
                     "&rarr;"

        first_label - The text to display for the first page link. Defaults to
                      "&laquo;"

        last_label - The text to display for the last page link. Defaults to
                     "&raquo;"

        url_view_name - The named URL to use. Defaults to None. If None, then the
                        default template simply appends the url parameter as a
                        relative URL link, eg: <a href="?page=1">1</a>

        url_param_name - The name of the parameter to use in the URL. If
                         url_view_name is set to None, this string is used as the
                         parameter name in the relative URL path. If a URL
                         name is specified, this string is used as the
                         parameter name passed into the reverse() method for
                         the URL.

        url_extra_args - This is used only in conjunction with url_view_name.
                         When referencing a URL, additional arguments may be
                         passed in as a list.

        url_extra_kwargs - This is used only in conjunction with url_view_name.
                           When referencing a URL, additional named arguments
                           may be passed in as a dictionary.

        url_get_params - The other get parameters to pass, only the page
                         number will be overwritten. Use this to preserve
                         filters.

        url_anchor - The anchor to use in URLs. Defaults to None.

        extra_pagination_classes - A space separated list of CSS class names
                                   that will be added to the top level <ul>
                                   HTML element. In particular, this can be
                                   utilized in Bootstrap 4 installatinos  to
                                   add the appropriate alignment classes from
                                   Flexbox utilites, eg:  justify-content-center
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (Page object reference)" % bits[0])
    page = parser.compile_filter(bits[1])
    kwargs = {}
    bits = bits[2:]

    kwarg_re = re.compile(r'(\w+)=(.+)')

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to bootstrap_pagination paginate tag")
            name, value = match.groups()
            kwargs[name] = parser.compile_filter(value)

    return BootstrapPaginationNode(page, kwargs)


@register.tag
def bootstrap_pager(parser, token):
    """
    Renders a Page object as a Twitter Bootstrap styled pager bar.
    Compatible with Bootstrap 2.x and 3.x only.

    Example::

        {% bootstrap_pager page_obj %}


    Named Parameters::


        previous_label - The label to show for the Previous link (defaults to "Previous Page")

        next_label - The label to show for the Next link (defualts to "Next Page")

        previous_title - The link title for the previous link (defaults to "Previous Page")

        next_title - The link title for the next link (defaults to "Next Page")

        url_view_name - The named URL to use. Defaults to None. If None, then the
                        default template simply appends the url parameter as a
                        relative URL link, eg: <a href="?page=1">1</a>

        url_param_name - The name of the parameter to use in the URL. If
                         url_view_name is set to None, this string is used as the
                         parameter name in the relative URL path. If a URL
                         name is specified, this string is used as the
                         parameter name passed into the reverse() method for
                         the URL.

        url_extra_args - This is used only in conjunction with url_view_name.
                        When referencing a URL, additional arguments may be
                        passed in as a list.

        url_extra_kwargs - This is used only in conjunction with url_view_name.
                           When referencing a URL, additional named arguments
                           may be passed in as a dictionary.

        url_get_params - The other get parameters to pass, only the page
                         number will be overwritten. Use this to preserve
                         filters.

        url_anchor - The anchor to use in URLs. Defaults to None.

        extra_pager_classes - A space separated list of CSS class names
                              that will be added to the top level <ul>
                              HTML element. This could be  used to,
                              as an example, add a class to prevent
                              the pager from showing up when printing.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (Page object reference)" % bits[0])
    page = parser.compile_filter(bits[1])
    kwargs = {}
    bits = bits[2:]

    kwarg_re = re.compile(r'(\w+)=(.+)')

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to bootstrap_pagination pager tag")
            name, value = match.groups()
            kwargs[name] = parser.compile_filter(value)

    return BootstrapPagerNode(page, kwargs)
