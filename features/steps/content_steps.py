"""Step definitions for website content tests."""

import os
import glob
import re

from behave import given, then


OUTPUT_DIR = "site"


@given("the site has been built")
def step_site_is_built(context):
    """Confirm the site output directory exists with expected files."""
    assert os.path.isdir(OUTPUT_DIR), f"{OUTPUT_DIR}/ directory does not exist"
    assert os.path.isfile(os.path.join(OUTPUT_DIR, "index.html")), \
        f"{OUTPUT_DIR}/index.html does not exist"
    assert os.path.isfile(os.path.join(OUTPUT_DIR, "404.html")), \
        f"{OUTPUT_DIR}/404.html does not exist"


@then('the index page should not contain a link to "{filename}"')
def step_index_no_link(context, filename):
    """Assert the index page does not link to the given file."""
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path) as f:
        content = f.read()
    assert f'href="{filename}"' not in content, \
        f"Index page unexpectedly contains a link to {filename}"


@then('no published post should contain a link to "{filename}"')
def step_no_post_links_to(context, filename):
    """Assert no published post page links to the given file."""
    for filepath in glob.glob(os.path.join(OUTPUT_DIR, "*.html")):
        basename = os.path.basename(filepath)
        if basename in ("index.html", "404.html", filename):
            continue
        with open(filepath) as f:
            content = f.read()
        assert f'href="{filename}"' not in content, \
            f"Published post {basename} unexpectedly contains a link to {filename}"


@then('the file "{filename}" should exist in the output')
def step_file_exists(context, filename):
    """Assert a file exists in the output directory."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    assert os.path.exists(filepath), f"Expected {filename} to exist in {OUTPUT_DIR}/"


@then('the page "{filename}" should have no prev or next navigation links')
def step_no_nav_links(context, filename):
    """Assert a page has no prev/next navigation links (only Home)."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath) as f:
        content = f.read()
    nav_links = re.findall(r'<nav class="post-nav">(.*?)</nav>', content, re.DOTALL)
    assert len(nav_links) == 1, "Expected exactly one post-nav element"
    nav_html = nav_links[0]
    post_links = re.findall(r'href="[^"]*\.html"', nav_html)
    assert len(post_links) == 0, \
        f"Draft page should have no prev/next links, but found: {post_links}"
