"""
build-catalogue.py

Main pipeline. Reads data/input/reference.xlsx for set configuration,
fetches card data from TCGdex, determines variants per card, and writes
the master catalogue to data/output/catalogue.xlsx. Also downloads one
image per card (shared across all variants).

Usage:
    # Process all in-scope sets
    uv run python scripts/build-catalogue.py

    # Process a single set
    uv run python scripts/build-catalogue.py --set me02.5

    # Dry run — no images downloaded, no file written
    uv run python scripts/build-catalogue.py --dry-run
"""

import requests
import argparse
import os
import re
import time
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

# --- Paths ---
INPUT_PATH  = os.path.join("data", "input", "reference.xlsx")
OUTPUT_PATH = os.path.join("data", "output", "catalogue.xlsx")
IMG_DIR     = os.path.join("data", "output", "images")

# --- APIs ---
TCGDEX_URL      = "https://api.tcgdex.net/v2/en"
FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD&to=AUD"

# --- Styling ---
HEADER_FILL  = PatternFill("solid", start_color="1F4E79")
HEADER_FONT  = Font(bold=True, color="FFFFFF", name="Arial", size=11)
ALT_FILL     = PatternFill("solid", start_color="DCE6F1")
NORMAL_FONT  = Font(name="Arial", size=10)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"    [ERROR] {url}: {e}")
                return None


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")


def download_image(url, filepath, retries=3):
    if os.path.exists(filepath):
        return True
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=20, stream=True)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"    [ERROR] Image download failed: {os.path.basename(filepath)} — {e}")
                return False


def get_usd_to_aud():
    data = fetch(FRANKFURTER_URL)
    if data:
        rate = data.get("rates", {}).get("AUD")
        if rate:
            print(f"  USD->AUD rate: {rate}")
            return rate
    print("  [WARN] Could not fetch exchange rate — price_aud_converted will be empty")
    return None


# ---------------------------------------------------------------------------
# Read input workbook
# ---------------------------------------------------------------------------

def load_sets(wb, target_set_id=None):
    ws = wb["Sets"]
    sets = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        set_id, set_name, series_id, series_name, set_type, in_scope, notes = row
        if in_scope != "Yes":
            continue
        if target_set_id and set_id != target_set_id:
            continue
        sets[set_id] = {
            "set_id": set_id,
            "set_name": set_name,
            "series_id": series_id,
            "series_name": series_name,
            "set_type": set_type,
        }
    return sets


def load_rarities(wb):
    ws = wb["Rarities"]
    rarities = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        rarity, base_finish, can_reverse, *_ = row
        rarities[rarity] = {
            "base_finish": base_finish,
            "can_reverse_holo": (can_reverse == "Yes"),
        }
    return rarities


def load_overrides(wb):
    ws = wb["VariantOverrides"]
    overrides = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        set_id, local_id, card_name, variants_str, reviewed_by, reviewed_date, notes = row
        if not reviewed_by or not reviewed_date:
            continue  # unreviewed rows are ignored
        key = (set_id, str(local_id))
        overrides[key] = [v.strip() for v in variants_str.split("|") if v.strip()]
    return overrides


# ---------------------------------------------------------------------------
# Variant logic
# ---------------------------------------------------------------------------

def get_variants_for_card(card, set_info, rarities, overrides):
    """
    Returns a list of variant label strings for this card.

    Special sets: use override sheet (must be reviewed).
    Main sets: apply rarity rules; unknown rarity defaults to no reverse holo.
    """
    set_id   = set_info["set_id"]
    set_type = set_info["set_type"]
    local_id = card.get("localId", "")
    rarity   = card.get("rarity", "") or ""
    tcg_vars = card.get("variants", {})

    if set_type == "special":
        key = (set_id, local_id)
        if key not in overrides:
            raise ValueError(
                f"Special set {set_id} card {local_id} has no reviewed override entry. "
                f"Run prep-special-set.py and complete the VariantOverrides sheet first."
            )
        return overrides[key]

    # Main set — apply rarity rules
    rarity_rule = rarities.get(rarity, {"base_finish": "Holo", "can_reverse_holo": False})
    base_finish = rarity_rule["base_finish"]   # "Normal" or "Holo"
    can_reverse = rarity_rule["can_reverse_holo"]

    variants = [base_finish]

    if tcg_vars.get("firstEdition"):
        variants.append("First Edition")
    if tcg_vars.get("wPromo"):
        variants.append("Promo")
    if can_reverse and tcg_vars.get("reverse"):
        variants.append("Reverse Holo")

    return variants


