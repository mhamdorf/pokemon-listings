# Scripts reference

All scripts live in `scripts/` and are run from the project root:

```bash
uv run python scripts/<script-name>.py [options]
```

---

## build-catalogue.py

The main pipeline. Fetches card data from TCGdex, determines variants, downloads images, and writes to `data/output/catalogue.xlsx`.

Supports incremental builds — sets already in the catalogue are detected and skipped automatically.

### Options

| Option | Description |
| --- | --- |
| `--set <set_id>` | Process a single set only (e.g. `--set sv10`) |
| `--dry-run` | Fetch and print without writing any files or downloading images |

### Examples

```bash
# Add a single set
uv run python scripts/build-catalogue.py --set sv10

# Add all in-scope sets that haven't been built yet
uv run python scripts/build-catalogue.py

# Preview what would happen for a set without writing anything
uv run python scripts/build-catalogue.py --set sv10 --dry-run
```

### What it writes

- `data/output/catalogue.xlsx` — appends to existing file, or creates fresh if absent
- `data/output/images/large/{series}/{set}/` — high-resolution card images
- `data/output/images/small/{series}/{set}/` — low-resolution card images

---

## prep-special-set.py

One-time prep tool for special sets. Scrapes Bulbapedia to generate a draft `VariantOverrides` sheet in `reference.xlsx`. Run this before `build-catalogue.py` for any special set.

### Options

| Option | Description |
| --- | --- |
| `--set <set_id>` | The special set ID to prepare (required) |
| `--bulbapedia-name <name>` | The Bulbapedia article name for the set (required) |

### Example

```bash
uv run python scripts/prep-special-set.py --set me02.5 --bulbapedia-name Ascended_Heroes
```

### What it writes

- Rows to the `VariantOverrides` sheet in `data/input/reference.xlsx`

After running, open `reference.xlsx`, review the `VariantOverrides` sheet, correct any uncertain rows, and fill in `reviewed_by` and `reviewed_date` before running the build.

---

## create-input-workbook.py

Creates `data/input/reference.xlsx` from scratch with the correct sheet structure. Run this once when setting up the project for the first time. Does not overwrite an existing file.

### Example

```bash
uv run python scripts/create-input-workbook.py
```

---

## explore-card-schema.py

Developer tool. Fetches a single card from TCGdex and prints every field it returns. Useful for inspecting the API schema or checking a specific card's data.

### Options

| Option | Description |
| --- | --- |
| `--card <card_id>` | The TCGdex card ID to inspect (e.g. `--card sv10-001`) |

### Example

```bash
uv run python scripts/explore-card-schema.py --card sv10-001
```

---

## explore-rarities.py

Developer tool. Inspects all rarities returned by TCGdex across one or more sets and shows how they map to variant flags. Useful when onboarding a new series and checking whether the Rarities sheet covers all rarity values.

### Example

```bash
uv run python scripts/explore-rarities.py
```
