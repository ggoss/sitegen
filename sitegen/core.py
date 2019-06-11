#!/usr/bin/env python3
# encoding: utf-8

# core.py

from sitegen import *


def create_new_post(slug: str, path: str = './posts/') -> None:
    """Creates a new (blank) blog post, including a YAML block for metadata.

    Metadata fields include:
        post_title: (str) title of post
        post_description: (str) description of post (optional)
        author: (str) set to the default author defined in Params.DEFAULT_AUTHOR.
        date: (datetime) set by default to current date and time
        slug: (str) post slug; by default, also used as filename
        topics: bulleted list of topics the post pertains to (in YAML bulleted-list format)
        related_posts: bulleted list of related posts (by slug)
        render_toc: (bool) if 'True', a table of contents will be generated for the post and shown on the sidebar
        enable_comments: (bool) if 'False', post comments will not be shown

    Note:
        If you need to use a colon, dash, or any other character that might trip up the YAML interpreter, wrap the
        containing metadata field in double quotes. Additionally, while changing the default value for any metadata
        field is permitted, changing the name of a metadata field will cause problems.

    Args:
        slug: will be sanitized to eliminate whitespaces and illegal characters; will be used in URL and post_db to
            represent post, and also as filename (after '.md' is appended)
        path: path in which to create the post
    """
    if not os.path.exists(path):
        os.makedirs(path)

    slug = sanitize_string(slug)

    if os.path.exists(path + slug + '.md'):
        raise FileExistsError(f'{path + filename}.md already exists')

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(path + slug + '.md', 'w+') as file:
        file.writelines(['---\n', 'post_title: \n', 'post_description: \n', f'author: {params.DEFAULT_AUTHOR}\n',
                         f'date: {current_datetime}\n', f'slug: {slug}\n', 'topics: \n', 'related_posts: \n',
                         'render_toc: False\n', 'enable_comments: True\n', '---\n', '\n'])


def read_post_metadata(filename: str, path: str = './posts/') -> dict:
    """Imports the metadata contained within a post (currently, markdown only) given its filename, and returns a dict
    containing the post's metadata.

    Args:
        filename: name of the post file to import
        path: path containing the post file

    Returns:
        dict of the post's metadata
    """
    if not is_markdown(filename):
        raise MarkdownProcessingError('The input file does not have a known markdown extension.')

    with open(path + filename, 'r') as f:
        text = f.read()
        meta = text.split('---', 2)[-2]
        post_meta = yaml.safe_load(meta)

        post_meta['slug'] = sanitize_string(post_meta['slug'].strip().lower())

    return post_meta


def read_post_text(filename: str, path: str = './posts/', output_format: str = 'html') -> str:
    """Imports a post (currently, markdown only) given its filename, optionally converts the post from markdown to html,
    and returns the post as a string.

    NOTE: Metadata contained in the input file is stripped from the returned text.

    Args:
        filename: name of the post file to import
        path: path containing the post file
        output_format: if 'html', converts the post to from md to html

    Returns:
        dict of the post and its metadata
    """
    if not is_markdown(filename):
        raise MarkdownProcessingError('The input file does not have a known markdown extension.')

    with open(path + filename, 'r') as f:
        text = f.read()
        post = text.split('---', 2)[-1]

    if output_format == 'html':
        try:
            post = md_to_html(post)
        except:
            raise MarkdownProcessingError(f'There was an error processing the input file {filename}.')

    return post


