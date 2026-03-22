# Pokemon TCG Catalogue

A pipeline that builds a master catalogue of Pokemon TCG card data, starting with the Mega Evolution and Scarlet & Violet series. Powers eBay multi-variation listings today, and a personal storefront in the future.

## What it does

- Fetches card data (metadata, pricing, images) from the [TCGdex API](https://tcgdex.net)
- Determines the correct variants for each card (Normal, Holo, Reverse Holo, named variants for special sets)
- Downloads card images at two sizes (large and small)
- Writes everything to `data/output/catalogue.xlsx` — a master Excel workbook with named tables, ready for Power Query views

## Documentation

| | |
| --- | --- |
| [Your first build](docs/tutorials/your-first-build.md) | Get set up and run your first catalogue build end-to-end |
| [Add a main set](docs/how-to/add-a-main-set.md) | Add a standard set to the catalogue |
| [Add a special set](docs/how-to/add-a-special-set.md) | Add a special set (requires manual review step) |
| [Create a Power Query view](docs/how-to/create-a-power-query-view.md) | Slice the master catalogue into a custom view in Excel |
| [Scripts reference](docs/reference/scripts.md) | All scripts and their command-line options |
| [Reference workbook](docs/reference/reference-workbook.md) | `data/input/reference.xlsx` sheet-by-sheet |
| [Catalogue workbook](docs/reference/catalogue-workbook.md) | `data/output/catalogue.xlsx` structure and image paths |
| [Architecture](docs/explanation/architecture.md) | Vision, phases, design decisions |
| [Set types explained](docs/explanation/set-types.md) | Main vs special sets, rarity rules, variant logic |

## Quick start

```bash
uv sync                                                    # install dependencies
uv run python scripts/build-catalogue.py --set sv10        # build a single set
uv run python scripts/build-catalogue.py                   # build all in-scope sets
```

See [Your first build](docs/tutorials/your-first-build.md) for a full walkthrough.
