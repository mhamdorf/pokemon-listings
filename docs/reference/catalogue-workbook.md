# Catalogue workbook (`data/output/catalogue.xlsx`)

The main output of the pipeline. Generated and updated by `build-catalogue.py`. This file is gitignored — it's a build artefact, not source data.

---

## Sheets

### Sets

A summary of every set that has been built into the catalogue.

| Column | Description | Example |
| --- | --- | --- |
| Set ID | TCGdex set identifier | `sv10` |
| Set Name | Human-readable name | `Destined Rivals` |
| Series ID | Series code | `sv` |
| Series Name | Series name | `Scarlet & Violet` |
| Set Type | `main` or `special` | `main` |
| Total Cards | Number of cards in the set | `244` |
| Release Date | Official release date | `2025-05-30` |

### Cards

The master record — one row per card, every available field from the TCGdex API.

| Column | Description |
| --- | --- |
| Card ID | TCGdex card identifier — e.g. `sv10-001` |
| Set ID | e.g. `sv10` |
| Local ID | Card number within the set — e.g. `001` |
| Name | Card name |
| Category | `Pokemon`, `Trainer`, or `Energy` |
| Rarity | As returned by TCGdex — e.g. `Common`, `Double Rare`, `Illustration Rare` |
| HP | Hit points (Pokemon only) |
| Types | Comma-separated energy types — e.g. `Grass`, `Fire, Water` |
| Stage | `Basic`, `Stage 1`, `Stage 2` (Pokemon only) |
| Evolves From | Name of the pre-evolution, if any |
| Pokédex ID | National Pokédex number(s), comma-separated |
| Retreat Cost | Number of energy to retreat |
| Trainer Type | `Item`, `Supporter`, `Stadium` (Trainer cards only) |
| Abilities | Stringified — e.g. `Ability: Wonder Guard — Effect text` |
| Attacks | Stringified — e.g. `Vise Grip [Grass] 20 \| Tackle [Colorless,Colorless] 40` |
| Weaknesses | e.g. `Fire ×2` |
| Resistances | e.g. `Psychic -30` |
| Card Effect | Full effect text (Trainer and Energy cards) |
| Regulation Mark | e.g. `I`, `J` |
| Legal (Standard) | `Yes` or `No` |
| Legal (Expanded) | `Yes` or `No` |
| Illustrator | Illustrator credit |
| Image (API URL) | TCGdex base image URL — for reference |
| Image (Large) | Relative path to the downloaded high-res image |
| Image (Small) | Relative path to the downloaded low-res image |
| Variants | Pipe-separated variant labels — e.g. `Normal \| Reverse Holo` |
| Price USD (TCGPlayer) | Market or mid price in USD at time of build |
| Price EUR (Cardmarket) | Trend price in EUR at time of build |
| Last Updated (API) | Timestamp of last TCGdex data update |

> **Note on pricing:** Prices are a snapshot taken at build time and will go stale. They are not updated on Power Query refresh — only when a set is rebuilt via the pipeline.

Both the Sets and Cards sheets are formatted as named Excel Tables (`Sets` and `Cards`), enabling Power Query to reference them by name.

---

## Power Query views

Slice views (e.g. a Catalogue for listings) are not written by the pipeline — they're built as Power Query queries inside the workbook itself, reading from the `Cards` table. See [Create a Power Query view](../how-to/create-a-power-query-view.md).

When new sets are added via the pipeline, refresh all queries with **Data → Refresh All**.

---

## Images

Downloaded alongside the catalogue build, stored at:

```
data/output/images/
├── large/
│   └── {series_id}/
│       └── {set_id}/
│           └── {local_id}_{card-name-slug}.jpg   ← high resolution
└── small/
    └── {series_id}/
        └── {set_id}/
            └── {local_id}_{card-name-slug}.jpg   ← low resolution
```

**Example paths:**

```
data/output/images/large/sv/sv10/001_ethans-pinsir.jpg
data/output/images/small/me/me02.5/003_erikas-vileplume-ex.jpg
```

One image is downloaded per card, shared across all its variants. The `Image (Large)` and `Image (Small)` columns in the Cards sheet store relative paths to these files.

Images are gitignored — they're not committed to the repository.
