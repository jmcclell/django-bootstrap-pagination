===========================
Django Bootstrap Pagination
===========================


This application serves to make using Twitter's Bootstrap Pagination styles
work seamlessly with Django Page objects. By passing in a Page object and
one or more optional arguments, Bootstrap pagination bars and pagers can
be rendered with very little effort.

Compatible with Django 1.3+

------------
Installation
------------

**PIP**

  pip install django-bootstrap-pagination

**Download**

Download the latest stable distribution from:

http://pypi.python.org/pypi/django-bootstrap-pagination

Download the latest development version from:

github @ http://www.github.com/jmcclell/django-bootstrap-pagination


  setup.py install

-----
Usage
-----

**Setup**

Make sure you include bootstrap-pagination in your installed_apps list in settings.py:


  INSTALLED_APPS = (
      'bootstrap-pagination',
  )


Additionally, include the following snippet at the top of any template that makes use of
the pagination tags:

  {% load bootstrap_pagination %}

==================
bootstrap_paginate
==================

**All Optional Arguments**

range
  Defines the maximum number of page links to show

show_prev_next
  Boolean. Defines whether or not to show the Previous and Next links. (Accepts "true" or "false")

previous_label
  The label to use for the Previous link

next_label
  The label to use for the Next link

show_first_last
  Boolean. Defines whether or not to show the First and Last links. (Accepts "true" or "false")

first_label
  The label to use for the First page link

last_label
  The label to use for the Last page link

alignment
  How to align the pagination bar. Defaults to "center". (Accepts "left", "center", and "right")

url_view_name
  A named URL reference (such as one that might get passed inti the URL template tag) to use as
  the URL template. Must be resolvable by the reverse() function. **If this option is not
  specified, the tag simply uses a relative url such as "?page=1" which is fine in most
  situations**

url_param_name
  Determines the name of the GET parameter for the page number. The default is "page". If no 
  **url_view_name** is defined, this string is appended to the url as "?{{url_param_name}}=1".
  
url_extra_args
  **Only valid when url_view_name is set.**
  Additional arguments to pass into reverse() to resolve the URL.

url_extra_kwargs
  **Only valid when url_view_name is set.**
  Additional named arguments to pass into reverse() to resolve the URL. Additionally,the
  template tag will add an extra parameter to this for the page, as it is assumed that if
  given a url_name, the page will be a named variable in the URL regular expression. In
  this case, the **url_param_name** continues to be the string used to represent the name.
  That is, by default, **url_param_name** is equal to "page" and thus it is expected that
  there is a named "page" argument in the URL referenced by **url_view_name**. This allows
  us to use pretty pagination URLs such as "/page/1"

**Basic Usage**

The following will show a pagination bar with a link to every page, a previous link, and a next link:

  {% bootstrap_paginate page_obj %}

The following will show a pagination bar with at most 10 page links, a previous link, and a next link:

  {% bootstrap_paginate page_obj range=10 %}

The following will show a pagination bar with at most 10 page links, a first page link, and a last page link:

  {% bootstrap_paginate page_obj range=10 show_prev_next="false" show_first_last="true" %}

**Advanced Usage**

Given a url configured such as:

  archive_index_view = ArchiveIndexView.as_view(
      date_field='date',
      paginate_by=10,            
      allow_empty=True,
      queryset=MyModel.all(),
      template_name='example/archive.html'    
  )
    
  urlpatterns = patterns(
      'example.views',
       url(r'^$', archive_index_view, name='archive_index'),
       url(r'^page/(?P<page>\d+)/$', archive_index_view,
       name='archive_index_paginated'))


We could simply use the basic usage (appending ?page=#) with the *archive_index* URL above,
as the *archive_index_view* class based generic view from django doesn't care how it gets
the page parameter. However, if we want pretty URLs, such as those defined in the
*archive_index_paginated* URL (ie: /page/1), we need to define the URL in our template tag:


  {% bootstrap_paginate page_obj url_view_name="archive_index_paginated" %}

Because we are using a default page parameter name of "page" and our URL requires no other
parameters, everything works as expected. If our URL required additional parameters, we
would pass them in using the optional arguments **url_extra_args** and **url_extra_kwargs**.
Likewise, if our page parameter had a different name, we would pass in a different
**url_param_name** argument to the template tag.

===============
bootstrap_pager
===============

A much simpler implementation of the Bootstrap Pagination functionality is the Pager, which
simply provides a Previous and Next link.

**All Optional Arguments**

previous_label
  Defines the label for the Previous link

next_label
  Defines the label for the Next link

previous_title
  Defines the link title for the previous link

next_title
  Defines the link title for the next link

centered
  Boolean. Defines whether or not the links are centered. Defaults to false.
  (Accepts "true" or "false")
  
url_view_name
  A named URL reference (such as one that might get passed inti the URL template tag) to use as
  the URL template. Must be resolvable by the reverse() function. **If this option is not
  specified, the tag simply uses a relative url such as "?page=1" which is fine in most
  situations**

url_param_name
  Determines the name of the GET parameter for the page number. The default is "page". If no 
  **url_view_name** is defined, this string is appended to the url as "?{{url_param_name}}=1".
  
url_extra_args
  **Only valid when url_view_name is set.**
  Additional arguments to pass into reverse() to resolve the URL.

url_extra_kwargs
  **Only valid when url_view_name is set.**
  Additional named arguments to pass into reverse() to resolve the URL. Additionally,the
  template tag will add an extra parameter to this for the page, as it is assumed that if
  given a url_name, the page will be a named variable in the URL regular expression. In
  this case, the **url_param_name** continues to be the string used to represent the name.
  That is, by default, **url_param_name** is equal to "page" and thus it is expected that
  there is a named "page" argument in the URL referenced by **url_view_name**. This allows
  us to use pretty pagination URLs such as "/page/1"


**Usage**

Usage is basically the same as for bootstrap_paginate. The simplest usage is:

  {% bootstrap_pager page_obj %}

A somewhat more advanced usage might look like:

  {% bootstrap_pager page_obj previous_label="Newer Posts" next_label="Older Posts" url_view_name="post_archive_paginated" %}
