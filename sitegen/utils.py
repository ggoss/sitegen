#!/usr/bin/env python3
# encoding: utf-8

# utils.py

from sitegen import *


def sanitize_string(input_string: str) -> str:
    """Removes whitespace before and after a string, replaces spaces with dashes, and removes doublequotes, backslashes,
    and everything else that is not alphanumeric or one of the following: $ + ! * _ -

    Args:
        input_string:

    Returns:

    """
    string = copy(input_string)

    unsafe_characters = re.compile(r'[^A-Za-z0-9$+!*_-]')
    string = re.sub(unsafe_characters, '', string.strip().replace('"', '').replace('\'', '').replace(' ', '-'))

    return string


def md5_hash(filename: str, path: str) -> str:
    """Calculates the md5 hash of an input file.

    Args:
        filename: name of input file
        path: path of input file

    Returns:
        str containing 128-bit md5-hash
    """
    with open(path + filename, 'rb') as f:
        bytes = f.read()
        hash_str = hashlib.md5(bytes).hexdigest()

    return hash_str


def sort_posts(post_db: dict, sort_key: str) -> list:
    """Return a sorted list of posts, given a dict of data for all posts.

    Args:
        post_db: data for all posts
        sort_key: key by which the posts should be sorted; can be either 'date' or 'post_title'

    Returns:
        list of sorted posts
    """
    valid_keys = ['date', 'post_title']
    assert sort_key in valid_keys, 'Cannot sort by that key. '
    reverse = True if (sort_key == 'date') else False

    post_list = post_db.keys()
    sorted_posts = sorted(post_list, key=lambda post: str(post_db[post][sort_key]), reverse=reverse)

    return sorted_posts


def get_newest_posts(post_db: dict, number: int = None, topic_name: Optional[str] = None) -> list:
    """Return a list of the most recent posts in a given topic (or in all topics).

    Args:
        post_db: data for all posts
        number: number of recent posts to list ('None' by default, to list all posts)
        topic_name: if 'None', will list posts from all topics; if a specific 'topic_name' is given, will list only the
            most recent posts from that topic

    Returns:
        list of newest posts
    """
    newest_posts = sort_posts(post_db, 'date')

    if topic_name is None:
        return newest_posts[:number]
    else:
        return [post for post in newest_posts if topic_name in post_db[post]['topics']][:number]


def is_markdown(filename: str) -> bool:
    """Checks whether a given file has a known markdown extension.

    Args:
        filename: name of file to check

    Returns:
        bool
    """
    markdown_extensions = ['md', 'mkd', 'markdown', 'mdown', 'mkdn', 'txt']

    if filename.split('.')[-1] in markdown_extensions:
        return True
    else:
        return False


def make_output_dirs(post_db: dict, pagination_dict: dict, output_dir: str = './') -> None:
    """Creates the directory structure needed to save all posts in post_db, if the necessary directories do not already
    exist.

    Args:
        post_db: data for all posts
        pagination_dict: pagination data for blog
        output_dir: directory to which all generated pages will be saved; everything here will be moved into the site's
            base directory
    """
    dirs = list(set([os.path.dirname(post['url']) for post in post_db.values()]))
    try:
        for dir in dirs:
            os.makedirs(output_dir + dir)
    except:
        raise FileExistsError

    page_dirs = list(set([os.path.dirname(pagination_dict[page]['url']) for page in pagination_dict.keys() if type(page) is int]))

    for page_dir in page_dirs:
        try:
            os.makedirs(output_dir + page_dir)
        except:
            continue


def compress_blog_images(soup_body: object, max_width: int = Params.MAX_IMAGE_WIDTH, posts_dir: str = Params.POSTS_PATH, output_dir: str = Params.OUTPUT_PATH, blog_image_dir: str = Params.BLOG_IMAGE_PATH) -> object:
    """For each image in the input bs4 object, locates the file, compresses it, moves it to the output dir, and changes
    its url to reflect this change. If image filename ends with 'large,' compress but do not scale.

    Args:
        soup_body: bs4 object input
        posts_dir: directory containing input posts with links to images
        output_dir: directory to which blog is written
        blog_image_dir: blog image directory

    Returns:
        modified bs4 object
    """
    assert isinstance(soup_body, BeautifulSoup), 'Input must be a bs4.BeautifulSoup object'

    for img in soup_body.find_all('img'):
        # retrieves path of input image from post
        input_image = img['src']
        # compresses image and returns the relative path
        max_width = None if input_image.split('.')[-2][-5:] == 'large' else max_width
        compressed_image = compress_image(posts_dir + input_image, output_dir + blog_image_dir, max_width)
        # removes output_dir from the path to make it suitable for use as a url and replaces the url
        img['src'] = '/' + compressed_image.replace(output_dir, '')

    return soup_body


def compress_image(input_image: str, output_dir: str, max_width: Optional[int] = None) -> str:
    """Scales and compresses an image. If compressed image already exists in output_dir, returns the output file path
    but does not recompress the image.

    Args:
        input_image: input file path
        output_dir: directory to which processed image should be saved
        max_width: if image is wider than max_width, it will be scaled to this width;
            if None, compress, but do not scale

    Returns:
        output file path
    """
    assert type(input_image) is str, 'Input must be a string.'
    assert (output_dir[-1] == '/')

    def _resize_im(image, maximum_width):
        if (maximum_width is not None) and (image.width > maximum_width):
            image = image.resize((maximum_width, int((maximum_width / image.width) * image.height)), Image.LANCZOS)
        return image

    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)

    filename, ext = os.path.basename(input_image).split('.')

    if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff']:
        with Image.open(input_image) as im:
            if im.format is 'JPEG':
                output_image = f'{output_dir}{filename}_c.jpg'
                if os.path.exists(output_image) is False:
                    im = _resize_im(im, max_width)
                    im.save(output_image, 'JPEG', optimize=True, quality=75, progressive=True)
            elif im.format is 'PNG':
                output_image = f'{output_dir}{filename}_c.png'
                if os.path.exists(output_image) is False:
                    im = _resize_im(im, max_width)
                    im.save(output_image, 'PNG', optimize=True)
            elif im.format is 'GIF':
                output_image = f'{output_dir}{filename}_c.gif'
                if os.path.exists(output_image) is False:
                    im = _resize_im(im, max_width)
                    im.save(output_image, 'GIF', save_all=True, optimize=True, loop=0)
            elif im.format is 'TIFF':
                output_image = f'{output_dir}{filename}_c.jpg'
                if os.path.exists(output_image) is False:
                    im = _resize_im(im, max_width)
                    im.save(output_image, 'JPEG', optimize=True, quality=75, progressive=True)
            else:
                print(f'Input image "{input_image}" is not a recognized {ext} image. Moving to output without compressing or scaling.')
                output_image = f'{output_dir}{filename}{ext}'
                if os.path.exists(output_image) is False:
                    shutil.move(input_image, output_image)
    elif ext.lower() == 'svg':
        output_image = f'{output_dir}{filename}_c.svg'
        if os.path.exists(output_image) is False:
            subprocess.run(f'./svgcleaner/svgcleaner {input_image} {output_image}', shell=True)
    else:
        output_image = f'{output_dir}{filename}{ext}'
        if os.path.exists(output_image) is False:
            shutil.move(input_image, output_image)

    return output_image
