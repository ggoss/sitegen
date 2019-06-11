#!/usr/bin/env python3
# encoding: utf-8

# __init__.py

# External Imports
import os
import re
import math
import shutil
import subprocess
import hashlib
import yaml
import json
from copy import copy, deepcopy
from datetime import datetime
from functools import partial
from typing import Dict, Tuple, List, Union, Optional

from PIL import Image

from bs4 import BeautifulSoup
import misaka as m  # in testing, misaka was orders of magnitude faster than python-markdown
import houdini as h
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name

from jinja2 import FileSystemLoader, Environment


# Internal Imports
from .config import Params
from .exceptions import SitegenError, ImageProcessingError, MarkdownProcessingError, ImageTagsError, CheckboxListError, PostDatabaseError
from .utils import sanitize_string, md5_hash, sort_posts, get_newest_posts, is_markdown, make_output_dirs, compress_blog_images, compress_image
from .toc import build_toc_list, build_toc_html, render_sidebar_toc, add_toc_id_tags
from .md_processing import md_to_html, downgrade_md_headings, HighlighterRenderer, add_table_tags, set_table_col_widths, add_blockquote_class, render_checkbox_list, render_image_autoscale, render_image_float_center, render_image_float_left, render_image_float_right, render_image_carousels, make_images_clickable, render_youtube_embeds, youtube_embed_link
from .core import create_new_post, read_post_metadata, read_post_text, build_post_db, build_topic_dict, build_blog_pagination_dict
from .templating import render_from_template, get_topic_url_links, get_month_name, get_pretty_date
from .serve import serve
from .sitemap import generate_sitemap
#from .s3 import sync
