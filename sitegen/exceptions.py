#!/usr/bin/env python3
# encoding: utf-8

# exceptions.py

class SitegenError(Exception):
    pass

class ImageProcessingError(SitegenError):
    def __init__(self, msg=None):
        error = 'An error occurred while processing an image.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class MarkdownProcessingError(SitegenError):
    def __init__(self, msg=None):
        error = 'An error occurred while processing a markdown file.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class ImageTagsError(MarkdownProcessingError):
    def __init__(self, msg=None):
        error = 'There was a problem with one of the image formatting tags in a markdown file. You might have omitted or incorrectly formatted a closing tag.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class CheckboxListError(MarkdownProcessingError):
    def __init__(self, msg=None):
        error = 'An error occurred while processing the checkboxes.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class TocError(MarkdownProcessingError):
    def __init__(self, msg=None):
        error = 'An error occurred while generating the table of contents.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class PostDatabaseError(MarkdownProcessingError):
    def __init__(self, msg=None):
        error = 'An error occurred while incorporating a markdown file into the post database.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)

class YoutubeEmbedError(MarkdownProcessingError):
    def __init__(self, msg=None):
        error = 'Invalid youtube link format.'
        if msg is None:
            msg = error
        else:
            msg = f'{error}: {msg}'
        super().__init__(msg)
