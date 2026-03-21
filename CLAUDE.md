# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool for generating Pokemon listings, likely using data from APIs and producing spreadsheet/image outputs. Uses `pandas` and `openpyxl` for data/Excel handling, `Pillow` for images, and `requests` for HTTP.

## Setup & Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync

# Run the project
uv run python main.py

# Add a dependency
uv add <package>
```

## Project Structure

- `main.py` — entry point
- `scripts/` — standalone data pipeline scripts
- `data/input/` — manually provided input files (e.g. set lists, config)
- `data/output/` — all generated files: Excel workbooks, images (gitignored)
- `pyproject.toml` — project metadata and dependencies (Python 3.12+)
- `uv.lock` — locked dependency versions (commit this)

All scripts must write outputs to `data/output/` and read inputs from `data/input/`.
