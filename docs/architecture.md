# Architecture

## Vision

A Python backend that builds a master catalogue of Pokemon TCG card data, designed to power multiple frontends:

- **Phase 1** — eBay multi-variation listings (buyer selects from a dropdown of card + variant combinations)
- **Phase 2** — eBay API integration with AUD pricing via sold comps
- **Phase 3** — Own TCG storefront website

Each phase builds directly on the last — nothing gets thrown away.

---

## Scope

The following series are in scope for now:

| Series | ID |
|---|---|
| Mega Evolution | `me` |
| XY | `xy` |
| Sun & Moon | `sm` |
| Sword & Shield | `swsh` |
| Scarlet & Violet | `sv` |

Vintage series (Base, Jungle, Fossil, etc.) are deliberately out of scope. The data model accommodates them for future expansion.

Pokémon TCG Pocket (`tcgp`) is excluded — digital only, not physical cards.

---

## Data Sources

| Source | Purpose | When Used |
|---|---|---|
| TCGdex API (`api.tcgdex.net/v2/en`) | Card metadata, images, variant flags, pricing | Main pipeline (runtime) |
| Frankfurter API (`api.frankfurter.app`) | USD → AUD currency conversion | Main pipeline (runtime) |
| Bulbapedia (scraping) | Draft variant names for special sets | Prep tool only (one-time per special set) |
| eBay Australia API | AUD sold comps | Phase 2 (not yet built) |
| Custom photos | Per-variant card images | Future — photographing physical stock |

---

## Set Types

| Type | Description | Variant Logic |
|---|---|---|
| `main` | Standard sets | Rarity rules table (see below) |
| `special` | Non-standard sets (e.g. Ascended Heroes) | Manual override sheet, required before pipeline runs |

Special sets can have up to 3–4 variants per card, including named reverse holos (e.g. "Reverse Holo (Fire Energy)", "Reverse Holo (Friend Ball)"). The TCGdex boolean flags are not granular enough to handle these — hence the manual override requirement.

---

## Rarity Rules

Determines variant logic for main sets. If a rarity is not in the table, the pipeline defaults to `can_reverse_holo = False`.

| Rarity | Base Finish | Can Reverse Holo | Notes |
|---|---|---|---|
| Common | Normal | Yes | |
| Uncommon | Normal | Yes | |
| Rare | Holo | Yes | Older sets |
| Rare Holo | Holo | Yes | DP–BW era |
| Holo Rare | Holo | Yes | SWSH era |
| Double Rare | Holo | No | |
| Ultra Rare | Holo | No | |
| Illustration Rare | Holo | No | |
| Special Illustration Rare | Holo | No | |
| Hyper Rare | Holo | No | |
| ACE SPEC Rare | Holo | No | |
| Radiant Rare | Holo | No | |
| Amazing Rare | Holo | No | |
| Shiny Rare | Holo | No | |
| Shiny Ultra Rare | Holo | No | |

This table lives in the input workbook (`data/input/reference.xlsx`, sheet: `Rarities`) and is read by the pipeline at runtime — nothing is hardcoded.

---

## Data Model

### `sets`
| Field | Example | Notes |
|---|---|---|
| `set_id` | `me02.5` | TCGdex ID |
| `set_name` | `Ascended Heroes` | |
| `set_type` | `special` | `main` or `special` |
| `series_id` | `me` | |
| `series_name` | `Mega Evolution` | |
| `total_cards` | `295` | |
| `release_date` | `2026-01-31` | |

### `cards` — master catalogue (pure reference data, never modified by operational processes)
| Field | Example | Notes |
|---|---|---|
| `card_id` | `me02.5-001` | TCGdex ID |
| `set_id` | `me02.5` | |
| `local_id` | `001` | Card number within set |
| `name` | `Erika's Oddish` | |
| `rarity` | `Common` | |
| `hp` | `60` | |
| `types` | `Grass` | Comma-separated if multiple |
| `stage` | `Basic` | |
| `illustrator` | `Yoriyuki Ikegami` | |
| `regulation_mark` | `J` | |
| `image_api` | `https://assets.tcgdex.net/...` | TCGdex base URL |
| `image_custom` | *(empty)* | Reserved for future custom photos |

### `variants` — one row per card + variant (the listing unit)
| Field | Example | Notes |
|---|---|---|
| `variant_id` | `me02.5-001-normal` | Generated |
| `card_id` | `me02.5-001` | |
| `variant_label` | `Reverse Holo (Fire Energy)` | The eBay dropdown value |
| `finish` | `Reverse Holo` | Normalised finish type |
| `image_api` | `https://assets.tcgdex.net/...` | Inherited from card (same image for all variants) |
| `image_custom` | *(empty)* | Reserved for variant-specific photos |
| `price_usd_tcgplayer` | `0.12` | From TCGdex API |
| `price_aud_converted` | `0.19` | Dynamically converted via Frankfurter at time of generation |
| `price_aud_ebay` | *(empty)* | Reserved for Phase 2 eBay comps |