# ---------------------------------------------------------------------------
# Excel output
# ---------------------------------------------------------------------------

def setup_workbook():
    wb = Workbook()
    wb.remove(wb.active)

    # --- Sets sheet ---
    ws_sets = wb.create_sheet("Sets")
    sets_headers = ["Set ID", "Set Name", "Series ID", "Series Name", "Set Type",
                    "Total Cards", "Release Date"]
    _write_header(ws_sets, sets_headers, [14, 28, 12, 20, 12, 14, 14])

    # --- Cards sheet ---
    ws_cards = wb.create_sheet("Cards")
    cards_headers = ["Card ID", "Set ID", "Local ID", "Name", "Rarity",
                     "HP", "Types", "Stage", "Illustrator", "Regulation Mark",
                     "Image API", "Image Custom"]
    _write_header(ws_cards, cards_headers, [18, 12, 10, 28, 26, 6, 14, 14, 24, 16, 50, 20])

    # --- Variants sheet ---
    ws_variants = wb.create_sheet("Variants")
    variants_headers = ["Variant ID", "Card ID", "Set ID", "Local ID", "Card Name",
                        "Variant Label", "Finish", "Image API", "Image Custom",
                        "Price USD (TCGPlayer)", "Price AUD (Converted)", "Price AUD (eBay)"]
    _write_header(ws_variants, variants_headers,
                  [28, 18, 12, 10, 28, 30, 14, 50, 20, 20, 20, 18])

    return wb, ws_sets, ws_cards, ws_variants


def _write_header(ws, headers, col_widths):
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 20
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    ws.freeze_panes = "A2"


def _style_row(ws, row_num, values):
    fill = ALT_FILL if row_num % 2 == 0 else None
    for col, val in enumerate(values, 1):
        cell = ws.cell(row=row_num, column=col, value=val)
        cell.font = NORMAL_FONT
        cell.alignment = Alignment(vertical="center")
        if fill:
            cell.fill = fill


def write_set_row(ws, row_num, set_info, total_cards, release_date):
    _style_row(ws, row_num, [
        set_info["set_id"], set_info["set_name"],
        set_info["series_id"], set_info["series_name"],
        set_info["set_type"], total_cards, release_date,
    ])


def write_card_row(ws, row_num, card, set_id):
    card_id   = card.get("id", "")
    local_id  = card.get("localId", "")
    types     = ", ".join(card.get("types") or [])
    image_api = card.get("image", "")
    _style_row(ws, row_num, [
        card_id, set_id, local_id,
        card.get("name", ""), card.get("rarity", ""),
        card.get("hp"), types,
        card.get("stage", ""), card.get("illustrator", ""),
        card.get("regulationMark", ""),
        image_api, "",  # image_custom empty
    ])


