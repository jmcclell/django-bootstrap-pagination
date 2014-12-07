import re

from django.core.urlresolvers import reverse, NoReverseMatch
from django.template import Context, Node, Library, TemplateSyntaxError, VariableDoesNotExist
from django.template.loader import get_template
from django.conf import settings
from django.http import QueryDict

register = Library()


def strToBool(val):
    """
    Helper function to turn a string representation of "true" into
    boolean True.
    """
    return val.lower() == "true"


def get_page_url(page_num, current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params):
    """
    Helper function to return a valid URL string given the template tag parameters
    """
    if url_view_name is not None:
        # Add page param to the kwargs list. Overrides any previously set parameter of the same name.
        url_extra_kwargs[url_param_name] = page_num

       # This bit of code comes from the default django url tag
        try:
            url = reverse(url_view_name, args=url_extra_args, kwargs=url_extra_kwargs, current_app=current_app)
        except NoReverseMatch as e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                url = reverse(project_name + '.' + url_view_name, args=url_extra_args, kwargs=url_extra_kwargs, current_app=current_app)
            else:
                raise e

    else:
        url = ''
        url_get_params = url_get_params or QueryDict(url)
        url_get_params = url_get_params.copy()
        url_get_params[url_param_name] = page_num

    if (len(url_get_params) > 0):
        url += '?' + url_get_params.urlencode()

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

        previous_label = str(kwargs.get("previous_label", "Previous Page"))
        next_label = str(kwargs.get("next_label", "Next Page"))
        previous_title = str(kwargs.get("previous_title", "Previous Page"))
        next_title = str(kwargs.get("next_title", "Next Page"))

        url_view_name = kwargs.get("url_view_name", None)
        if url_view_name is not None:
            url_view_name = str(url_view_name)

        url_param_name = str(kwargs.get("url_param_name", "page"))
        url_extra_args = kwargs.get("url_extra_args", [])
        url_extra_kwargs = kwargs.get("url_extra_kwargs", {})
        url_get_params = kwargs.get("url_get_params", context['request'].GET)

        previous_page_url = None
        if page.has_previous():
            previous_page_url = get_page_url(page.previous_page_number(), context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        next_page_url = None
        if page.has_next():
            next_page_url = get_page_url(page.next_page_number(), context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        return get_template("bootstrap_pagination/pager.html").render(
            Context({
                'page': page,
                'previous_label': previous_label,
                'next_label': next_label,
                'previous_title': previous_title,
                'next_title': next_title,
                'previous_page_url': previous_page_url,
                'next_page_url': next_page_url
            }, autoescape=False))


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
        previous_label = str(kwargs.get("previous_label", "&larr;"))
        next_label = str(kwargs.get("next_label", "&rarr;"))
        show_first_last = strToBool(kwargs.get("show_first_last", "false"))
        first_label = str(kwargs.get("first_label", "&laquo;"))
        last_label = str(kwargs.get("last_label", "&raquo;"))

        url_view_name = kwargs.get("url_view_name", None)
        if url_view_name is not None:
            url_view_name = str(url_view_name)

        url_param_name = str(kwargs.get("url_param_name", "page"))
        url_extra_args = kwargs.get("url_extra_args", [])
        url_extra_kwargs = kwargs.get("url_extra_kwargs", {})
        url_get_params = kwargs.get("url_get_params", context['request'].GET)

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
            url = get_page_url(curpage, context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)
            page_urls.append((curpage, url))

        first_page_url = None
        if current_page >= 1:
            first_page_url = get_page_url(1, context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        last_page_url = None
        if current_page <= page_count:
            last_page_url = get_page_url(page_count, context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        previous_page_url = None
        if page.has_previous():
            previous_page_url = get_page_url(page.previous_page_number(), context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        next_page_url = None
        if page.has_next():
            next_page_url = get_page_url(page.next_page_number(), context.current_app, url_view_name, url_extra_args, url_extra_kwargs, url_param_name, url_get_params)

        return get_template("bootstrap_pagination/pagination.html").render(
            Context({
                'page': page,
                'size': size,
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
                'next_page_url': next_page_url
            }, autoescape=False))


@register.tag
def bootstrap_paginate(parser, token):
    """
    Renders a Page object as a Twitter Bootstrap styled pagination bar.
    Compatible with Bootstrap 3.x only.

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

        url_name - The named URL to use. Defaults to None. If None, then the
                   default template simply appends the url parameter as a
                   relative URL link, eg: <a href="?page=1">1</a>

        url_param_name - The name of the parameter to use in the URL. If
                         url_name is set to None, this string is used as the
                         parameter name in the relative URL path. If a URL
                         name is specified, this string is used as the
                         parameter name passed into the reverse() method for
                         the URL.

        url_extra_args - This is used only in conjunction with url_name.
                        When referencing a URL, additional arguments may be
                        passed in as a list.

        url_extra_kwargs - This is used only in conjunction with url_name.
                           When referencing a URL, additional named arguments
                           may be passed in as a dictionary.

        url_get_params - The other get parameters to pass, only the page
                         number will be overwritten. Use this to preserve
                         filters.


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
    Compatible with Bootstrap 2.x only.

    Example::

        {% bootstrap_pager page_obj %}


    Named Parameters::


        previous_label - The label to show for the Previous link (defaults to "Previous Page")

        next_label - The label to show for the Next link (defualts to "Next Page")

        previous_title - The link title for the previous link (defaults to "Previous Page")

        next_title - The link title for the next link (defaults to "Next Page")

        url_name - The named URL to use. Defaults to None. If None, then the
                   default template simply appends the url parameter as a
                   relative URL link, eg: <a href="?page=1">1</a>

        url_param_name - The name of the parameter to use in the URL. If
                         url_name is set to None, this string is used as the
                         parameter name in the relative URL path. If a URL
                         name is specified, this string is used as the
                         parameter name passed into the reverse() method for
                         the URL.

        url_extra_args - This is used only in conjunction with url_name.
                        When referencing a URL, additional arguments may be
                        passed in as a list.

        url_extra_kwargs - This is used only in conjunction with url_name.
                           When referencing a URL, additional named arguments
                           may be passed in as a dictionary.

        url_get_params - The other get parameters to pass, only the page
                         number will be overwritten. Use this to preserve
                         filters.
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
