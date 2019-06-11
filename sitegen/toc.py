#!/usr/bin/env python3
# encoding: utf-8

# toc.py

from sitegen import *


def build_toc_list(post: Dict[str, Union[str, list]]) -> List[Tuple[int, str, str]]:
    """Given a post_db_entry dict as input, returns the TOC headings from h1 -> h4 (post title is the one and only h1)
    as a list of tuples of <heading level (i.e. 1, 2, 3, or 4)>, <heading>, and <anchor>

    Args:
        post: single entry in post_db

    Returns:
        list of TOC entries
    """
    soup_post = BeautifulSoup(post['post_body'], features='html.parser')

    toc_list = [(1, post['post_title'], post['slug'])]

    for i, heading in enumerate(soup_post.find_all(['h2', 'h3', 'h4'])):
        heading_level = heading.name[-1]
        heading_string = heading.string
        heading_anchor = f'{post["slug"]}${sanitize_string(heading.string.lower().strip())}'

        all_anchors = [toc_item[2] for toc_item in toc_list]
        if heading_anchor in all_anchors:
            heading_anchor = f'_{str(i)}'

        toc_list.append((heading_level, heading_string, heading_anchor))

    return toc_list


def build_toc_html(toc_list: List[Tuple[int, str, str]]) -> str:
    """Given a list of tuples of (heading_level, heading, anchor) for a given post, converts it to an html-formatted
    table of contents, returned as a string.

    Args:
        toc_list: list of tuples of (heading_level, heading, anchor) for an individual post

    Returns:
        toc_html: string containing the html-formatted table of contents
    """
    if len(toc_list) > 1:
        toc_md = '### Table of Contents\n'
        for (heading_level, heading_string, heading_anchor) in toc_list[1:]:
            if heading_level == 1:
                raise TocError('Post title should be the only h1 heading.')
            toc_md += f'{(int(heading_level) - 1) * " "}- [{heading_string}](#{heading_anchor})\n'

        converter = m.Markdown(m.HtmlRenderer(), extensions=('math', 'math_explicit', 'no-intra-emphasis', 'strikethrough', 'superscript',))
        toc_html = converter(toc_md)
    else:
        toc_html = ''

    return toc_html


def render_sidebar_toc(toc_list: List[Tuple[int, str, str]]) -> str:
    """Function used within Jinja2 template to output a sidebar table of contents (using the h2 -> h4 headings as TOC
    items), given the toc_list entry for a post in post_db, with the appropriate html-formatting for this blog.

    Args:
        toc_list: list of tuples of (heading_level, heading, anchor) for an individual post

    Returns:
        html-formatted table of contents
    """
    toc_html = build_toc_html(toc_list)
    soup_toc = BeautifulSoup(toc_html, features='html.parser')

    soup_toc.find('h3', string='Table of Contents')['class'] = 'sidebar-header'
    soup_toc.find('ul')['class'] = 'sidebar-list'

    return str(soup_toc)


def add_toc_id_tags(post: Dict[str, Union[str, list]]) -> Dict[str, str]:
    """Returns a modified copy of post, with id html tags for anchor links added to headings in post['post_body'].

    Args:
        post: a single post_db entry

    Returns:
        a copy of 'post' with anchor links added to headings in post['post_body']
    """
    post_copy = copy(post)

    toc_list = post_copy['toc_list'][1:] # exclude the first item (h1), which isn't yet rendered in the html

    soup_post = BeautifulSoup(post_copy['post_body'], features='html.parser')

    for heading in soup_post.find_all(['h2', 'h3', 'h4']):
        heading_level = heading.name[-1]
        heading_string = heading.string
        toc_item = toc_list.pop(0)
        if not ((toc_item[0] == heading_level) and (toc_item[1] == heading_string)):
            raise TocError('There is a mismatch between the toc_list and the post_body used to create it. WHAT DID YOU DO?!')
        heading['id'] = toc_item[2]

    post_copy['post_body'] = str(soup_post)

    return post_copy