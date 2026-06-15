#!/usr/bin/env python3
"""
Step 5: Export products from products.db to MODX MiniShop3 import files.

Default output is CSV for ImpEx3 (modstore.pro) / the built-in MiniShop3 CSV
importer on MODX 3. Product specs are emitted as `option.<key>` columns so they
become filterable MiniShop3 options; gallery uses the "||" multi-value separator
and brand maps to `vendor`. The legacy XML output (--format xml) is kept for the
old MiniShop2/msImportExport flow and is not used by ImpEx3.

Usage:
    python3 5_exporter.py
    python3 5_exporter.py --db products.db --output export/guitars
    python3 5_exporter.py --split-by-category    # one file per top-level category
    python3 5_exporter.py --use-russian          # use translated texts (after step 4)
"""

import argparse
import csv
import json
import logging
import os
import re
import sqlite3
from xml.dom import minidom
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Base columns mapped to MiniShop3 / ImpEx3 import fields.
# Product options are added dynamically as `option.<slug>` columns (see export_csv).
# Field names follow MiniShop3 core/components/minishop3/config/import-fields.php:
#   gallery -> multiple images via "||"; vendor -> brand; category path -> resource tree.
CSV_BASE_FIELDS = [
    "pagetitle", "longtitle", "alias", "description", "content",
    "price", "old_price", "article", "image", "gallery",
    "category", "vendor", "rating", "reviews_count",
    "availability", "source_url",
]

# MiniShop3/ImpEx3 separator for multi-value cells (gallery, multi-options).
MULTI_SEP = "||"


def slugify_option_key(key: str) -> str:
    """Stable latin-ish option key for the `option.<key>` column header.

    The option key is the system identifier / frontend placeholder in MiniShop3,
    so it must stay consistent across the whole catalogue (same spec -> same key).
    """
    s = key.strip().lower()
    s = re.sub(r"[^\w]+", "_", s, flags=re.UNICODE)
    return s.strip("_")[:64]


def parse_props(raw: str) -> dict:
    try:
        props = json.loads(raw or "{}")
        return props if isinstance(props, dict) else {}
    except Exception:
        return {}


def row_to_dict(row: sqlite3.Row, use_russian: bool) -> dict:
    d = dict(row)
    if use_russian:
        d["pagetitle"] = d.get("pagetitle_ru") or d.get("pagetitle") or ""
        d["longtitle"] = d.get("longtitle_ru") or d.get("longtitle") or ""
        d["description"] = d.get("description_ru") or d.get("description") or ""
        d["content"] = d.get("content_ru") or d.get("content") or ""
    # Options: keep English keys for stable `option.<key>` headers, but use
    # translated values (zipped by position) when a Russian properties set exists.
    en_props = parse_props(d.get("properties"))
    if use_russian:
        ru_props = parse_props(d.get("properties_ru"))
        ru_values = list(ru_props.values())
        options = {}
        for i, (k, v) in enumerate(en_props.items()):
            options[k] = ru_values[i] if i < len(ru_values) else v
        d["_options"] = options
    else:
        d["_options"] = en_props
    d["vendor"] = d.get("brand") or ""
    d["category"] = d.get("category_path") or d.get("category_name") or ""
    d["source_url"] = d.get("url") or ""
    d["gallery"] = d.get("gallery") or ""
    return d


def export_csv(rows: list, filepath: str, use_russian: bool):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    dicts = [row_to_dict(r, use_russian) for r in rows]

    # Collect the union of option keys for this file (first-seen order preserved),
    # then map each to a `option.<slug>` column header for ImpEx3 / MiniShop3.
    option_keys, header_for = [], {}
    for d in dicts:
        for key in d["_options"]:
            if key not in header_for:
                header_for[key] = "option." + slugify_option_key(key)
                option_keys.append(key)
    option_columns = [header_for[k] for k in option_keys]
    fieldnames = CSV_BASE_FIELDS + option_columns

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for d in dicts:
            record = {field: d.get(field, "") for field in CSV_BASE_FIELDS}
            for key, value in d["_options"].items():
                record[header_for[key]] = value
            writer.writerow(record)
    log.info("CSV saved: %s (%d products, %d option columns)",
             filepath, len(rows), len(option_columns))


