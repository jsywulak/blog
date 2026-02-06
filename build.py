import glob
import os
import shutil

import markdown
from jinja2 import Environment, FileSystemLoader

CONTENT_DIR = "content"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"
OUTPUT_DIR = "site"


def parse_post(filepath):
    md = markdown.Markdown(extensions=["meta"])
    with open(filepath) as f:
        body = md.convert(f.read())
    meta = md.Meta
    slug = os.path.splitext(os.path.basename(filepath))[0]
    return {
        "title": meta["title"][0],
        "date": meta["date"][0],
        "slug": slug,
        "content": body,
    }


def build():
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    base_template = env.get_template("base.html")
    index_template = env.get_template("index.html")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build individual posts
    posts = []
    for filepath in glob.glob(f"{CONTENT_DIR}/*.md"):
        post = parse_post(filepath)
        posts.append(post)
        html = base_template.render(title=post["title"], content=post["content"])
        with open(f"{OUTPUT_DIR}/{post['slug']}.html", "w") as f:
            f.write(html)

    # Sort posts by date, newest first
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Build index page
    html = index_template.render(posts=posts)
    with open(f"{OUTPUT_DIR}/index.html", "w") as f:
        f.write(html)

    # Build 404 page
    html = base_template.render(title="Page Not Found", content="<p>404 - Page Not Found</p>")
    with open(f"{OUTPUT_DIR}/404.html", "w") as f:
        f.write(html)

    # Copy static files
    shutil.copy(f"{STATIC_DIR}/style.css", f"{OUTPUT_DIR}/style.css")

    print(f"Built {len(posts)} post(s) to {OUTPUT_DIR}/")


if __name__ == "__main__":
    build()
