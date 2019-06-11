#!/usr/bin/env python3
# encoding: utf-8

# custom_jinja_filters.py

from sitegen import *


def render_from_template(directory: str, template_name: str, **kwargs: Union[dict, str, list]) -> str:
    """Using Jinja2, fill an HTML template with data from fields defined in the provided dict."""
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    env.filters['get_topic_url_links'] = get_topic_url_links
    env.filters['render_sidebar_toc'] = render_sidebar_toc
    env.filters['get_month_name'] = get_month_name
    env.filters['get_pretty_date'] = get_pretty_date
    env.filters['get_newest_posts'] = get_newest_posts
    template = env.get_template(template_name)

    return template.render(**kwargs)


def get_topic_url_links(topic_names: list) -> list:
    topic_links = []
    for topic_name in topic_names:
        topic_url = f'/{Params.BLOG_PATH}all-topics.html#{topic_name}'
        topic_link = f'<a class="text-muted" href="{topic_url}">{topic_name}</a>'
        topic_links.append(topic_link)
    return topic_links


def get_month_name(date: datetime.date) -> str:
    """Function used within Jinja2 template to get month name from a date of type 'datetime.date'

    Args:
        date: datetime.date object

    Returns:
        str: month name (e.g. 'March')
    """
    month_name = date.strftime('%B')

    return month_name


def get_pretty_date(date: datetime.date) -> str:
    """Function used within Jinja2 template to get a pretty date from a date of type 'datetime.date'

    Args:
        date: datetime.date object

    Returns:
        str: date in format 'Month Day, Year' (e.g. 'March 26, 2019')
    """
    pretty_date = date.strftime('%B %d, %Y')

    return pretty_date
