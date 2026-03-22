# Create the Listing view in ebay.xlsx

The Listing view joins the master catalogue with your stock quantities. It shows one row per in-stock card variant — exactly what you need to generate an eBay CSV export.

**Prerequisites:** `ebay.xlsx` exists with a Stock sheet (run `build-stock-sheet.py` first).

---

## Step 1 — Open the Power Query editor

In `ebay.xlsx`:

1. **Data → Get Data → Launch Power Query Editor**

---

## Step 2 — Add the Listing query

1. In the Power Query editor: **Home → New Source → Blank Query**
2. **Home → Advanced Editor**
3. Paste the query below, replacing the `CataloguePath` value with the actual path to your `catalogue.xlsx`
4. Click **Done**, then rename the query to `Listing`

```m
let
    // -----------------------------------------------------------------------
    // Update this path if you move catalogue.xlsx
    // -----------------------------------------------------------------------
    CataloguePath = "C:\Dev\pokemon-listings\data\output\catalogue.xlsx",

    // -----------------------------------------------------------------------
    // Load Cards table from catalogue.xlsx
    // -----------------------------------------------------------------------
    CatalogueFile = Excel.Workbook(File.Contents(CataloguePath), null, true),
    CardsTable    = CatalogueFile{[Item="Cards", Kind="Table"]}[Data],

    // -----------------------------------------------------------------------
    // Expand pipe-separated Variants into one row per variant
    // -----------------------------------------------------------------------
    SplitToList   = Table.TransformColumns(CardsTable, {
                        {"Variants", each Text.Split(_, " | "), type list}
                    }),
    ExpandRows    = Table.ExpandListColumn(SplitToList, "Variants"),
    TrimVariants  = Table.TransformColumns(ExpandRows, {{"Variants", Text.Trim}}),
    RenameVariant = Table.RenameColumns(TrimVariants, {{"Variants", "Variant Label"}}),

    // -----------------------------------------------------------------------
    // Derive Variant ID — must match the ID column in the Stock sheet
    // -----------------------------------------------------------------------
    AddVariantID  = Table.AddColumn(RenameVariant, "Variant ID", each
                        [#"Card ID"] & "-" & Text.Lower(Text.Replace([Variant Label], " ", "-")),
                        type text),

    // -----------------------------------------------------------------------
    // Join to Stock sheet for Qty
    // -----------------------------------------------------------------------
    StockTable    = Excel.CurrentWorkbook(){[Name="Stock"]}[Content],
    StockQty      = Table.SelectColumns(StockTable, {"Variant ID", "Qty"}),
    StockTyped    = Table.TransformColumnTypes(StockQty, {{"Qty", Int64.Type}}),

    Joined        = Table.NestedJoin(
                        AddVariantID, {"Variant ID"},
                        StockTyped,   {"Variant ID"},
                        "StockData",  JoinKind.Left
                    ),
    WithQty       = Table.ExpandTableColumn(Joined, "StockData", {"Qty"}),

    // -----------------------------------------------------------------------
    // Only show in-stock rows (Qty >= 1)
    // Remove this step if you want to see all rows including out-of-stock
    // -----------------------------------------------------------------------
    InStock       = Table.SelectRows(WithQty, each [Qty] <> null and [Qty] >= 1)

in
    InStock
```

---

## Step 3 — Load to sheet

1. **Home → Close & Load To…**
2. Choose **Table** and **New worksheet**
3. Rename the sheet `Listing`

---

## Refreshing

When you update quantities in the Stock sheet, or when new sets are added to the catalogue:

**Data → Refresh All**

The Listing view will reflect the updated stock automatically.

---

## Exporting to CSV for eBay

Once the Listing view looks correct:

1. Run `uv run python scripts/export-ebay-csv.py --set me02.5` *(not yet built)*
2. This reads `ebay.xlsx` directly and generates the eBay upload CSV

Or manually: select the Listing sheet → **File → Save a Copy → CSV** for a quick one-off export.
