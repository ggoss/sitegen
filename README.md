# Sitegen
I wrote this static site generator to create my personal site, garrettgoss.com. See my blog post [here](https://garrettgoss.com/blog/2019/05/sitegen.html) for a more in-depth introduction.

# Getting started
These instructions will build the included example site, from test posts and templates.

## Clone the repo
Clone the repo to your local machine. For example:
```bash
git clone https://github.com/ggoss/sitegen
```

## Prepare the virtual environment

`cd` into the repo folder:
```bash
cd sitegen
```

Create the virtual environment:
```bash
python3 -m venv venv
```

Activate it:
```bash
source ./venv/bin/activate
```

Install dependencies:
```bash
pip3 install -r requirements.txt
```
NOTE: if you'd like to be able to losslessly reduce `svg` assets as part of the site generation process, download one of the pre-built releases of svgcleaner from https://github.com/RazrFalcon/svgcleaner/releases, and extract it to `sitegen/svgcleaner`. There are no `svgs` in the included example site, so you can get started without doing so.

## Build the included example site:
The test site should be successfully built to `sitegen/output` and served to `http://localhost:8000`
```bash
python3 sitegen.py
```

During the build, you should see something like this:
```bash
(venv) garrett@garrett-laptop:~/projects/sitegen$ python3 sitegen.py

Generating site.
---------------
[ 0.22 s] Cached post database not found. Initializing post database...
[ 0.22 s] Updating post database...
[ 1.41 s] Creating output directories...
[ 1.41 s] Generating pages for each post...
[ 1.46 s] Generating "all-topics" page...
[ 1.46 s] Generating "all-posts" page...
[ 1.46 s] Generating blog index...
[ 1.50 s] Caching posts...
[ 1.50 s] Caching images...
[ 1.51 s] Done.

Previewing site.
---------------
Serving to http://localhost:8000
Press CTRL+C to quit.
```

Subsequent builds should be faster, as previously-processed images (scaled and compressed) are cached and copied (rather than re-processed):
```bash
(venv) garrett@garrett-laptop:~/projects/sitegen$ python3 sitegen.py

Generating site.
---------------
[ 0.18 s] Copying cached images to output directory...
[ 0.19 s] Loading cached post database...
[ 0.19 s] Updating post database...
[ 0.20 s] Creating output directories...
[ 0.20 s] Generating pages for each post...
[ 0.24 s] Generating "all-topics" page...
[ 0.25 s] Generating "all-posts" page...
[ 0.25 s] Generating blog index...
[ 0.29 s] Caching posts...
[ 0.29 s] Caching images...
[ 0.29 s] Done.

Previewing site.
---------------
Serving to http://localhost:8000
Press CTRL+C to quit.
```

# Documentation
See [here](https://garrettgoss.com/blog/2019/05/sitegen.html) for a summary of current features.

# Configuration
Most settings can be configured in `sitegen/sitegen/config.py`.

If you'd like blog-post comments to work, go to https://utteranc.es/ and configure a comments repo. In the included blog-post template `sitegen/templates/blog-post.html`, replace `"[ENTER REPO HERE]"` with the repo you created.

To change the look and feel of the site, modify the included html templates and CSS (`sitegen/templates/assets/css/styles.css`) with reckless abandon. Sitegen uses Jinja2 for templating, so you have a ton of freedom here.

# License
Sitegen is licensed under the MIT License.
