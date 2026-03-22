# Your first build

This tutorial walks you through setting up the project and running your first catalogue build from scratch. By the end you'll have a populated `catalogue.xlsx` with card data and downloaded images.

**Time required:** ~30 minutes (mostly waiting for the build to run)

---

## Prerequisites

You'll need the following installed before you start:

- **Python 3.12** — [python.org/downloads](https://www.python.org/downloads/)
- **uv** — a fast Python package manager. Install it by running this in your terminal:
  ```bash
  pip install uv
  ```
- **Microsoft Excel** — for viewing and working with the output

You'll also need a copy of this repository on your computer (either cloned via git or downloaded as a zip).

---

## Step 1 — Install dependencies

Open a terminal, navigate to the project folder, and run:

```bash
uv sync
```

This reads `pyproject.toml` and installs everything the project needs into a local virtual environment. You only need to do this once.

---

## Step 2 — Check the input workbook

The pipeline reads its configuration from `data/input/reference.xlsx`. Open it and check:

- The **Sets** sheet lists the sets you want to build. Sets marked `Yes` in the `In Scope` column will be processed.
- The **Rarities** sheet defines the variant rules for main sets — you shouldn't need to touch this.

If `reference.xlsx` doesn't exist yet, run:

```bash
uv run python scripts/create-input-workbook.py
```

---

## Step 3 — Run your first build

Start with a single main set to make sure everything works. Scarlet & Violet base set is a good choice:

```bash
uv run python scripts/build-catalogue.py --set sv01
```

You'll see progress printed to the terminal as each card is fetched:

```
============================================================
  Scarlet & Violet (sv01) [main]
============================================================
  198 cards | Released: 2023-03-31
  [1/198] Sprigatito (sv01-001) -> Normal, Reverse Holo  [ETA 12m30s]
  [2/198] Floragato (sv01-002) -> Normal, Reverse Holo  [ETA 11m55s]
  ...
```

The ETA updates with each card as the pipeline gets a feel for the API response speed.

> **Tip:** The first run fetches everything from the API and downloads all card images, so it takes a while — typically 5–20 minutes depending on the set size and network speed. Subsequent runs for the same set are skipped automatically.

---

## Step 4 — View the output

When the build finishes, open `data/output/catalogue.xlsx`. You'll find two sheets:

- **Sets** — one row per processed set with card counts and release dates
- **Cards** — one row per card with every available field from the API: rarity, HP, attacks, pricing, image paths, and more

Both sheets are formatted as named Excel Tables (`Sets` and `Cards`), which means you can filter and sort immediately, and build Power Query views off them.

---

## Step 5 — Check the images

Card images are downloaded to `data/output/images/`, organised by size and series:

```
data/output/images/
├── large/
│   └── sv/
│       └── sv01/
│           ├── 001_sprigatito.jpg
│           ├── 002_floragato.jpg
│           └── ...
└── small/
    └── sv/
        └── sv01/
            └── ...
```

One image is downloaded per card and shared across all its variants (Normal, Reverse Holo, etc.).

---

## Step 6 — Add more sets

Once your first build looks good, add more sets. Each run appends to the same `catalogue.xlsx` — sets already in the workbook are skipped automatically:

```bash
uv run python scripts/build-catalogue.py --set sv02
uv run python scripts/build-catalogue.py --set sv10
```

Or process all in-scope sets in one go:

```bash
uv run python scripts/build-catalogue.py
```

---

## Next steps

- [Create a Power Query view](../how-to/create-a-power-query-view.md) — slice the Cards master into a purpose-built listing view
- [Add a special set](../how-to/add-a-special-set.md) — special sets like Ascended Heroes require a manual review step before the pipeline can run
- [Scripts reference](../reference/scripts.md) — all available command-line options
