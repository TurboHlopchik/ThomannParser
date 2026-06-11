#!/usr/bin/env python3
"""
Step 5: Export products from products.db to MODX MiniShop2 import files.
Generates XML and/or CSV compatible with msImport extra for MODX 3.

Usage:
    python3 5_exporter.py
    python3 5_exporter.py --db products.db --output export/guitars
    python3 5_exporter.py --category "Guitars" --format xml
    python3 5_exporter.py --use-russian          # use translated texts (after step 4)
    python3 5_exporter.py --split-by-category    # one file per top-level category
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

CSV_FIELDS = [
    "pagetitle", "longtitle", "alias", "description", "content",
    "price", "old_price", "article", "image", "gallery",
    "category", "brand", "rating", "reviews_count",
    "availability", "properties", "source_url",
]


def row_to_dict(row: sqlite3.Row, use_russian: bool) -> dict:
    d = dict(row)
    if use_russian:
        d["pagetitle"] = d.get("pagetitle_ru") or d.get("pagetitle") or ""
        d["longtitle"] = d.get("longtitle_ru") or d.get("longtitle") or ""
        d["description"] = d.get("description_ru") or d.get("description") or ""
        d["content"] = d.get("content_ru") or d.get("content") or ""
        d["properties"] = d.get("properties_ru") or d.get("properties") or "{}"
    else:
        d["properties"] = d.get("properties") or "{}"
    d["category"] = d.get("category_path") or d.get("category_name") or ""
    d["source_url"] = d.get("url") or ""
    d["gallery"] = d.get("gallery") or ""
    return d


def export_csv(rows: list, filepath: str, use_russian: bool):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            d = row_to_dict(row, use_russian)
            writer.writerow({field: d.get(field, "") for field in CSV_FIELDS})
    log.info("CSV saved: %s (%d products)", filepath, len(rows))


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
        sub("brand", d.get("brand"))
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
        try:
            props = json.loads(d.get("properties") or "{}")
            for key, val in props.items():
                prop_el = ET.SubElement(props_el, "property")
                prop_el.set("name", str(key))
                prop_el.text = str(val)
        except Exception:
            pass

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
    parser.add_argument("--format", choices=["csv", "xml", "both"], default="both")
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