---

## Input Workbook (`data/input/reference.xlsx`)

All pipeline configuration lives here. Human-maintained.

| Sheet | Purpose |
|---|---|
| `Sets` | Set registry — which sets to process, their type, series |
| `Rarities` | Rarity rules table (base finish, can_reverse_holo) |
| `VariantOverrides` | Manual variant definitions for special sets (see below) |

---

## Special Set Workflow

Special sets require human preparation before the pipeline can run. The pipeline will error if a special set is queued without a confirmed override entry.

### Step-by-step process

1. **Run the prep tool** to scrape Bulbapedia and generate a draft:
   ```
   uv run python scripts/prep-special-set.py --set <set_id>
   ```
   This writes a draft to the `VariantOverrides` sheet in `data/input/reference.xlsx`.

2. **Review the draft** — open `reference.xlsx` and check the `VariantOverrides` sheet:
   - Verify each card's variant list against physical cards or community resources
   - Correct any wrong or missing variant names
   - The variant names are pipe-separated (e.g. `Normal|Reverse Holo (Fire Energy)|Reverse Holo (Friend Ball)`)

3. **Sign off** — fill in `reviewed_by` and `reviewed_date` for each row.

4. **Run the pipeline** — the pipeline reads the confirmed override sheet as the authority.

### `VariantOverrides` sheet columns

| Column | Example | Notes |
|---|---|---|
| `set_id` | `me02.5` | |
| `local_id` | `001` | |
| `card_name` | `Erika's Oddish` | For readability |
| `variants` | `Normal\|Reverse Holo (Fire Energy)\|Reverse Holo (Friend Ball)` | Pipe-separated, exact labels |
| `reviewed_by` | `hamdo` | Must be filled before pipeline will process |
| `reviewed_date` | `2026-03-21` | Must be filled before pipeline will process |
| `notes` | `Confirmed via physical card` | Optional |

---

## Pipeline Scripts

| Script | Purpose | Run when |
|---|---|---|
| `scripts/prep-special-set.py` | Scrapes Bulbapedia to draft `VariantOverrides` for a special set | Once per special set, before pipeline |
| `scripts/build-catalogue.py` | Main pipeline — builds master catalogue from TCGdex + input workbook | When processing a new set |
| `scripts/explore-card-schema.py` | Dev tool — inspect all API fields for a given card | As needed |
| `scripts/explore-rarities.py` | Dev tool — inspect all rarities and their variant flags | As needed |

### `build-catalogue.py` logic (per set)

1. Read set registry from `Sets` sheet — determine set type
2. If `special`: check `VariantOverrides` sheet for all cards in set — **error if any card is missing or unreviewed**
3. If `main`: load rarity rules from `Rarities` sheet
4. Fetch card data from TCGdex for each card in the set
5. Determine variants:
   - Special set → use override sheet
   - Main set → apply rarity rules; unknown rarity defaults to no reverse holo
6. Fetch current USD → AUD rate from Frankfurter API (once per run)
7. Write to master catalogue (`data/output/catalogue.xlsx`): sets, cards, variants sheets
8. Download images to `data/output/images/`

---

## Folder Structure

```
pokemon-listings/
├── scripts/              # Pipeline and utility scripts
├── data/
│   ├── input/            # reference.xlsx (sets, rarities, variant overrides)
│   └── output/           # Generated catalogue, images (gitignored)
│       ├── images/
│       └── catalogue.xlsx
├── docs/                 # Design documents (here)
├── main.py               # Entry point (TBD)
└── CLAUDE.md
```

---

## Operational Workbooks (future — layered on top of master catalogue)

The master catalogue is read-only reference data. Operational concerns live separately:

| Workbook | Purpose |
|---|---|
| `inventory.xlsx` | Which cards you physically own, quantity, condition |
| `listings.xlsx` | eBay listing IDs, listed prices, listing status |

---

## Key Design Decisions

- **Master catalogue is append-only reference data** — inventory, listings, and pricing are never written back into it
- **Bulbapedia is a prep tool only** — never a runtime dependency; unreliable as a live data source
- **Unknown rarities default to no reverse holo** — safe fallback; can be corrected by adding to the rarities table
- **Special sets block the pipeline if overrides are missing** — enforces the human review step; prevents silent data gaps
- **`image_custom` columns reserved now** — populated later when physical cards are photographed; pipeline prefers custom over API image if present
- **TCGPlayer USD pricing pulled at generation time** and converted to AUD via Frankfurter; a separate `price_aud_ebay` column is reserved for Phase 2
- **Vintage series are out of scope** but the data model supports them — add rarity rules and they'll work
