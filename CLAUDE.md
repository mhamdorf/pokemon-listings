# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project overview

A Python pipeline that builds a master Pokemon TCG card catalogue from the TCGdex API, powering eBay multi-variation listings and eventually a personal TCG storefront.

**In-scope series:** Mega Evolution (`me`), Scarlet & Violet (`sv`). XY, Sun & Moon, Sword & Shield registered but deferred.

See `docs/explanation/architecture.md` for the full design.

## Setup

Uses [uv](https://docs.astral.sh/uv/) for dependency management (Python 3.12).

```bash
uv sync          # install dependencies
uv add <package> # add a new dependency
```

## Scripts

All scripts run from the project root via `uv run python scripts/<name>.py`.

| Script | Purpose |
| --- | --- |
| `build-catalogue.py` | Main pipeline — incremental builds, appends new sets to `catalogue.xlsx` |
| `prep-special-set.py` | One-time prep for special sets — drafts VariantOverrides via Bulbapedia |
| `create-input-workbook.py` | Creates `data/input/reference.xlsx` (run once to initialise) |
| `explore-card-schema.py` | Dev tool — inspect all API fields for a given card |
| `explore-rarities.py` | Dev tool — inspect all rarities and their variant flags across sets |

### Common commands

```bash
# Add a single set
uv run python scripts/build-catalogue.py --set sv10

# Add all in-scope sets not yet built
uv run python scripts/build-catalogue.py

# Dry run (no files written)
uv run python scripts/build-catalogue.py --set sv10 --dry-run

# Prepare a special set for manual review
uv run python scripts/prep-special-set.py --set me02.5 --bulbapedia-name Ascended_Heroes
```

## Folder structure

```text
pokemon-listings/
├── scripts/              # pipeline and utility scripts
├── data/
│   ├── input/            # reference.xlsx — commit this
│   └── output/           # catalogue.xlsx, images/ — gitignored
├── docs/
│   ├── tutorials/
│   ├── how-to/
│   ├── reference/
│   └── explanation/
└── main.py               # entry point (not yet built out)
```

## Output structure

**`data/output/catalogue.xlsx`** — two sheets, both formatted as named Excel Tables:

- `Sets` — one row per processed set
- `Cards` — one row per card, all TCGdex fields (master reference)

Power Query views (e.g. Catalogue for listings) are built inside the workbook reading from the `Cards` table — not written by the pipeline.

**`data/output/images/`** — card images at two sizes:

```text
images/large/{series_id}/{set_id}/{local_id}_{card-name-slug}.jpg
images/small/{series_id}/{set_id}/{local_id}_{card-name-slug}.jpg
```

## Key concepts

- **Set types:** `main` (rarity rules drive variant logic) vs `special` (manual VariantOverrides required). Sets with `.5` in their ID are always special.
- **Special sets block the pipeline** if VariantOverrides entries are missing or unreviewed — run `prep-special-set.py` first, then human fills in `reviewed_by` + `reviewed_date`.
- **Incremental builds** — `build-catalogue.py` detects existing sets in `catalogue.xlsx` and skips them. Running the same set twice is safe.
- **One image per card**, shared across all variants — no per-variant images.
- **Rarity rules** live in `data/input/reference.xlsx` (Rarities sheet), not hardcoded. Unknown rarities default to `Holo` with no reverse holo.
- **Pricing:** TCGPlayer USD and Cardmarket EUR pulled from TCGdex at build time, converted to AUD via Frankfurter. Prices go stale — not updated on Power Query refresh.
- **Master catalogue is append-only reference data** — inventory, listings, and eBay pricing live in separate workbooks (future).

## Design preferences

- **Documentation** follows the [Diataxis](https://diataxis.fr) framework: tutorials, how-to guides, reference, explanation.
- **Visual design** (workbooks, future website) follows a soft UI aesthetic — muted palette, single accent colour, generous whitespace. Reference points: Linear.app, Stripe. Workbook accent colour: `#5C5BDB` (soft indigo), alternating row fill: `#F4F3FF`.
