#!/usr/bin/env python3
# encoding: utf-8

# config.py

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    POSTS_PER_PAGE = 3
    DEFAULT_AUTHOR = 'This guy'
    MAX_IMAGE_WIDTH = 1024  # units: px
    # input file paths
    POSTS_PATH = './posts/'
    IMAGE_PATH = './posts/images/'
    ADDITIONAL_FILES_PATH = './posts/etc/'
    TEMPLATE_PATH = './templates/'
    # output file paths
    OUTPUT_PATH = './output/'
    BLOG_PATH = 'blog/'
    BLOG_IMAGE_PATH = 'assets/img/'
    BLOG_ADDITIONAL_FILES_PATH = 'assets/etc/'
    # sitemap paths
    BASE_URL = 'https://www.some.site/'  # only for generating sitemap (all other links are relative)
    SITEMAP_PATH = 'sitemap.txt'
    SITEMAP_INCLUDE = ['index.html', 'about.html', 'resume.html', 'contact.html', 'blog/all-topics.html', 'blog/all-posts.html'] # in addition to posts
    # cache paths
    CACHE_PATH = './.cache/'
    IMAGE_CACHE_PATH = './.cache/images/'
    # should a preview be served to localhost after build?
    PREVIEW = True
    # port to use for preview
    PREVIEW_PORT = 8000
    # aws s3 parameters
    BUCKET_NAME = 'some.site'

