# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based blog project (early development stage).

## Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (once requirements.txt or pyproject.toml is created)
pip install -r requirements.txt
# or: poetry install
# or: pdm install
```

## Technology Stack

- **Language:** Python
- **Package Management:** Not yet configured (supports Poetry, pdm, pipenv, or UV based on .gitignore)
- **Testing:** Not yet configured (pytest recommended)
- **Type Checking:** Not yet configured (mypy recommended)
- **Linting:** Not yet configured (ruff recommended)
