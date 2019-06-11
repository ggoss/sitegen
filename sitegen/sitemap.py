#!/usr/bin/env python3
# encoding: utf-8

# sitemap.py

from sitegen import *


def generate_sitemap(post_db: dict, format: str = 'txt') -> None:
    """

    Args:
        post_db: data for all posts
        format: (str) sitemap format; 'txt' is currently the only format supported

    Returns:
        nothing, but saves a sitemap to Params.SITEMAP_PATH, within Params.OUTPUT_PATH

    """

    if format is not 'txt':
        raise NotImplementedError

    with open(os.path.join(Params.OUTPUT_PATH, Params.SITEMAP_PATH), 'w+') as f:
        for page in Params.SITEMAP_INCLUDE:
            f.write(f'{Params.BASE_URL}{page}\n')
        for post in post_db:
            f.write(f'{Params.BASE_URL}{post_db[post]["url"][1:]}\n')