def export_xml(rows: list, filepath: str, use_russian: bool):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    root = ET.Element("products")

    for row in rows:
        d = row_to_dict(row, use_russian)
        item = ET.SubElement(root, "product")

        def sub(tag, text):
            el = ET.SubElement(item, tag)
            el.text = str(text) if text else ""

        sub("pagetitle", d.get("pagetitle"))
        sub("longtitle", d.get("longtitle"))
        sub("alias", d.get("alias"))
        sub("description", d.get("description"))
        sub("content", d.get("content"))
        sub("price", d.get("price"))
        sub("old_price", d.get("old_price"))
        sub("article", d.get("article"))
        sub("image", d.get("image"))
        sub("brand", d.get("vendor"))
        sub("rating", d.get("rating"))
        sub("reviews_count", d.get("reviews_count"))
        sub("availability", d.get("availability"))
        sub("category", d.get("category"))
        sub("source_url", d.get("source_url"))

        # Gallery
        gallery_el = ET.SubElement(item, "gallery")
        for img_url in (d.get("gallery") or "").split("||"):
            if img_url.strip():
                ET.SubElement(gallery_el, "image").text = img_url.strip()

        # Properties
        props_el = ET.SubElement(item, "properties")
        for key, val in d.get("_options", {}).items():
            prop_el = ET.SubElement(props_el, "property")
            prop_el.set("name", str(key))
            prop_el.text = str(val)

    xml_str = minidom.parseString(
        ET.tostring(root, encoding="unicode")
    ).toprettyxml(indent="  ", encoding=None)
    lines = xml_str.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info("XML saved: %s (%d products)", filepath, len(rows))


def export_category_tree_xml(conn: sqlite3.Connection, filepath: str):
    """
    Export category structure as a separate XML for creating MODX resource tree.
    """
    rows = conn.execute("""
        SELECT DISTINCT category_id, category_name, category_path
        FROM products
        WHERE status IN ('scraped', 'translated')
        ORDER BY category_path
    """).fetchall()

    root = ET.Element("categories")
    for row in rows:
        cat_el = ET.SubElement(root, "category")
        cat_el.set("id", row[0] or "")
        cat_el.set("name", row[1] or "")
        cat_el.set("path", row[2] or "")

        # Build alias from path
        parts = [p.strip() for p in (row[2] or "").split(">")]
        alias = "-".join(re.sub(r"[^\w]", "-", p.lower()) for p in parts)
        alias = re.sub(r"-+", "-", alias).strip("-")
        cat_el.set("alias", alias[:100])

    xml_str = minidom.parseString(
        ET.tostring(root, encoding="unicode")
    ).toprettyxml(indent="  ", encoding=None)

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_str)
    log.info("Category tree saved: %s (%d categories)", filepath, len(rows))


def main():
    parser = argparse.ArgumentParser(description="Export products.db → MODX MiniShop2 import files")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--output", default="export/thomann", help="Output path base (without extension)")
    parser.add_argument("--format", choices=["csv", "xml", "both"], default="csv")
    parser.add_argument("--category", default=None, help="Filter by category name")
    parser.add_argument("--use-russian", action="store_true", help="Use translated Russian texts")
    parser.add_argument("--split-by-category", action="store_true", help="One file per top-level category")
    parser.add_argument("--status", default="scraped", help="Product status to export (scraped/translated)")
    parser.add_argument("--export-categories", action="store_true", help="Also export category tree XML")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    if args.export_categories:
        export_category_tree_xml(conn, os.path.dirname(args.output) + "/categories.xml")

    if args.split_by_category:
        # Get distinct top-level categories
        top_cats = conn.execute("""
            SELECT DISTINCT
                CASE WHEN instr(category_path, ' > ') > 0
                     THEN substr(category_path, 1, instr(category_path, ' > ') - 1)
                     ELSE category_path
                END as top_cat
            FROM products
            WHERE status = ?
            ORDER BY top_cat
        """, (args.status,)).fetchall()

        for (top_cat,) in top_cats:
            rows = conn.execute("""
                SELECT * FROM products
                WHERE status = ? AND category_path LIKE ?
                ORDER BY category_path, id
            """, (args.status, f"{top_cat}%")).fetchall()

            slug = re.sub(r"[^\w]", "_", top_cat.lower()).strip("_")
            base = f"{args.output}_{slug}"

            if args.format in ("csv", "both"):
                export_csv(rows, base + ".csv", args.use_russian)
            if args.format in ("xml", "both"):
                export_xml(rows, base + ".xml", args.use_russian)
    else:
        query = "SELECT * FROM products WHERE status = ?"
        params = [args.status]
        if args.category:
            query += " AND category_path LIKE ?"
            params.append(f"%{args.category}%")
        query += " ORDER BY category_path, id"

        rows = conn.execute(query, params).fetchall()
        log.info("Exporting %d products", len(rows))

        if args.format in ("csv", "both"):
            export_csv(rows, args.output + ".csv", args.use_russian)
        if args.format in ("xml", "both"):
            export_xml(rows, args.output + ".xml", args.use_russian)

    conn.close()
    log.info("Export complete.")


if __name__ == "__main__":
    main()