def write_variant_row(ws, row_num, card, set_id, variant_label, image_api, usd_price, aud_rate):
    card_id  = card.get("id", "")
    local_id = card.get("localId", "")
    name     = card.get("name", "")

    # Normalise finish from label
    if "Reverse" in variant_label:
        finish = "Reverse Holo"
    elif variant_label in ("Holo", "First Edition"):
        finish = variant_label
    else:
        finish = "Normal"

    variant_id  = f"{card_id}-{sanitize_filename(variant_label).lower()}"
    aud_price   = round(usd_price * aud_rate, 2) if usd_price and aud_rate else ""

    _style_row(ws, row_num, [
        variant_id, card_id, set_id, local_id, name,
        variant_label, finish,
        image_api, "",       # image_custom empty
        usd_price if usd_price else "",
        aud_price,
        "",                  # price_aud_ebay — Phase 2
    ])


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def process_set(set_info, rarities, overrides, ws_sets, ws_cards, ws_variants,
                sets_row, cards_row, variants_row, usd_to_aud, dry_run):

    set_id   = set_info["set_id"]
    set_name = set_info["set_name"]
    set_type = set_info["set_type"]

    print(f"\n{'='*60}")
    print(f"  {set_name} ({set_id}) [{set_type}]")
    print(f"{'='*60}")

    # Validate special sets have overrides before fetching anything
    if set_type == "special":
        set_override_keys = [k for k in overrides if k[0] == set_id]
        if not set_override_keys:
            print(f"  [SKIP] Special set {set_id} has no reviewed VariantOverrides entries.")
            print(f"         Run prep-special-set.py and complete the override sheet first.")
            return sets_row, cards_row, variants_row

    # Fetch set metadata
    set_data = fetch(f"{TCGDEX_URL}/sets/{set_id}")
    if not set_data:
        print(f"  [ERROR] Could not fetch set data.")
        return sets_row, cards_row, variants_row

    card_stubs   = set_data.get("cards", [])
    release_date = set_data.get("releaseDate", "")
    total_cards  = len(card_stubs)

    print(f"  {total_cards} cards | Released: {release_date}")

    if not dry_run:
        write_set_row(ws_sets, sets_row, set_info, total_cards, release_date)
    sets_row += 1

    errors = []

    for i, stub in enumerate(card_stubs, 1):
        local_id = stub.get("localId", "")
        card_name = stub.get("name", local_id)

        print(f"  [{i}/{total_cards}] {card_name} ({set_id}-{local_id})", end="")

        card = fetch(f"{TCGDEX_URL}/sets/{set_id}/{local_id}")
        if not card:
            print(f" [ERROR]")
            errors.append(f"{set_id}/{local_id}")
            continue

        # Determine variants
        try:
            variant_labels = get_variants_for_card(card, set_info, rarities, overrides)
        except ValueError as e:
            print(f" [ERROR] {e}")
            errors.append(f"{set_id}/{local_id}")
            continue

        print(f" -> {', '.join(variant_labels)}")

        # Image: download once per card, reuse path for all variants
        image_base = card.get("image", "")
        image_path = ""
        if image_base and not dry_run:
            filename = sanitize_filename(f"{set_id}_{local_id}") + ".jpg"
            filepath = os.path.join(IMG_DIR, filename)
            if download_image(f"{image_base}/high.jpg", filepath):
                image_path = filepath

        # TCGPlayer USD price (normal variant price as reference)
        usd_price = None
        pricing = card.get("pricing", {}).get("tcgplayer", {})
        normal_pricing = pricing.get("normal", {})
        if normal_pricing:
            usd_price = normal_pricing.get("marketPrice") or normal_pricing.get("midPrice")

        if not dry_run:
            write_card_row(ws_cards, cards_row, card, set_id)
        cards_row += 1

        for label in variant_labels:
            if not dry_run:
                write_variant_row(ws_variants, variants_row, card, set_id,
                                  label, image_base, usd_price, usd_to_aud)
            variants_row += 1

        time.sleep(0.05)

    print(f"\n  Done: {total_cards} cards processed, {len(errors)} errors")
    if errors:
        for e in errors:
            print(f"    - {e}")

    return sets_row, cards_row, variants_row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", default=None, help="Process a single set ID only")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and print without writing output files")
    args = parser.parse_args()

    if not os.path.exists(INPUT_PATH):
        print(f"Input workbook not found: {INPUT_PATH}")
        print("Run scripts/create-input-workbook.py first.")
        return

    print("Loading reference workbook...")
    ref_wb   = load_workbook(INPUT_PATH)
    sets     = load_sets(ref_wb, target_set_id=args.set)
    rarities = load_rarities(ref_wb)
    overrides = load_overrides(ref_wb)

    if not sets:
        msg = f"Set '{args.set}' not found or not in scope." if args.set else "No in-scope sets found."
        print(msg)
        return

    print(f"  {len(sets)} set(s) to process")
    print(f"  {len(rarities)} rarities loaded")
    print(f"  {len(overrides)} override entries loaded")

    print("\nFetching USD->AUD exchange rate...")
    usd_to_aud = get_usd_to_aud()

    dry_run = args.dry_run
    if not dry_run:
        os.makedirs(IMG_DIR, exist_ok=True)
        os.makedirs(os.path.join("data", "output"), exist_ok=True)
        wb, ws_sets, ws_cards, ws_variants = setup_workbook()
    else:
        wb = ws_sets = ws_cards = ws_variants = None
        print("  [DRY RUN] No files will be written.")

    sets_row = cards_row = variants_row = 2

    for set_info in sets.values():
        sets_row, cards_row, variants_row = process_set(
            set_info, rarities, overrides,
            ws_sets, ws_cards, ws_variants,
            sets_row, cards_row, variants_row,
            usd_to_aud, dry_run,
        )

    if not dry_run:
        wb.save(OUTPUT_PATH)
        print(f"\n{'='*60}")
        print(f"Catalogue saved: {OUTPUT_PATH}")
        print(f"  Sets:     {sets_row - 2}")
        print(f"  Cards:    {cards_row - 2}")
        print(f"  Variants: {variants_row - 2}")
        print(f"  Images:   {IMG_DIR}/")


if __name__ == "__main__":
    main()
