# Add a special set to the catalogue

Special sets — any set with `.5` in its ID, like `me02.5` (Ascended Heroes) or `sv03.5` (151) — have non-standard variant structures. Their reverse holos have specific names rather than generic "Reverse Holo", so the pipeline can't determine them automatically. A manual review step is required before the build can run.

---

## Overview

The process has four steps:

1. Register the set in `reference.xlsx`
2. Run the prep tool to generate a draft override sheet
3. Review and sign off the draft
4. Run the build

---

## Step 1 — Register the set

Open `data/input/reference.xlsx` and add a row to the **Sets** sheet:

| Column | Value | Notes |
| --- | --- | --- |
| Set ID | `sv03.5` | Must match the TCGdex set ID exactly |
| Set Name | `151` | Human-readable name |
| Series ID | `sv` | Series code |
| Series Name | `Scarlet & Violet` | Human-readable series name |
| Set Type | `special` | **Must be `special`** |
| In Scope | `Yes` | |
| Notes | *(optional)* | |

Save `reference.xlsx`.

---

## Step 2 — Run the prep tool

The prep tool scrapes Bulbapedia to generate a draft of the variant overrides for each card in the set. Run it with the set ID and the Bulbapedia article name for the set:

```bash
uv run python scripts/prep-special-set.py --set sv03.5 --bulbapedia-name Pokémon_TCG:_Scarlet_&_Violet_151
```

> **Finding the Bulbapedia article name:** Search for the set on [bulbapedia.bulbagarden.net](https://bulbapedia.bulbagarden.net). The article name is the part of the URL after `/wiki/` — use underscores for spaces.

This writes a draft to the **VariantOverrides** sheet in `reference.xlsx`. Rows the tool was uncertain about are highlighted in yellow.

---

## Step 3 — Review the draft

Open `reference.xlsx` and go to the **VariantOverrides** sheet. For each row:

- Check the variant list against your physical cards or a reliable community resource
- The `variants` column is pipe-separated — e.g. `Normal|Reverse Holo (Grass Energy)|Reverse Holo (Poké Ball)`
- Correct any rows marked `Reverse Holo (???)` — the tool couldn't determine the variant name
- For `ex` cards and other premium rarities, the typical answer is just `Holo` (no reverse holo)
- When you're satisfied with a row, fill in `reviewed_by` (your name) and `reviewed_date` (today's date)

The pipeline will not process any card whose row is missing `reviewed_by` or `reviewed_date`.

---

## Step 4 — Run the build

Once all rows are reviewed and signed off:

```bash
uv run python scripts/build-catalogue.py --set sv03.5
```

The pipeline reads the confirmed override sheet as the sole authority for variants — rarity rules are not used for special sets.

---

## Notes

- The prep tool is a starting point, not a final answer. Always verify against physical cards.
- If you add new cards to the override sheet after the build has run, you'll need to delete the set's rows from `catalogue.xlsx` and rebuild — there's no partial update.
- See [Set types explained](../explanation/set-types.md) for background on why special sets work differently.
