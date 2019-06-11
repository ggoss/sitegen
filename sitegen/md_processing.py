#!/usr/bin/env python3
# encoding: utf-8

# custom_tags.py

from sitegen import *


def md_to_html(text: str) -> str:
    """Renders html-formatted text from markdown-formatted text.

    Args:
        text: markdown-formatted text

    Returns:
        html-formatted text
    """
    # modify text in md files before converting to html
    # headings are downgraded by one (e.g. h1 -> h2), so that the post title is always the only h1 heading for each post
    text = downgrade_md_headings(text)

    # convert md-formatted text to html
    renderer = HighlighterRenderer()
    converter = m.Markdown(renderer, extensions=('fenced-code', 'math', 'math_explicit', 'no-intra-emphasis', 'quote', 'strikethrough', 'superscript', 'tables', 'underline', 'hard-wrap',))  # removed 'autolink'
    html = converter(text)

    # create bs4 object from html for additional processing
    soup = BeautifulSoup(html, features='html.parser')

    # modify html (within bs4 object)
    soup = add_table_tags(soup)
    soup = set_table_col_widths(soup)
    soup = add_blockquote_class(soup)
    try:
        soup = render_checkbox_list(soup)
    except Exception as e:
        raise CheckboxListError from e
    try:
        soup = compress_blog_images(soup)
    except Exception as e:
        raise ImageProcessingError from e
    try:
        soup = render_image_float_center(soup)
        soup = render_image_float_left(soup)
        soup = render_image_float_right(soup)
        soup = render_image_carousels(soup)
        #soup = make_images_clickable(soup)
    except Exception as e:
        raise ImageTagsError from e
    soup = render_youtube_embeds(soup)

    # convert back to html
    html = str(soup)

    return html


def downgrade_md_headings(text: str) -> str:
    """Downgrades all headings in a markdown-formatted input text to the next heading level (e.g. # to ##).

    Args:
        text: markdown-formatted text

    Returns:
        markdown-formatted text
     """
    return text.replace('\n#', '\n##')


