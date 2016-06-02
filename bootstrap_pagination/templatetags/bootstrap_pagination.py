import django
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template import Node, Library, TemplateSyntaxError
from django.template.loader import get_template
from django.conf import settings
from django.http import QueryDict
from django.utils.html import mark_safe


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


class ArgumentResolver():

    def __init__(self, context, kwargs):
        self.context = context
        self.kwargs = kwargs
        self.resolved = {}

    def get(self, arg_name, default=None):
        try:
            return self.resolved[arg_name]
        except KeyError:
            pass  # not yet resolved

        try:
            value = self.kwargs[arg_name]
        except KeyError:
            return default

        try:
            resolve_fn = value.resolve
        except AttributeError:
            result = value
        else:
            result = resolve_fn(self.context)

        # Note: deliberately not catching VariableDoesNotExist - let that
        # bubble up though the templateing system for most debuggable errors

        self.resolved[arg_name] = result
        return result

    def get_bool(self, arg_name, default):
        return self.get(arg_name, default) in ["true", "yes", "on", "1", True]

    def get_html(self, arg_name, default):
        return mark_safe(self.get(arg_name, default))

    def page_url(self, page_num):
        """
        Helper function to return a valid URL string given the template tag parameters
        """
        request = (getattr(self.context, "request", None) or
                   self.context.get("request"))

        # Resolve the GET parameters
        get_params = self.get("url_get_params", "")
        param_name = str(self.get("url_param_name", "page"))

        if not get_params and request:
            get_params = request.GET.copy()

        # Make sure the get_params are a mutable querydict.
        if isinstance(get_params, QueryDict):
            get_params = get_params.copy()
        elif isinstance(get_params, dict):
            new_get_params = QueryDict("", mutable=True)
            new_get_params.update(get_params)
            get_params = new_get_params
        else:
            get_params = QueryDict(get_params, mutable=True)

        view_name = self.get("url_view_name")
        if view_name:
            extra_args = self.get("url_extra_args", [])
            extra_kwargs = self.get("url_extra_kwargs", {})

            # Add page param to the kwargs list. Overrides any previously set
            # parameter of the same name.
            extra_kwargs[param_name] = page_num

            # Resolve current app. Over the time, current_app has moved around
            # a bit
            current_app = None
            if request and django.VERSION >= (1, 8, 0):
                current_app = getattr(request, "current_app", None)
            elif django.VERSION < (1, 10, 0):
                current_app = getattr(self.context, "current_app", None)

            # This bit of code comes from the default django url tag
            try:
                url = reverse(str(view_name), args=extra_args,
                              kwargs=extra_kwargs,
                              current_app=current_app)
            except NoReverseMatch as e:
                if settings.SETTINGS_MODULE:
                    project_name = settings.SETTINGS_MODULE.split('.')[0]
                    url = reverse('%s.%s' % (project_name, view_name),
                                  args=extra_args,
                                  kwargs=extra_kwargs,
                                  current_app=current_app)
                else:
                    raise e

        else:
            # No view defined. Use the GET arguments instead
            get_params[param_name] = page_num
            url = ''

        if get_params:
            url += '?' + get_params.urlencode()

        anchor = self.get("url_anchor", None)
        if anchor:
            url += '#' + anchor

        return url


class BootstrapPagerNode(Node):
    def __init__(self, page, kwargs):
        self.page = page
        self.kwargs = kwargs

    def render(self, context):
        page = self.page.resolve(context)
        args = ArgumentResolver(context, self.kwargs)

        previous_label = args.get_html("previous_label", "Previous Page")
        next_label = args.get_html("next_label", "Next Page")
        previous_title = args.get_html("previous_title", "Previous Page")
        next_title = args.get_html("next_title", "Next Page")

        previous_page_url = None
        if page.has_previous():
            previous_page_url = args.page_url(page.previous_page_number())

        next_page_url = None
        if page.has_next():
            previous_page_url = args.page_url(page.next_page_number())

        return get_template("bootstrap_pagination/pager.html").render(
            Context({
                'page': page,
                'previous_label': previous_label,
                'next_label': next_label,
                'previous_title': previous_title,
                'next_title': next_title,
                'previous_page_url': previous_page_url,
                'next_page_url': next_page_url
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
        args = ArgumentResolver(context, self.kwargs)

        # Unpack our keyword arguments, substituting defaults where necessary
        range_length = args.get("range", None)
        if range_length is not None:
            range_length = int(range_length)

        size = args.get("size", None)
        if size is not None:
            size = str(size.lower())
            if size not in ["small", "large"]:
                raise Exception("Optional argument \"size\" expecting one "
                                "of \"small\", or \"large\"")

        previous_label = args.get_html("previous_label", "&larr;")
        next_label = args.get_html("next_label", "&rarr;")
        first_label = args.get_html("first_label", "&laquo;")
        last_label = args.get_html("last_label", "&raquo;")

        show_prev_next = args.get_bool("show_prev_next", "true")
        show_first_last = args.get_bool("show_first_last", "false")
        show_index_range = args.get_bool("show_index_range", "false")

        # Generage our viewable page range
        page_count = page.paginator.num_pages
        current_page = page.number

        if range_length is None:
            range_min = 1
            range_max = page_count
        else:
            if range_length < 1:
                raise Exception("Optional argument \"range\" expecting "
                                "integer greater than 0")
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

        # Generate our URLs (page range + special urls for first, previous,
        # next, and last)
        page_urls = []
        for curpage in page_range:
            first_index = (curpage - 1) * page.paginator.per_page + 1
            last_index = curpage * page.paginator.per_page

            if curpage == page.paginator.num_pages and show_index_range:
                last_index = len(page.paginator.object_list)

            index_range = "%s-%s" % (first_index, last_index)

            url = args.page_url(curpage)
            page_urls.append((curpage, index_range, url))

        first_page_url = args.page_url(1) if current_page >= 1 else None
        last_page_url = (args.page_url(page_count)
                         if current_page <= page_count else None)

        previous_page_url = (args.page_url(page.previous_page_number())
                             if page.has_previous() else None)
        next_page_url = (args.page_url(page.next_page_number())
                         if page.has_next() else None)

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
                'next_page_url': next_page_url
            }))


def parse_tag(parser, token, tag):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (Page object reference)" % bits[0])

    page = parser.compile_filter(bits[1])
    kwargs = {}
    for argument in bits[2:]:
        try:
            name, value = argument.split('=', 1)
        except ValueError:  # no = separator
            raise TemplateSyntaxError("Malformed argument to %s tag" % tag)

        kwargs[name] = parser.compile_filter(value)

    return page, kwargs


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

        url_anchor - The anchor to use in URLs. Defaults to None.
    """
    page, kwargs = parse_tag(parser, token, "bootstrap_paginate")
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

        url_anchor - The anchor to use in URLs. Defaults to None.
    """
    page, kwargs = parse_tag(parser, token, "bootstrap_pager")
    return BootstrapPagerNode(page, kwargs)
