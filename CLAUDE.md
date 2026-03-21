# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python backend that builds a master Pokemon TCG card catalogue, powering eBay multi-variation listings and eventually a personal TCG storefront. See `docs/architecture.md` for the full design.

**In-scope series:** Mega Evolution (`me`), Scarlet & Violet (`sv`). XY, Sun & Moon, Sword & Shield to be added later.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management (Python 3.12).

```bash
uv sync          # install dependencies
uv add <package> # add a new dependency
```

## Scripts

All scripts are run from the project root via `uv run python scripts/<name>.py`.

| Script | Purpose |
|---|---|
| `build-catalogue.py` | Main pipeline — builds master catalogue from TCGdex + reference.xlsx |
| `prep-special-set.py` | One-time prep for special sets — drafts VariantOverrides sheet via Bulbapedia |
| `create-input-workbook.py` | Generates `data/input/reference.xlsx` (run once to initialise) |
| `explore-card-schema.py` | Dev tool — inspect all API fields for a given card |
| `explore-rarities.py` | Dev tool — inspect all rarities and their variant flags across sets |

### Common commands

```bash
# Process all in-scope sets
uv run python scripts/build-catalogue.py

# Process a single set
uv run python scripts/build-catalogue.py --set sv01

# Dry run (no files written)
uv run python scripts/build-catalogue.py --set sv01 --dry-run

# Prepare a special set for manual review
uv run python scripts/prep-special-set.py --set me02.5 --bulbapedia-name Ascended_Heroes
```

## Folder Structure

```
pokemon-listings/
├── scripts/              # all pipeline and utility scripts
├── data/
│   ├── input/            # reference.xlsx (sets, rarities, variant overrides) — commit this
│   └── output/           # generated catalogue, images — gitignored
├── docs/                 # design and architecture documentation
└── main.py               # entry point (not yet built out)
```

All scripts read inputs from `data/input/` and write outputs to `data/output/`.

## Key Concepts

- **Set types:** `main` (standard rarity rules) vs `special` (named reverse holos, requires manual override sheet). Sets with `.5` in their ID are always special.
- **Special sets block the pipeline** if `VariantOverrides` entries are missing or unreviewed — run `prep-special-set.py` first, then human reviews `reference.xlsx` and fills in `reviewed_by` + `reviewed_date`.
- **One image per card**, shared across all variants — downloaded to `data/output/images/`.
- **Rarity rules** live in `data/input/reference.xlsx` (Rarities sheet), not hardcoded. Unknown rarities default to no reverse holo.
- **Pricing:** TCGPlayer USD pulled from TCGdex API, converted to AUD via Frankfurter. `price_aud_ebay` column reserved for Phase 2.