def build_post_db(input_dir: str, blog_dir: str, cached_post_db: Optional[Dict[str, dict]] = None) -> Dict[str, dict]:
    """Builds a nested dict of post-data for all markdown-formatted posts in 'input_dir.' The filenames (without
    extensions) of the md-formatted input posts are used as keys in the output dict, and dicts of data about each post
    are used as their corresponding values. These include: in-file specified metadata, text contents, URLs (for use once
    the post is rendered to HTML, constructed in the format '/month/year/slug.html' using their defined metadata), md5
    hashes, and a list of the post's headings (h1 -> h4), which will optionally be used to construct a table of contents
    for each post.

    Args:
        input_dir: directory of input markdown-formatted posts
        blog_dir: desired output base directory of all rendered posts
        cached_post_db: (optional) cached version of post_db

    Returns:
        post database, with {input filenames without extensions} as keys (e.g. the key for input file 'ex.md' would be
            'ex') and dicts of their data as values
    """
    if cached_post_db is not None:
        post_db = deepcopy(cached_post_db)
    else:
        post_db: Dict[str, dict] = {}

    # Read post metadata and text, add to post_db
    for post in os.listdir(input_dir):
        if is_markdown(post):
            try:
                post_db_entry = read_post_metadata(post, input_dir)
                post_db_entry['hash'] = md5_hash(post, input_dir)

                if (cached_post_db is not None) and (post_db_entry['slug'] in cached_post_db.keys()):
                    if post_db[post_db_entry['slug']]['hash'] == post_db_entry['hash']:
                        post_db[post_db_entry['slug']]['date'] = datetime.strptime(post_db[post_db_entry['slug']]['date'],
                                                                                   '%Y-%m-%d %H:%M:%S')
                        continue
                post_db_entry['post_body'] = read_post_text(post, input_dir, output_format='html')

                post_db_entry['toc_list'] = build_toc_list(post_db_entry)
                post_db_entry = add_toc_id_tags(post_db_entry)

                post_db[post_db_entry['slug']] = post_db_entry
            except Exception as e:
                raise PostDatabaseError(post) from e

    # Generate post URLs, add to post_db
    newest_posts = sort_posts(post_db, 'date')
    for i, post in enumerate(newest_posts):
        month = post_db[post]['date'].month
        year = post_db[post]['date'].year
        slug = post_db[post]['slug']
        post_db[post]['url'] = f'/{blog_dir}{year}/{month:02d}/{slug}.html'

    return post_db


def build_topic_dict(post_db: dict, sort_key: str = 'date') -> dict:
    """Returns a dict of topics and all corresponding posts, sorted by either 'date' or 'post_title'

    Args:
        post_db: data for all posts
        sort_key: key by which the posts should be sorted; can be either 'date' or 'post_title'

    Returns:
        dict, topics are keys, lists of posts are values
    """
    valid_keys = ['date', 'post_title']
    if sort_key not in valid_keys:
        raise KeyError(f'Cannot sort by that key. Valid keys: {valid_keys}')

    post_list = sort_posts(post_db, sort_key)
    topic_list = sorted(list(set([topics for post in post_list for topics in post_db[post]['topics']])))

    topic_posts_dict = {topic: [] for topic in topic_list}

    for post in post_list:
        topics = post_db[post]['topics']
        for topic in topics:
            topic_posts_dict[topic].append(post)

    return topic_posts_dict


def build_blog_pagination_dict(post_db: dict, posts_per_page: int = 10) -> dict:
    """Creates a dict of blog page numbers and a list of the names of all posts to display on each page.

    Args:
        post_db: data for all posts
        posts_per_page: posts per page in main blog

    Returns:
        dict, blog page numbers are keys, lists of posts for each page are values
    """
    all_posts = sort_posts(post_db, 'date')
    n_pages = math.ceil(len(all_posts) / posts_per_page)

    paginated_blog = {}
    paginated_blog['all_posts'] = all_posts.copy()
    paginated_blog['n_pages'] = n_pages
    for page_number in range(n_pages + 1)[1:]:
        paginated_blog[page_number] = {}
        paginated_blog[page_number]['posts'] = [all_posts.pop(0) for _ in range(posts_per_page) if len(all_posts) > 0]
        paginated_blog[page_number]['url'] = '/' if (page_number == 1) else f'/{Params.BLOG_PATH}page/{page_number}/'

    return paginated_blog
