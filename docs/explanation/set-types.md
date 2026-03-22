# Set types explained

The pipeline treats sets in one of two ways depending on how their variants work. Understanding this distinction helps when registering new sets and diagnosing unexpected output.

---

## Main sets

Standard sets where variant logic follows predictable rarity rules.

**Examples:** Scarlet & Violet (`sv01`), Destined Rivals (`sv10`), Phantasmal Flames (`me02`)

For each card in a main set, the pipeline:

1. Looks up the card's rarity in the Rarities sheet
2. Determines the base finish (`Normal` or `Holo`) from the rarity
3. Checks whether that rarity can have a Reverse Holo variant
4. Checks TCGdex API flags for whether the specific card actually has a reverse variant in print

The result is a list of variants like `["Normal", "Reverse Holo"]` or `["Holo"]`.

**Rarity → variant mapping (examples):**

| Rarity | Base Finish | Can Reverse Holo |
| --- | --- | --- |
| Common | Normal | Yes |
| Uncommon | Normal | Yes |
| Rare | Holo | Yes |
| Double Rare | Holo | No |
| Ultra Rare | Holo | No |
| Illustration Rare | Holo | No |

The full table lives in `data/input/reference.xlsx` (Rarities sheet) and is read at runtime — nothing is hardcoded.

---

## Special sets

Sets with non-standard variant structures where the reverse holos have specific names, not just "Reverse Holo".

**Examples:** Ascended Heroes (`me02.5`), 151 (`sv03.5`), Prismatic Evolutions (`sv08.5`)

Any set with `.5` in its ID is always a special set.

In special sets, a card's reverse holos might be named:

- `Reverse Holo (Grass Energy)`
- `Reverse Holo (Poké Ball)`
- `Reverse Holo (Friend Ball)`
- `Reverse Holo (Team Rocket)`

These names vary card by card based on the artwork's theme. The TCGdex API only tells us a card *has* a reverse variant — not which named variant it is. The Rarities sheet doesn't help either, because the variant names aren't derived from rarity.

The only way to know is to look at the physical card. This is why special sets require a manual override sheet reviewed by a human.

**How the override sheet works:**

Each card in the special set gets a row in the `VariantOverrides` sheet with an explicit pipe-separated list of variants:

```
Normal|Reverse Holo (Grass Energy)|Reverse Holo (Poké Ball)
```

The pipeline reads this list directly and skips all rarity rules. If a card's row is missing or unsigned, the pipeline stops and reports an error — it won't silently produce incomplete data.

---

## Why not use the same approach for everything?

Main sets and rarity rules handle the vast majority of cards automatically — hundreds of cards per set with no manual work. Special sets are the exception, not the rule. Treating them differently keeps the common case simple while still supporting the edge case correctly.

Forcing manual overrides for every card in every set would be thousands of rows of data entry with no benefit. Forcing rarity rules onto special sets would produce incorrect variant names in the catalogue, which would break listings.

The two-path design is the right trade-off.
