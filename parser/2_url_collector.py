#!/usr/bin/env python3
"""
Step 2: Collect all product URLs from category pages.
Reads categories.json, paginates through each leaf category,
saves product URLs with their category path to products.db (SQLite).

Usage:
    python3 2_url_collector.py
    python3 2_url_collector.py --categories categories.json --db products.db
    python3 2_url_collector.py --category-filter "Guitars"   # only one top-level cat
    python3 2_url_collector.py --resume                       # skip already-done categories

Run can be interrupted and resumed with --resume.
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

BASE_URL = "https://www.thomann.de"


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            article TEXT,
            category_id TEXT,
            category_name TEXT,
            category_path TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories_done (
            category_id TEXT PRIMARY KEY,
            url TEXT,
            products_found INTEGER,
            done_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON products(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category_id)")
    conn.commit()
    return conn


def get_session(proxy: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    try:
        resp = session.get(BASE_URL + "/intl/", timeout=20)
        if resp.status_code == 200:
            log.info("Session warmed up (cookies: %d)", len(session.cookies))
        time.sleep(1)
    except Exception as e:
        log.warning("Warmup failed: %s", e)
    return session


def fetch(session: requests.Session, url: str, delay: float = 1.5) -> Optional[BeautifulSoup]:
    time.sleep(delay)
    try:
        session.headers["Referer"] = BASE_URL + "/intl/"
        resp = session.get(url, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        if resp.status_code == 403:
            if resp.headers.get("x-deny-reason") == "host_not_allowed":
                log.error("IP blocked. Use --proxy with residential proxy.")
                sys.exit(1)
        log.warning("HTTP %s: %s", resp.status_code, url)
        return None
    except Exception as e:
        log.error("Error fetching %s: %s", url, e)
        return None


def extract_product_urls(soup: BeautifulSoup, base_url: str) -> list:
    """Extract product page URLs from a category listing page."""
    urls = []
    seen = set()

    selectors = [
        "a.product__link",
        "a[class*='product-link']",
        "a[class*='product__link']",
        ".product-list__item a[href*='.htm']",
        "article a[href*='.htm']",
        ".fx-product-thumb a[href*='.htm']",
        "a[data-product]",
    ]

    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href", "")
            if not href or ".htm" not in href:
                continue
            full = urljoin(base_url, href).split("?")[0]
            if full not in seen and "thomann.de" in full:
                seen.add(full)
                urls.append(full)
        if urls:
            break

    # Fallback: any .htm link that looks like a product (has numeric ID in URL)
    if not urls:
        for a in soup.select("a[href*='.htm']"):
            href = a.get("href", "")
            full = urljoin(base_url, href).split("?")[0]
            if re.search(r"\d{5,}", full) and full not in seen:
                seen.add(full)
                urls.append(full)

    return urls


def get_total_pages(soup: BeautifulSoup) -> int:
    """Detect total number of pages in pagination."""
    # Look for last page number
    pagination = soup.select(".pagination a, [class*='pagination'] a, [aria-label*='page' i]")
    max_page = 1
    for el in pagination:
        text = el.get_text(strip=True)
        m = re.search(r"(\d+)", text)
        if m:
            max_page = max(max_page, int(m.group(1)))

    # Also check for "next" with page count text
    total_text = soup.select_one("[class*='total'], [class*='results-count'], .count")
    if total_text:
        m = re.search(r"(\d+)", total_text.get_text())
        if m:
            per_page = len(extract_product_urls(soup, "")) or 50
            max_page = max(max_page, -(-int(m.group(1)) // per_page))  # ceiling division

    return max_page


def get_next_page_url(soup: BeautifulSoup, current_url: str) -> Optional[str]:
    next_el = soup.select_one("a[rel='next'], a[class*='next'], [aria-label='next page' i]")
    if next_el:
        href = next_el.get("href", "")
        if href:
            return urljoin(current_url, href)

    # Try incrementing pg= or pg parameter
    for pattern, replace in [
        (r"([?&]pg=)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1)),
        (r"(/pg)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1)),
    ]:
        if re.search(pattern, current_url):
            return re.sub(pattern, replace, current_url)

    # Append first page param
    if "pg=" not in current_url and "/pg" not in current_url:
        sep = "&" if "?" in current_url else "?"
        return current_url + sep + "pg=2"

    return None


def collect_category(
    session: requests.Session,
    cat: dict,
    conn: sqlite3.Connection,
    delay: float,
) -> int:
    """Paginate through a category and insert product URLs into DB."""
    cat_url = cat["url"]
    cat_id = cat["id"]
    cat_name = cat["name"]
    cat_path = cat.get("category_path", cat_name)

    log.info("Category: %s | %s", cat_path, cat_url)

    soup = fetch(session, cat_url, delay)
    if not soup:
        return 0

    total_found = 0
    page = 1
    current_url = cat_url

    while True:
        product_urls = extract_product_urls(soup, current_url)
        log.info("  Page %d: %d products", page, len(product_urls))

        for purl in product_urls:
            article = ""
            m = re.search(r"_(\d{6,})\.htm", purl)
            if m:
                article = m.group(1)
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO products (url, article, category_id, category_name, category_path) VALUES (?,?,?,?,?)",
                    (purl, article, cat_id, cat_name, cat_path),
                )
            except sqlite3.Error as e:
                log.warning("DB insert error: %s", e)

        conn.commit()
        total_found += len(product_urls)

        next_url = get_next_page_url(soup, current_url)
        if not next_url or next_url == current_url or not product_urls:
            break

        page += 1
        soup = fetch(session, next_url, delay)
        if not soup:
            break
        current_url = next_url

    # Mark category as done
    conn.execute(
        "INSERT OR REPLACE INTO categories_done (category_id, url, products_found) VALUES (?,?,?)",
        (cat_id, cat_url, total_found),
    )
    conn.commit()
    log.info("  Done: %d total product URLs collected", total_found)
    return total_found


def get_leaf_categories(tree: list, parent_path: str = "") -> list:
    """Return all categories, annotated with full path string."""
    result = []
    for cat in tree:
        path = f"{parent_path} > {cat['name']}" if parent_path else cat["name"]
        cat_copy = dict(cat)
        cat_copy["category_path"] = path
        subcats = cat.get("subcategories", [])
        if subcats:
            result.extend(get_leaf_categories(subcats, path))
        else:
            result.append(cat_copy)
    return result


def main():
    parser = argparse.ArgumentParser(description="Collect product URLs from Thomann categories")
    parser.add_argument("--categories", default="categories.json")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--category-filter", default=None, help="Only process top-level category matching this name")
    parser.add_argument("--resume", action="store_true", help="Skip already-processed categories")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--proxy", default=None)
    args = parser.parse_args()

    with open(args.categories, encoding="utf-8") as f:
        data = json.load(f)

    tree = data.get("tree", data) if isinstance(data, dict) else data

    # Filter to one top-level category if requested
    if args.category_filter:
        filtered = [c for c in tree if args.category_filter.lower() in c["name"].lower()]
        if not filtered:
            log.error("Category '%s' not found. Available: %s",
                      args.category_filter, [c["name"] for c in tree])
            sys.exit(1)
        tree = filtered
        log.info("Filtering to: %s", [c["name"] for c in tree])

    # Get all leaf categories with paths
    leaves = get_leaf_categories(tree)
    log.info("Total leaf categories to process: %d", len(leaves))

    conn = init_db(args.db)
    session = get_session(args.proxy)

    # Get already-done categories if resuming
    done_ids = set()
    if args.resume:
        rows = conn.execute("SELECT category_id FROM categories_done").fetchall()
        done_ids = {r[0] for r in rows}
        log.info("Resuming: %d categories already done", len(done_ids))

    total_products = 0
    for i, cat in enumerate(leaves, 1):
        if cat["id"] in done_ids:
            log.info("[%d/%d] Skipping (done): %s", i, len(leaves), cat["category_path"])
            continue
        log.info("[%d/%d]", i, len(leaves))
        count = collect_category(session, cat, conn, args.delay)
        total_products += count

    total_in_db = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    log.info("Done. Total product URLs in DB: %d", total_in_db)
    conn.close()


if __name__ == "__main__":
    main()
