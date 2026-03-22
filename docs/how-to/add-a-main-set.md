# Add a main set to the catalogue

Main sets follow standard rarity rules — no manual review required. This is the straightforward path.

---

## 1 — Register the set

Open `data/input/reference.xlsx` and go to the **Sets** sheet. Add a row for the new set:

| Column | Value | Notes |
| --- | --- | --- |
| Set ID | `sv09` | Must match the TCGdex set ID exactly |
| Set Name | `Journey Together` | Human-readable name |
| Series ID | `sv` | Series code (`me`, `sv`, etc.) |
| Series Name | `Scarlet & Violet` | Human-readable series name |
| Set Type | `main` | Use `main` for standard sets |
| In Scope | `Yes` | Set to `Yes` to include in builds |
| Notes | *(optional)* | Anything useful for your own reference |

> **Finding the TCGdex set ID:** Browse [tcgdex.net](https://tcgdex.net) or use `explore-card-schema.py` to look up a known card from the set. The set ID appears in the card ID — e.g. `sv09-001` → set ID is `sv09`.

Save `reference.xlsx` before running the pipeline.

---

## 2 — Run the build

```bash
uv run python scripts/build-catalogue.py --set sv09
```

The pipeline will fetch all card data, determine variants using the Rarities rules, download images, and append the results to `catalogue.xlsx`.

---

## 3 — Refresh Power Query views

If you have Power Query views set up in `catalogue.xlsx`, go to **Data → Refresh All** to pull in the new rows.

---

## Notes

- If the set ID doesn't exist in TCGdex, the pipeline will log an error and skip the set. Double-check the ID.
- If the set's rarities include something not in the Rarities sheet, those cards will default to `Holo` with no reverse holo. Add the new rarity to the Rarities sheet if needed — see the [reference workbook docs](../reference/reference-workbook.md).
- Already-processed sets are skipped automatically on re-runs — no risk of duplicating data.
