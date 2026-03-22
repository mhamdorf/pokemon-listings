# Architecture

## What this project is

A data pipeline that builds a master catalogue of Pokemon TCG card data. The catalogue drives everything downstream — eBay listings today, a personal storefront later. The Python scripts do the heavy lifting; the outputs are Excel workbooks and card images that anyone can work with.

---

## Phases

The project is designed in layers, each one building on the last without throwing anything away.

| Phase | Description | Status |
| --- | --- | --- |
| 1 | Build master catalogue · download images · eBay multi-variation listings | In progress |
| 2 | eBay AU API integration · AUD pricing from sold comps · automated listing management | Planned |
| 3 | Personal TCG storefront website | Planned |

---

## Data sources

| Source | What it provides | When it's used |
| --- | --- | --- |
| TCGdex API (`api.tcgdex.net/v2/en`) | Card metadata, images, variant flags, pricing | Pipeline runtime |
| Frankfurter API (`api.frankfurter.app`) | USD → AUD exchange rate | Pipeline runtime (once per run) |
| Bulbapedia (scraping) | Draft variant names for special sets | Prep tool only — one-time per special set |
| eBay Australia API | AUD sold comps | Phase 2 — not yet built |

Bulbapedia is deliberately never a runtime dependency. It's too unreliable as a live data source, and the data it provides (variant names) is human-verified anyway.

---

## Master data + views pattern

The pipeline writes a single master sheet (`Cards`) containing every available field for every card. Nothing is pre-filtered or pre-sliced.

Purpose-built views — a listings view, a website export, a pricing sheet — are built as Power Query queries inside Excel, reading from the `Cards` table. This means:

- Adding or removing columns from a view doesn't require re-running any Python
- Multiple views can coexist off the same master, each with different columns and filters
- New sets added via the pipeline flow into all views on the next Excel refresh

The master catalogue is append-only reference data. Operational concerns (inventory counts, listing IDs, sold prices) live in separate workbooks — never written back into the catalogue.

---

## Incremental builds

The pipeline supports incremental builds. When `catalogue.xlsx` already exists:

1. The pipeline reads which sets are already present (from the Sets sheet)
2. Any set already in the catalogue is skipped with a `[SKIP]` notice
3. New sets are appended — existing data is untouched

This means you can run the pipeline whenever a new set is released and it will only do the new work.

---

## Design decisions

**Rarity rules are configuration, not code.** The mapping from rarity to variant logic (base finish, can reverse holo) lives in `reference.xlsx`, not in the Python scripts. Adding support for a new rarity is a spreadsheet edit, not a code change.

**Special sets are fully manual.** For sets with non-standard variant structures, the pipeline requires a human-reviewed override sheet before it will run. This is intentional — a silent data gap in the catalogue is worse than a pipeline that refuses to continue.

**One image per card.** All variants of a card (Normal, Holo, Reverse Holo) share the same image. Variant-specific photography of physical stock is out of scope for now; the data model accommodates it when the time comes.

**Pricing is a snapshot, not live.** USD prices from TCGPlayer (via TCGdex) are captured at build time and converted to AUD via Frankfurter. They will go stale. Phase 2 will introduce a separate AUD pricing column sourced from eBay AU sold comps.

**Unknown rarities default safe.** If a card has a rarity not in the Rarities sheet, the pipeline defaults to `Holo` with no reverse holo. This prevents spurious reverse holo entries — the risk of creating a variant that doesn't exist is worse than missing one. Unknown rarities are visible in the catalogue and can be corrected by adding to the Rarities sheet.

---

## Scope

**Currently in scope:** Mega Evolution (`me`), Scarlet & Violet (`sv`)

**Deferred:** XY, Sun & Moon, Sword & Shield — the data model supports them fully, they just haven't been registered yet

**Out of scope:** Vintage (Base Set, Jungle, Fossil, etc.) and Pokemon TCG Pocket (digital only)