class HighlighterRenderer(m.HtmlRenderer):
    """Subclass of misaka HtmlRenderer to include syntax highlighting functionality"""
    def blockcode(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = None

        if lexer:
            formatter = HtmlFormatter()
            return highlight(text, lexer, formatter)

        # default
        return f'\n<pre><code>{h.escape_html(text.strip())}</code></pre>\n'


def add_table_tags(soup_body: object) -> object:
    """For each table in the input bs4 object, change the class to 'table table-sm table-hover' for bootstrap formatting.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for table in soup_body.find_all('table'):
        table['class'] = 'table table-striped table-sm table-hover'
    return soup_body


def set_table_col_widths(soup_body: object) -> object:
    """For each table in the input bs4 object, apply column widths if specified within the header row (e.g. by adding
    <3em> to the end of the contents of a cell of the header row, that column will be set to have a width of 3em).

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for table in soup_body.find_all('table'):
        for th in table.find_all('th'):
            match = re.search(r'(?<=<).+(?=>)', th.string)
            if match is not None:
                if th.has_attr('style'):
                    th['style'] = f'{th["style"]}; width:{match[0]}'
                else:
                    th['style'] = f'width:{match[0]};'
                th.string = re.sub(r'<[A-Za-z0-9%]+>', '', th.string).strip()

    return soup_body


def add_blockquote_class(soup_body: object) -> object:
    """For each blockquote in the input bs4 object, change the class to 'blockquote text-muted' so that the bootstrap
    framework blockquote styling will be applied.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for bq in soup_body.find_all('blockquote'):
        bq['class'] = 'blockquote'

        for p in bq.find_all('p'):
            for dash in ['-- ', '--- ', '– ', '— ', '&ndash; ', '&mdash; ']:
                if p.string[:len(dash)] == dash:
                    bqf = soup_body.new_tag('footer')
                    bqf['class'] = 'blockquote-footer'
                    bqf.string = p.string.replace(dash, '')
                    p.replace_with(bqf)

    return soup_body


def render_checkbox_list(soup_body: object) -> object:
    """As the chosen markdown processor does not support task lists (lists with checkboxes), this function post-processes
    a bs4 object created from outputted HTML, replacing instances of '[ ]' (or '[]') at the beginning of a list item
    with an unchecked box, and instances of '[x]' (or '[X]') at the beginning of a list item with a checked box.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for ul in soup_body.find_all('ul'):
        for li in ul.find_all('li', recursive=False):

            if (li.contents[0].string[:2] == '[]') or (li.contents[0].string[:3] == '[ ]'):
                unchecked = soup_body.new_tag("input", disabled="", type="checkbox")
                li.contents[0].string.replace_with(li.contents[0].string.replace('[] ', u'\u2002'))
                li.contents[0].string.replace_with(li.contents[0].string.replace('[ ] ', u'\u2002'))
                li.contents[0].insert_before(unchecked)
                li.find_parent('ul')['style'] = 'list-style-type: none; padding-left: 0.5em; margin-left: 0.25em;'

            elif (li.contents[0].string[:3] == '[x]') or (li.contents[0].string[:3] == '[X]'):
                checked = soup_body.new_tag("input", disabled="", checked="", type="checkbox")
                li.contents[0].string.replace_with(li.contents[0].string.replace('[x] ', u'\u2002'))
                li.contents[0].string.replace_with(li.contents[0].string.replace('[X] ', u'\u2002'))
                li.contents[0].insert_before(checked)
                li.find_parent('ul')['style'] = 'list-style-type: none; padding-left: 0.5em; margin-left: 0.25em;'

    return soup_body


def render_image_autoscale(soup_body: object) -> object:
    """Makes the size of all images tagged with <autoscale> tags fluid, autoscaling their width to the container width.
    NOTE: this is now just a wrapper for render_image_float_center()

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    # assert isinstance(soup_body, BeautifulSoup), 'Input must be a bs4.BeautifulSoup object'
    #
    # for autoscale in soup_body.find_all('autoscale'):
    #     img_src = autoscale.img['src']
    #
    #     autoscale_html = f'<img class="img-fluid mx-auto mb-4 d-block" src={img_src}>\n'
    #     autoscale.replace_with(BeautifulSoup(autoscale_html, features="html.parser"))
    #
    # return soup_body

    return render_image_float_center(soup_body)


def render_image_float_center(soup_body: object) -> object:
    """Makes the size of all images tagged with <float-center> or <autoscale> tags fluid, centering them and autoscaling
    their width to the container width by default. If the 'width' is provided in the tag
    (e.g. <float-center width="90%">), the image will be scaled accordingly (e.g. by %, em, rem, px, ...); likewise for
    'height'. If only 'height' or 'width' is provided, the other will be set to 'auto' to maintain the aspect ratio; if
    both are provided, the ratio may be altered. If a 'caption' if defined in the tag, the image will be placed within a
    <figure>, with the caption centered below (and scaled like the image; if the image width is set to 50%, then so will
    the caption's container width).

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    try:
        for float_center in soup_body.find_all(['float-center', 'autoscale']):
            img_src = float_center.img['src']

            if float_center.has_attr('width'):
                img_width = float_center['width']
            else:
                img_width = 'auto'

            if float_center.has_attr('height'):
                img_height = float_center['height']
            else:
                img_height = 'auto'

            if float_center.has_attr('caption'):
                img_caption = str(float_center['caption'])
                float_center_html = f'<figure class="figure" style="width:100%;">\n<img class="figure-img img-fluid mx-auto mb-4 d-block" height={img_height} width={img_width} src={img_src}>\n<figcaption class="figure-caption text-center m-auto" width:{img_width};">{img_caption}</figcaption>\n</figure>\n'
            else:
                float_center_html = f'<img class="img-fluid mx-auto mb-4 d-block" height={img_height} width={img_width} src={img_src}>\n'

            float_center.replace_with(BeautifulSoup(float_center_html, features="html.parser"))
    except:
        print(f'It looks like there might be an issue with the float-center closing tag for "{img_src}". Check the input markdown file.')
        raise

    return soup_body


def render_image_float_right(soup_body: object) -> object:
    """Makes the size of all images tagged with <float-right> tags fluid, aligning them to the right edge of their
    container and setting their 'width' to that provided in the tag (e.g. <float-right width="50%">); likewise for
    'height'. If only 'height' or 'width' is provided, the other will be set to 'auto' to maintain the aspect ratio; if
    both are provided, the ratio may be altered. Body text will automatically be wrapped around the image, so reasonable
    default margins are set. If a 'caption' if defined in the tag, the image will be placed within a <figure>, with the
    caption centered below (and scaled like the image; if the image width is set to 50%, then so will the caption's
    container width).

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    try:
        for float_right in soup_body.find_all('float-right'):
            img_src = float_right.img['src']

            if float_right.has_attr('width'):
                img_width = float_right['width']
            else:
                img_width = 'auto'

            if float_right.has_attr('height'):
                img_height = float_right['height']
            else:
                img_height = 'auto'

            if float_right.has_attr('caption'):
                img_caption = str(float_right['caption'])
                float_right_html = f'<figure class="figure float-right ml-3 mb-4" style="width:{img_width}; height:{img_height};">\n<img class="figure-img img-fluid m-auto d-block" src={img_src}>\n<figcaption class="figure-caption text-center m-auto" width:{img_width};>{img_caption}</figcaption>\n</figure>\n'
            else:
                float_right_html = f'<img class="float-right ml-3 mb-4" height={img_height} width={img_width} src={img_src}>\n'

            float_right.replace_with(BeautifulSoup(float_right_html, features="html.parser"))
    except:
        print(f'It looks like there might be an issue with the float-right closing tag for "{img_src}". Check the input markdown file.')
        raise

    return soup_body


def render_image_float_left(soup_body: object) -> object:
    """Makes the size of all images tagged with <float-left> tags fluid, aligning them to the left edge of their
    container and setting their 'width' to that provided in the tag (e.g. <float-left width="50%">); likewise for
    'height'. If only 'height' or 'width' is provided, the other will be set to 'auto' to maintain the aspect ratio; if
    both are provided, the ratio may be altered. Body text will automatically be wrapped around the image, so reasonable
    default margins are set. If a 'caption' if defined in the tag, the image will be placed within a <figure>, with the
    caption centered below (and scaled like the image; if the image width is set to 50%, then so will the caption's
    container width).

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    try:
        for float_left in soup_body.find_all('float-left'):
            img_src = float_left.img['src']

            if float_left.has_attr('width'):
                img_width = float_left['width']
            else:
                img_width = 'auto'

            if float_left.has_attr('height'):
                img_height = float_left['height']
            else:
                img_height = 'auto'

            if float_left.has_attr('caption'):
                img_caption = str(float_left['caption'])
                float_left_html = f'<figure class="figure float-left mr-3 mb-4" style="width:{img_width}; height:{img_height};">\n<img class="figure-img img-fluid m-auto d-block" src={img_src}>\n<figcaption class="figure-caption text-center m-auto" width:{img_width};>{img_caption}</figcaption>\n</figure>\n'
            else:
                float_left_html = f'<img class="float-left mr-3 mb-4" height={img_height} width={img_width} src={img_src}>\n'

            float_left.replace_with(BeautifulSoup(float_left_html, features="html.parser"))
    except:
        print(f'It looks like there might be an issue with the float-left closing tag for "{img_src}". Check the input markdown file.')
        raise

    return soup_body


def render_image_carousels(soup_body: object) -> object:
    """For each group of images in the input bs4 object of a md-formatted text file placed within <carousel> tags,
    creates a bootstrap4 image carousel in its place.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for carousel in soup_body.find_all('carousel'):

        # Refer to the carousel by the name of the first image contained within it
        carousel_id = carousel.find('img')['src'].split('/')[-1].split('.')[0]

        if carousel.has_attr('width'):
            carousel_width = str(carousel['width'])
        else:
            carousel_width = 'auto'

        carousel_html = []
        carousel_indicators = []

        for img_num, img in enumerate(carousel.find_all('img')):
            img_src = img['src']

            if img_num is 0:
                carousel_html = f'<div class="carousel slide mx-auto mb-4" data-ride="carousel" data-interval="false" data-pause="false" id="carousel-{carousel_id}" style="width:100%;">\n<div class="carousel-inner" role="listbox">\n<div class="carousel-item active"><img class="img-fluid mx-auto mb-4 d-block" src="{img_src}" width={carousel_width} /></div>\n'
                carousel_indicators = f'<ol class="carousel-indicators">\n<li data-target="#carousel-{carousel_id}" data-slide-to="{img_num}" class="active"></li>\n'
            else:
                carousel_html += f'<div class="carousel-item"><img class="img-fluid d-block mx-auto mb-4" src="{img_src}" width={carousel_width} /></div>\n'
                carousel_indicators += f'<li data-target="#carousel-{carousel_id}" data-slide-to="{img_num}"></li>\n'

        carousel_html += f'</div>\n<a href="#carousel-{carousel_id}" role="button" data-slide="prev" class="carousel-control-prev"><span aria-hidden="true" class="carousel-control-prev-icon"></span><span class="sr-only">Previous</span></a>\n<a href="#carousel-{carousel_id}" role="button" data-slide="next" class="carousel-control-next"><span aria-hidden="true" class="carousel-control-next-icon"></span><span class="sr-only">Next</span></a>\n'
        carousel_indicators += f'</ol>\n</div>'

        carousel_html += carousel_indicators

        carousel.replace_with(BeautifulSoup(carousel_html, features="html.parser"))

    return soup_body


def make_images_clickable(soup_body: object) -> object: # Not used.
    """Make each image in the input clickable.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for img in soup_body.find_all('img'):
        img.wrap(soup_body.new_tag('a', href=f"{img['src']}"))
        img.parent['target'] = "_blank"

    return soup_body


def render_youtube_embeds(soup_body: object) -> object:
    """Provides a simple way to embed youtube videos and make them responsive, using only the link to the youtube video.

    Args:
        soup_body: bs4 object input

    Returns:
        modified bs4 object
    """
    if not isinstance(soup_body, BeautifulSoup):
        raise TypeError('Input must be a bs4.BeautifulSoup object')

    for youtube_embed in soup_body.find_all('youtube-embed'):
        yt_src = youtube_embed_link(youtube_embed.a['href'])

        if youtube_embed.has_attr('ratio'):
            ratio = str(youtube_embed['ratio'])
        else:
            ratio = '16by9'

        if ratio not in ['16by9', '4by3', '1by1', '21by9']:
            ratio = '16by9'

        youtube_embed_html = f'<div class="embed-responsive embed-responsive-{ratio}">\n<iframe class="embed-responsive-item" src="{yt_src}" allowfullscreen>\n</iframe>\n'
        youtube_embed.replace_with(BeautifulSoup(youtube_embed_html, features="html.parser"))

    return soup_body


def youtube_embed_link(link: str) -> str:
    """Returns a Youtube embed link given an ordinary Youtube link.

    Args:
        link:

    Returns:

    """
    yt_link_normal = re.search(r'(?<=youtube.com/watch\?v=)[\w-]+(?=\W)*', link)
    yt_link_embed = re.search(r'(?<=youtube.com/embed/)[\w-]+(?=\W)*', link)

    if yt_link_embed is not None:
        return link.replace('youtube.com','youtube-nocookie.com')
    elif yt_link_normal is not None:
        return f'https://www.youtube-nocookie.com/embed/{yt_link_normal.group()}'
    else:
        raise YoutubeEmbedError
