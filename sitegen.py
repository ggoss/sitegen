#!/usr/bin/env python3
# encoding: utf-8

# sitegen.py

print('\nGenerating site.\n---------------')

# Time site generation
import time
st = time.time()
elapsed_time = lambda: time.time() - st

# Module Import
from sitegen import *

# Empty output directory if it already exists
if os.path.exists(Params.OUTPUT_PATH):
    shutil.rmtree(Params.OUTPUT_PATH)

# Copy site assets from the template directory that that will not be modified by this program (e.g. the 'Resume' page)
shutil.copytree(Params.TEMPLATE_PATH, Params.OUTPUT_PATH, ignore=shutil.ignore_patterns('index.html', 'all-topics.html', 'all-posts.html', 'blog-post.html'))

# Move image assets that have already been processed (in previous builds) to the output directory (so we don't waste
# time repeating the process)
if os.path.exists(Params.IMAGE_CACHE_PATH):
    print(f'[{elapsed_time():5.2f} s] Copying cached images to output directory...')
    for image in os.listdir(Params.IMAGE_CACHE_PATH):
        shutil.copy(Params.IMAGE_CACHE_PATH + image, Params.OUTPUT_PATH + Params.BLOG_IMAGE_PATH)

# Move additional (non-image) files, if they exist, from the ADDITIONAL_FILES_PATH to the BLOG_ADDITIONAL_FILES_PATH
if os.path.exists(Params.ADDITIONAL_FILES_PATH):
    if not os.path.exists(Params.BLOG_ADDITIONAL_FILES_PATH):
        os.makedirs(Params.OUTPUT_PATH + Params.BLOG_ADDITIONAL_FILES_PATH)
    for file in os.listdir(Params.ADDITIONAL_FILES_PATH):
        shutil.copy(Params.ADDITIONAL_FILES_PATH + file, Params.OUTPUT_PATH + Params.BLOG_ADDITIONAL_FILES_PATH)

# Load cached 'post_db' (if it exists) to avoid re-processing all assets on every build
if os.path.exists(f'{Params.CACHE_PATH}post_cache.json'):
    print(f'[{elapsed_time():5.2f} s] Loading cached post database...')
    with open(f'{Params.CACHE_PATH}post_cache.json', 'r') as post_cache:
        cached_post_db = json.load(post_cache)
else:
    print(f'[{elapsed_time():5.2f} s] Cached post database not found. Initializing post database...')
    cached_post_db = None

# Gather and process posts
print(f'[{elapsed_time():5.2f} s] Updating post database...')
post_db = build_post_db(Params.POSTS_PATH, Params.BLOG_PATH, cached_post_db)
pagination_dict = build_blog_pagination_dict(post_db, posts_per_page=Params.POSTS_PER_PAGE)
topic_posts_dict = build_topic_dict(post_db, 'date')

print(f'[{elapsed_time():5.2f} s] Creating output directories...')
make_output_dirs(post_db, pagination_dict, Params.OUTPUT_PATH)

# Render all individual blog post pages
print(f'[{elapsed_time():5.2f} s] Generating pages for each post...')
for post in pagination_dict['all_posts']:
    html = render_from_template(Params.TEMPLATE_PATH, 'blog-post.html', **post_db[post], post_db=post_db)

    with open(Params.OUTPUT_PATH + post_db[post]['url'], 'w') as f:
        f.write(html)

# Render 'all-topics' page, listing all topics and all posts in each
print(f'[{elapsed_time():5.2f} s] Generating "all-topics" page...')
with open(Params.OUTPUT_PATH + Params.BLOG_PATH + 'all-topics.html', 'w') as f:
    html = render_from_template(Params.TEMPLATE_PATH, 'all-topics.html', topic_posts_dict=topic_posts_dict, post_db=post_db)
    f.write(html)

# Render 'all-posts' page
print(f'[{elapsed_time():5.2f} s] Generating "all-posts" page...')
with open(Params.OUTPUT_PATH + Params.BLOG_PATH + 'all-posts.html', 'w') as f:
    newest_posts = get_newest_posts(post_db)
    html = render_from_template(Params.TEMPLATE_PATH, 'all-posts.html', newest_posts=newest_posts, post_db=post_db)
    f.write(html)

# Render blog index
print(f'[{elapsed_time():5.2f} s] Generating blog index...')
for page_number in range(pagination_dict['n_pages'] + 1)[1:]:
    # rel and prev links to add to page <head>
    if pagination_dict['n_pages'] > 1:
        if page_number == 1:
            rel_links = f'<link rel="next" href="{pagination_dict[page_number + 1]["url"]}"/>'
        elif page_number == pagination_dict['n_pages']:
            rel_links = f'<link rel="prev" href="{pagination_dict[page_number - 1]["url"]}"/>'
        else:
            rel_links = f'<link rel="next" href="{pagination_dict[page_number + 1]["url"]}"/>\n<link rel="prev" href="{pagination_dict[page_number - 1]["url"]}"/>'
    else:
        rel_links = ''

    html = render_from_template(Params.TEMPLATE_PATH, 'index.html', post_db=post_db, pagination_dict=pagination_dict, current_page=page_number, rel_links=rel_links)

    with open(Params.OUTPUT_PATH + pagination_dict[page_number]['url'] + 'index.html', 'w') as f:
        f.write(html)

# Generate sitemap
generate_sitemap(post_db)

# Cache 'post_db' so that we can keep track of what has changed from build-to-build
print(f'[{elapsed_time():5.2f} s] Caching posts...')
if not os.path.exists(Params.CACHE_PATH):
    os.makedirs(Params.CACHE_PATH)

with open(f'{Params.CACHE_PATH}post_cache.json', 'w') as post_cache:
    json.dump(post_db, post_cache, default=str) # 'default=str' used as datetime is not serializable by default

# Cache processed images to speed up future website builds
print(f'[{elapsed_time():5.2f} s] Caching images...')
if not os.path.exists(Params.IMAGE_CACHE_PATH):
    os.makedirs(Params.IMAGE_CACHE_PATH)

cached_images = [cached_image for cached_image in os.listdir(Params.IMAGE_CACHE_PATH)]

for image in os.listdir(Params.OUTPUT_PATH + Params.BLOG_IMAGE_PATH):
    if image not in cached_images:
        shutil.copy(Params.OUTPUT_PATH + Params.BLOG_IMAGE_PATH + image, Params.IMAGE_CACHE_PATH)

# Print time taken to generate site
print(f'[{elapsed_time():5.2f} s] Done.')

# Serve the current version of the blog to localhost:8000 for previewing
if Params.PREVIEW is True:
    print('\nPreviewing site.\n---------------')
    serve(Params.OUTPUT_PATH, Params.PREVIEW_PORT)