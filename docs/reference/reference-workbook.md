# Reference workbook (`data/input/reference.xlsx`)

The reference workbook is the human-maintained configuration file for the pipeline. It lives in `data/input/` and is committed to the repository. Never delete or move it — the pipeline won't run without it.

If it doesn't exist, run `scripts/create-input-workbook.py` to create it.

---

## Sets sheet

The set registry. The pipeline reads this to know which sets to process.

| Column | Description | Example |
| --- | --- | --- |
| Set ID | TCGdex set identifier | `sv10` |
| Set Name | Human-readable name | `Destined Rivals` |
| Series ID | Series code | `sv` |
| Series Name | Human-readable series name | `Scarlet & Violet` |
| Set Type | `main` or `special` | `main` |
| In Scope | `Yes` to include in builds | `Yes` |
| Notes | Optional free text | `Released May 2025` |

**Set type rules:**
- Any set with `.5` in its ID is always `special` (e.g. `sv03.5`, `me02.5`)
- All other sets are `main` unless manually overridden

---

## Rarities sheet

Defines variant logic for main sets. The pipeline looks up each card's rarity here to determine what variants it gets.

| Column | Description | Example |
| --- | --- | --- |
| Rarity | Rarity string as returned by TCGdex | `Double Rare` |
| Base Finish | The card's base physical finish | `Holo` or `Normal` |
| Can Reverse Holo | Whether this rarity can have a Reverse Holo variant | `Yes` or `No` |
| Notes | Optional context | `Mega Evolution series` |

**Default behaviour:** If a card's rarity isn't found in this sheet, the pipeline defaults to `Base Finish = Holo` and `Can Reverse Holo = No`. This is the safe fallback — it won't create a reverse holo that doesn't exist. If you find a rarity that's being defaulted incorrectly, add it to this sheet.

This sheet is not used for special sets — special sets use VariantOverrides instead.

---

## VariantOverrides sheet

Manual variant definitions for special sets. Each row defines the exact variants for one card in one special set. The pipeline will not process a special set card unless its row is present and signed off.

| Column | Description | Example |
| --- | --- | --- |
| Set ID | The special set | `me02.5` |
| Local ID | Card number within the set | `001` |
| Card Name | Human-readable name (for reference only) | `Erika's Oddish` |
| Variants | Pipe-separated list of variant labels | `Normal\|Reverse Holo (Grass Energy)\|Reverse Holo (Friend Ball)` |
| Reviewed By | Who confirmed this row | `hamdo` |
| Reviewed Date | When it was confirmed | `2026-03-21` |
| Notes | Optional context | `Confirmed via physical card` |

**Sign-off requirement:** Both `Reviewed By` and `Reviewed Date` must be filled in. Rows missing either field are ignored by the pipeline, which means those cards won't appear in the catalogue.

**Populating this sheet:** Use `prep-special-set.py` to generate a draft, then review and sign off manually. See [Add a special set](../how-to/add-a-special-set.md).
