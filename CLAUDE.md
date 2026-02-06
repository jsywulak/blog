# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A static site generator for a personal blog, deployed to S3.

## Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Technology Stack

- **Language:** Python
- **Package Management:** pip + requirements.txt
- **Key Dependencies:** Jinja2 (templating), Markdown (content parsing)
- **Testing:** Not yet configured (pytest recommended)
- **Type Checking:** Not yet configured (mypy recommended)
- **Linting:** Not yet configured (ruff recommended)

## Build

- `python build.py` or `make build`
- Markdown posts in `content/` with YAML frontmatter (title, date) are rendered to HTML in `site/`
- Templates in `templates/`, static assets in `static/`
- `site/` is gitignored (generated output)

## Adding a Post

1. Create `content/{slug}.md` with frontmatter and markdown body:
   ```markdown
   ---
   title: My Post Title
   date: 2025-01-01
   ---

   Post content here.
   ```
2. Run `python build.py`

## Deploy

- `make deploy` (builds then syncs `site/` to S3)
