import glob
import os
import shutil
from datetime import datetime

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
    published = meta.get("published", ["true"])[0].lower() == "true"
    date = meta["date"][0]
    # Posts live at yyyy/mm/dd/slug.html
    date_path = datetime.strptime(date, "%Y-%m-%d").strftime("%Y/%m/%d")
    return {
        "title": meta["title"][0],
        "date": date,
        "slug": slug,
        "url": f"{date_path}/{slug}.html",
        "content": body,
        "published": published,
    }


def build():
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    base_template = env.get_template("base.html")
    index_template = env.get_template("index.html")

    # Start clean so removed or renamed posts don't linger
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR)

    # Collect and sort posts by date (oldest first for chronological order)
    posts = []
    for filepath in glob.glob(f"{CONTENT_DIR}/*.md"):
        post = parse_post(filepath)
        posts.append(post)
    posts.sort(key=lambda p: p["date"])

    # Published posts only, for navigation and index
    published_posts = [p for p in posts if p["published"]]

    # Build individual posts with prev/next navigation
    for post in posts:
        if post["published"]:
            idx = published_posts.index(post)
            prev_post = published_posts[idx - 1] if idx > 0 else None
            next_post = published_posts[idx + 1] if idx < len(published_posts) - 1 else None
        else:
            prev_post = None
            next_post = None
        html = base_template.render(
            title=post["title"],
            date=post["date"],
            content=post["content"],
            prev_post=prev_post,
            next_post=next_post,
        )
        output_path = f"{OUTPUT_DIR}/{post['url']}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)

    # Reverse for index (newest first)
    published_posts.reverse()

    # Build index page
    html = index_template.render(posts=published_posts)
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
