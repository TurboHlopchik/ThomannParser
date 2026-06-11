#!/usr/bin/env python3
"""
Step 6 (optional): Monitor Thomann for new products and sync to MODX automatically.

How it works:
1. Periodically re-runs URL collection on specified categories
2. Detects new URLs not yet in products.db
3. Scrapes new products
4. Translates them
5. Exports a "delta" XML file
6. Pushes to MODX via REST API (using modAuth + msImport endpoint)

Usage:
    # Run once (detect + scrape + translate + export new products)
    python3 6_sync_monitor.py --once \
        --engine deepl --api-key YOUR_KEY \
        --modx-url https://yoursite.com --modx-key YOUR_MODX_API_KEY

    # Run on a schedule (every 24h)
    python3 6_sync_monitor.py --interval 24 \
        --engine deepl --api-key YOUR_KEY \
        --modx-url https://yoursite.com --modx-key YOUR_MODX_API_KEY

    # Dry run (detect new products only, no scraping/import)
    python3 6_sync_monitor.py --dry-run

Schedule via cron (recommended instead of --interval):
    # crontab -e
    0 3 * * * cd /path/to/parser && ./venv/bin/python3 6_sync_monitor.py --once ...
"""

import argparse
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sync_monitor.log"),
    ],
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

BASE_URL = "https://www.thomann.de"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_session(proxy: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    try:
        resp = session.get(BASE_URL + "/intl/", timeout=20)
        if resp.status_code == 200:
            log.info("Session warmed up")
        time.sleep(1)
    except Exception as e:
        log.warning("Warmup failed: %s", e)
    return session


def fetch(session: requests.Session, url: str, delay: float = 2.0) -> Optional[BeautifulSoup]:
    time.sleep(delay)
    try:
        resp = session.get(url, timeout=25)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        if resp.status_code == 403 and resp.headers.get("x-deny-reason") == "host_not_allowed":
            log.error("IP blocked.")
            return None
        log.warning("HTTP %s: %s", resp.status_code, url)
        return None
    except Exception as e:
        log.error("Fetch error: %s | %s", url, e)
        return None


# ─── New product detection ────────────────────────────────────────────────────

def get_known_urls(conn: sqlite3.Connection) -> set:
    rows = conn.execute("SELECT url FROM products").fetchall()
    return {r[0] for r in rows}


def scan_category_for_new_urls(
    session: requests.Session,
    cat_url: str,
    known_urls: set,
    delay: float = 2.0,
    max_pages: int = 5,
) -> list:
    """
    Scan first N pages of a category for URLs not in known_urls.
    Stop early if no new URLs found on a page (product order is stable on Thomann).
    """
    new_urls = []
    current_url = cat_url
    page = 1

    while page <= max_pages:
        soup = fetch(session, current_url, delay)
        if not soup:
            break

        page_urls = []
        for a in soup.select("a.product__link, a[class*='product-link'], article a[href*='.htm']"):
            href = a.get("href", "")
            if ".htm" in href:
                full = (BASE_URL + href if href.startswith("/") else href).split("?")[0]
                page_urls.append(full)

        found_on_page = [u for u in page_urls if u not in known_urls]
        new_urls.extend(found_on_page)

        log.info("  Page %d: %d total, %d new", page, len(page_urls), len(found_on_page))

        # If no new URLs on this page, stop scanning (products are sorted by date added)
        if not found_on_page:
            break

        next_el = soup.select_one("a[rel='next']")
        if not next_el:
            break
        next_href = next_el.get("href", "")
        if not next_href:
            break
        current_url = BASE_URL + next_href if next_href.startswith("/") else next_href
        page += 1

    return new_urls


def detect_new_products(
    session: requests.Session,
    conn: sqlite3.Connection,
    categories_json: str,
    category_filter: Optional[str],
    delay: float,
) -> list:
    """Check all leaf categories for new product URLs. Returns list of new URL+category dicts."""
    with open(categories_json, encoding="utf-8") as f:
        data = json.load(f)
    tree = data.get("tree", data) if isinstance(data, dict) else data

    if category_filter:
        tree = [c for c in tree if category_filter.lower() in c["name"].lower()]

    known_urls = get_known_urls(conn)
    log.info("Known products in DB: %d", len(known_urls))

    new_items = []

    def walk(cats, parent_path=""):
        for cat in cats:
            path = f"{parent_path} > {cat['name']}" if parent_path else cat["name"]
            subcats = cat.get("subcategories", [])
            if subcats:
                walk(subcats, path)
            else:
                log.info("Scanning: %s", path)
                new_urls = scan_category_for_new_urls(
                    session, cat["url"], known_urls, delay
                )
                for url in new_urls:
                    new_items.append({
                        "url": url,
                        "category_id": cat["id"],
                        "category_name": cat["name"],
                        "category_path": path,
                    })
                    known_urls.add(url)  # avoid duplicates across categories

    walk(tree)
    log.info("Total new products detected: %d", len(new_items))
    return new_items


def insert_new_urls(conn: sqlite3.Connection, new_items: list):
    for item in new_items:
        article = ""
        m = re.search(r"_(\d{6,})\.htm", item["url"])
        if m:
            article = m.group(1)
        conn.execute(
            "INSERT OR IGNORE INTO products (url, article, category_id, category_name, category_path, status) VALUES (?,?,?,?,?,'pending')",
            (item["url"], article, item["category_id"], item["category_name"], item["category_path"]),
        )
    conn.commit()
    log.info("Inserted %d new product URLs into DB", len(new_items))


# ─── MODX REST import ─────────────────────────────────────────────────────────

def push_to_modx(xml_filepath: str, modx_url: str, modx_api_key: str) -> bool:
    """
    Push export XML to MODX via msImport REST endpoint.

    Requires msImport extra with API endpoint enabled.
    Set up in MODX: System Settings → msimport.api_key = YOUR_KEY

    The endpoint: POST /assets/components/msimport/import.php
    """
    endpoint = modx_url.rstrip("/") + "/assets/components/msimport/import.php"
    log.info("Pushing to MODX: %s", endpoint)

    try:
        with open(xml_filepath, "rb") as f:
            resp = requests.post(
                endpoint,
                files={"file": (os.path.basename(xml_filepath), f, "application/xml")},
                data={"api_key": modx_api_key, "format": "xml"},
                timeout=120,
            )
        if resp.status_code == 200:
            result = resp.json()
            if result.get("success"):
                log.info("MODX import successful: %s", result)
                return True
            else:
                log.error("MODX import failed: %s", result)
                return False
        else:
            log.error("MODX HTTP %s: %s", resp.status_code, resp.text[:300])
            return False
    except Exception as e:
        log.error("MODX push error: %s", e)
        return False


# ─── Run pipeline steps via subprocess ────────────────────────────────────────

def run_step(script: str, args: list) -> bool:
    python = sys.executable
    cmd = [python, script] + args
    log.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        log.error("Step failed: %s", script)
        return False
    return True


# ─── Main sync loop ───────────────────────────────────────────────────────────

def sync_once(args):
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA journal_mode=WAL")

    session = get_session(args.proxy)

    # 1. Detect new products
    new_items = detect_new_products(
        session, conn, args.categories, args.category_filter, args.delay
    )

    if not new_items:
        log.info("No new products found.")
        conn.close()
        return

    if args.dry_run:
        log.info("Dry run — stopping before scrape/import. New URLs found:")
        for item in new_items[:20]:
            log.info("  %s | %s", item["category_path"], item["url"])
        if len(new_items) > 20:
            log.info("  ... and %d more", len(new_items) - 20)
        conn.close()
        return

    # 2. Insert new URLs to DB
    insert_new_urls(conn, new_items)
    conn.close()

    # 3. Scrape new products
    scrape_args = ["--db", args.db, "--delay", str(args.delay)]
    if args.category_filter:
        scrape_args += ["--category", args.category_filter]
    if not run_step("3_product_scraper.py", scrape_args):
        log.error("Scraping failed")
        return

    # 4. Translate
    if args.engine and args.api_key:
        translate_args = ["--db", args.db, "--engine", args.engine, "--api-key", args.api_key]
        if args.category_filter:
            translate_args += ["--category", args.category_filter]
        if not run_step("4_translator.py", translate_args):
            log.warning("Translation failed — exporting untranslated")

    # 5. Export delta (new products only)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    delta_path = f"export/delta_{timestamp}"
    os.makedirs("export", exist_ok=True)

    export_args = [
        "--db", args.db,
        "--output", delta_path,
        "--format", "xml",
        "--status", "translated" if args.engine else "scraped",
    ]
    if args.use_russian:
        export_args.append("--use-russian")
    if not run_step("5_exporter.py", export_args):
        log.error("Export failed")
        return

    xml_file = delta_path + ".xml"

    # 6. Push to MODX (optional)
    if args.modx_url and args.modx_key:
        success = push_to_modx(xml_file, args.modx_url, args.modx_key)
        if success:
            # Archive the delta file
            archive_dir = "export/archive"
            os.makedirs(archive_dir, exist_ok=True)
            shutil.move(xml_file, f"{archive_dir}/delta_{timestamp}.xml")
            log.info("Delta archived.")
    else:
        log.info("MODX push skipped (no --modx-url/--modx-key). Export at: %s", xml_file)

    log.info("Sync complete. %d new products processed.", len(new_items))


def main():
    parser = argparse.ArgumentParser(description="Monitor Thomann for new products and sync to MODX")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--categories", default="categories.json")
    parser.add_argument("--category-filter", default=None)

    # Run mode
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=float, default=24.0, help="Repeat interval in hours")
    parser.add_argument("--dry-run", action="store_true", help="Detect only, no scraping/import")

    # Translation
    parser.add_argument("--engine", choices=["deepl", "claude", "google"], default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--use-russian", action="store_true")

    # MODX
    parser.add_argument("--modx-url", default=None, help="MODX site URL")
    parser.add_argument("--modx-key", default=None, help="msImport API key")

    # Network
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--delay", type=float, default=2.0)

    args = parser.parse_args()

    if args.once or args.dry_run:
        sync_once(args)
    else:
        log.info("Running on %.0f-hour interval. Press Ctrl+C to stop.", args.interval)
        while True:
            try:
                log.info("=== Sync started at %s ===", datetime.now().isoformat())
                sync_once(args)
                log.info("=== Next sync in %.0f hours ===", args.interval)
                time.sleep(args.interval * 3600)
            except KeyboardInterrupt:
                log.info("Stopped by user.")
                break
            except Exception as e:
                log.error("Sync error: %s — retrying in 1 hour", e)
                time.sleep(3600)


if __name__ == "__main__":
    main()
