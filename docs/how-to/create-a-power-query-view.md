# Create a Power Query view

The `Cards` sheet in `catalogue.xlsx` is a master reference — every card, every field. Power Query lets you create purpose-built views off that master (a listing view, a website export, a pricing sheet) without touching any Python. You choose exactly which columns appear, and the view refreshes automatically when new sets are added.

This guide creates a **Catalogue** view — one row per sellable variant, with the columns relevant for listings.

---

## Step 1 — Open Power Query Editor

Open `catalogue.xlsx` in Excel, then:

1. Go to the **Data** tab
2. Click **Get Data → Launch Power Query Editor**

---

## Step 2 — Create a blank query

In the Power Query Editor:

1. **Home → New Source → Other Sources → Blank Query**
2. Go to **Home → Advanced Editor**
3. Replace everything in the editor with the query below, then click **Done**

```m
let
    Source        = Excel.CurrentWorkbook(){[Name="Cards"]}[Content],

    // Split "Normal | Reverse Holo" into one row per variant
    SplitToList   = Table.TransformColumns(Source, {
                        {"Variants", each Text.Split(_, " | "), type list}
                    }),
    ExpandRows    = Table.ExpandListColumn(SplitToList, "Variants"),
    TrimVariants  = Table.TransformColumns(ExpandRows, {{"Variants", Text.Trim}}),
    RenameVariant = Table.RenameColumns(TrimVariants, {{"Variants", "Variant Label"}}),

    // Derive Finish from Variant Label
    AddFinish     = Table.AddColumn(RenameVariant, "Finish", each
                        if Text.Contains([Variant Label], "Reverse") then "Reverse Holo"
                        else if [Variant Label] = "Holo" or [Variant Label] = "First Edition"
                            then [Variant Label]
                        else "Normal",
                        type text),

    // Derive Variant ID
    AddVariantID  = Table.AddColumn(AddFinish, "Variant ID", each
                        [#"Card ID"] & "-" & Text.Lower(Text.Replace([Variant Label], " ", "-")),
                        type text)
in
    AddVariantID
```

---

## Step 3 — Choose your columns

You now have a table with every field from Cards, expanded to one row per variant. To select the columns you want:

1. **Home → Choose Columns**
2. Tick only the columns you need for this view — for a listings view, a good starting set is:
   - Variant ID, Card ID, Set ID, Local ID, Name
   - Category, Rarity, Variant Label, Finish
   - Image (Large)
   - Price USD (TCGPlayer), Price AUD (Converted)
3. Click **OK**

You can come back and change this selection any time without re-running the Python scripts.

---

## Step 4 — Name and load the query

1. In the **Query Settings** panel on the right, rename the query from `Query1` to `Catalogue`
2. **Home → Close & Load To...**
3. Choose **Table** and select **New worksheet**
4. Click **Load**

Excel creates a new sheet named `Catalogue` containing your view.

---

## Step 5 — Style the table (optional)

The loaded table uses Excel's default table style. To match the look of the Cards sheet:

1. Click inside the Catalogue table
2. Go to **Table Design → Table Styles**
3. If you've created a custom `Soft Indigo` style (matching the Cards sheet colours), select it from the **Custom** section
4. Otherwise, choose any style you like — **Table Style Medium 2** is a clean option

---

## Keeping the view up to date

Whenever you add new sets to the catalogue via the Python pipeline:

1. Open `catalogue.xlsx`
2. **Data → Refresh All**

The Catalogue view (and any other Power Query views) will automatically pick up the new cards.

---

## Creating additional views

Repeat this process for any other views you need — e.g. a pricing sheet that only shows cards with a USD price, or a website export with a different column set. Each view is an independent Power Query query reading from the same `Cards` table.
