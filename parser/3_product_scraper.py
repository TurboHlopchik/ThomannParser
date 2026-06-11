#!/usr/bin/env python3
"""
Step 3: Scrape product data for all URLs in products.db.
Saves all data back to products.db. Supports pause/resume.

Usage:
    python3 3_product_scraper.py
    python3 3_product_scraper.py --db products.db
    python3 3_product_scraper.py --limit 100        # scrape only 100 products (for testing)
    python3 3_product_scraper.py --category "Guitars"

Interrupt with Ctrl+C — progress is saved, resume by running again.
"""

import argparse
import json
import logging
import re
import signal
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
running = True


def handle_interrupt(sig, frame):
    global running
    log.info("Interrupted — finishing current product and saving...")
    running = False


signal.signal(signal.SIGINT, handle_interrupt)


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")

    # Add product data columns if they don't exist
    existing = {row[1] for row in conn.execute("PRAGMA table_info(products)")}
    new_cols = {
        "pagetitle": "TEXT",
        "longtitle": "TEXT",
        "alias": "TEXT",
        "brand": "TEXT",
        "description": "TEXT",
        "content": "TEXT",
        "price": "TEXT",
        "old_price": "TEXT",
        "image": "TEXT",
        "gallery": "TEXT",
        "properties": "TEXT",
        "rating": "TEXT",
        "reviews_count": "TEXT",
        "availability": "TEXT",
        "scraped_at": "DATETIME",
        "scrape_error": "TEXT",
    }
    for col, col_type in new_cols.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE products ADD COLUMN {col} {col_type}")

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


def fetch(session: requests.Session, url: str, delay: float = 2.0) -> Optional[BeautifulSoup]:
    time.sleep(delay)
    try:
        session.headers["Referer"] = BASE_URL + "/intl/"
        resp = session.get(url, timeout=25)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        if resp.status_code == 403:
            if resp.headers.get("x-deny-reason") == "host_not_allowed":
                log.error("IP blocked. Use --proxy.")
                sys.exit(1)
            return None
        log.warning("HTTP %s: %s", resp.status_code, url)
        return None
    except Exception as e:
        log.error("Error: %s | %s", url, e)
        return None


def clean_price(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[^\d,.]", "", text.strip())
    cleaned = cleaned.replace(",", ".")
    # Handle "1.299.00" → "1299.00"
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return str(float(cleaned))
    except ValueError:
        return cleaned


def make_alias(title: str) -> str:
    alias = title.lower()
    alias = re.sub(r"[^\w\s-]", "", alias)
    alias = re.sub(r"[\s_]+", "-", alias)
    alias = re.sub(r"-+", "-", alias).strip("-")
    return alias[:120]


def parse_product(soup: BeautifulSoup, url: str) -> dict:
    p = {}

    # Title
    for sel in ["h1.product-title", "h1[class*='title']", ".fx-pdp-header__title", "h1"]:
        el = soup.select_one(sel)
        if el:
            p["pagetitle"] = el.get_text(strip=True)
            p["alias"] = make_alias(p["pagetitle"])
            break

    # Brand
    for sel in ["span[class*='manufacturer']", "a[class*='brand']", "span[class*='brand']",
                "[itemprop='brand']", ".fx-pdp-header__manufacturer"]:
        el = soup.select_one(sel)
        if el:
            p["brand"] = el.get_text(strip=True)
            break

    p["longtitle"] = f"{p.get('brand', '')} {p.get('pagetitle', '')}".strip()

    # Article / SKU
    for sel in ["[class*='article-number']", "[class*='product-id']", "[data-article]"]:
        el = soup.select_one(sel)
        if el:
            article = re.sub(r"[^\d]", "", el.get_text())
            if article:
                p["article"] = article
                break
    if "article" not in p:
        m = re.search(r"_(\d{6,})\.htm", url)
        if m:
            p["article"] = m.group(1)

    # Price
    for sel in [
        ".fx-product-stage-price__sale",
        ".product-price__main-price",
        "[class*='price--current']",
        "[class*='price-sale']",
        ".our-price",
        "[itemprop='price']",
    ]:
        el = soup.select_one(sel)
        if el:
            price_text = el.get("content") or el.get_text()
            p["price"] = clean_price(price_text)
            if p["price"]:
                break

    for sel in [
        ".fx-product-stage-price__uvp",
        "[class*='price--before']",
        "[class*='price--old']",
        "[class*='price-old']",
    ]:
        el = soup.select_one(sel)
        if el:
            p["old_price"] = clean_price(el.get_text())
            if p["old_price"]:
                break

    # Main image
    for sel in [
        ".pdp-image__main img",
        ".product-images__main img",
        ".fx-pdp-image__main img",
        "[class*='product-image'] img[class*='main']",
        ".product-stage img",
    ]:
        el = soup.select_one(sel)
        if el:
            src = el.get("data-src") or el.get("data-zoom-src") or el.get("src", "")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                p["image"] = src
                break

    # Gallery
    gallery = []
    seen = {p.get("image", "")}
    for sel in [
        ".product-images__thumbnails img",
        ".fx-pdp-images__thumbs img",
        "[class*='thumbnails'] img",
        "[class*='thumb-list'] img",
    ]:
        for img in soup.select(sel):
            src = img.get("data-zoom-src") or img.get("data-src") or img.get("src", "")
            src = re.sub(r"_\d+x\d+(\.[a-z]+)$", r"\1", src)
            if src.startswith("//"):
                src = "https:" + src
            if src and src not in seen and "placeholder" not in src:
                seen.add(src)
                gallery.append(src)
        if gallery:
            break
    p["gallery"] = "||".join(gallery)

    # Short description
    for sel in [
        ".fx-pdp-teaser",
        ".product-teaser",
        "[class*='description--short']",
        "[class*='short-description']",
    ]:
        el = soup.select_one(sel)
        if el:
            p["description"] = el.get_text(separator=" ", strip=True)[:600]
            break

    # Full description (HTML)
    for sel in [
        ".fx-pdp-description",
        ".product-detail-description",
        "[class*='description-text']",
        "[class*='product-description']",
    ]:
        el = soup.select_one(sel)
        if el:
            p["content"] = str(el)
            if not p.get("description"):
                p["description"] = el.get_text(separator=" ", strip=True)[:600]
            break

    # Technical specs
    props = {}

    # Method 1: table rows
    for table_sel in [
        "table[class*='spec']",
        "table[class*='feature']",
        ".product-features table",
        ".specifications table",
        "[class*='tech-specs'] table",
    ]:
        for table in soup.select(table_sel):
            for row in table.select("tr"):
                cells = row.select("th, td")
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    val = " | ".join(c.get_text(strip=True) for c in cells[1:])
                    if key and val:
                        props[key] = val

    # Method 2: definition lists
    for dl in soup.select("dl[class*='spec'], dl[class*='feature'], .product-features dl"):
        keys = dl.select("dt")
        vals = dl.select("dd")
        for k, v in zip(keys, vals):
            key = k.get_text(strip=True)
            val = v.get_text(strip=True)
            if key:
                props[key] = val

    # Method 3: feature list items
    if not props:
        for item in soup.select("[class*='feature__item'], [class*='spec-item']"):
            label = item.select_one("[class*='label'], [class*='name'], dt, strong")
            value = item.select_one("[class*='value'], dd")
            if label and value:
                props[label.get_text(strip=True)] = value.get_text(strip=True)

    p["properties"] = json.dumps(props, ensure_ascii=False)

    # Rating
    for sel in ["[itemprop='ratingValue']", "[class*='rating__value']"]:
        el = soup.select_one(sel)
        if el:
            p["rating"] = el.get("content") or el.get_text(strip=True)
            break

    for sel in ["[itemprop='reviewCount']", "[class*='rating__count']"]:
        el = soup.select_one(sel)
        if el:
            p["reviews_count"] = re.sub(r"[^\d]", "", el.get_text())
            break

    # Availability
    for sel in ["[class*='availability']", "[class*='delivery-info']", "[class*='stock']"]:
        el = soup.select_one(sel)
        if el:
            p["availability"] = el.get_text(strip=True)[:150]
            break

    return p


def main():
    parser = argparse.ArgumentParser(description="Scrape product data for URLs in products.db")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--limit", type=int, default=None, help="Max products to scrape (for testing)")
    parser.add_argument("--category", default=None, help="Filter by category name")
    parser.add_argument("--proxy", default=None)
    args = parser.parse_args()

    conn = init_db(args.db)
    session = get_session(args.proxy)

    # Build query
    query = "SELECT id, url FROM products WHERE status = 'pending'"
    params = []
    if args.category:
        query += " AND category_path LIKE ?"
        params.append(f"%{args.category}%")
    query += " ORDER BY id"
    if args.limit:
        query += f" LIMIT {args.limit}"

    rows = conn.execute(query, params).fetchall()
    total = len(rows)
    log.info("Products to scrape: %d", total)

    scraped = 0
    errors = 0

    for i, (row_id, url) in enumerate(rows, 1):
        if not running:
            break

        log.info("[%d/%d] %s", i, total, url)
        soup = fetch(session, url, args.delay)

        if not soup:
            conn.execute(
                "UPDATE products SET status='error', scrape_error='fetch_failed', scraped_at=CURRENT_TIMESTAMP WHERE id=?",
                (row_id,),
            )
            conn.commit()
            errors += 1
            continue

        try:
            data = parse_product(soup, url)
            conn.execute("""
                UPDATE products SET
                    status = 'scraped',
                    pagetitle = ?,
                    longtitle = ?,
                    alias = ?,
                    brand = ?,
                    description = ?,
                    content = ?,
                    price = ?,
                    old_price = ?,
                    image = ?,
                    gallery = ?,
                    properties = ?,
                    rating = ?,
                    reviews_count = ?,
                    availability = ?,
                    scraped_at = CURRENT_TIMESTAMP,
                    scrape_error = NULL
                WHERE id = ?
            """, (
                data.get("pagetitle"),
                data.get("longtitle"),
                data.get("alias"),
                data.get("brand"),
                data.get("description"),
                data.get("content"),
                data.get("price"),
                data.get("old_price"),
                data.get("image"),
                data.get("gallery"),
                data.get("properties"),
                data.get("rating"),
                data.get("reviews_count"),
                data.get("availability"),
                row_id,
            ))
            conn.commit()
            scraped += 1

            if i % 50 == 0:
                log.info("Progress: %d scraped, %d errors, %d remaining", scraped, errors, total - i)

        except Exception as e:
            log.error("Parse error for %s: %s", url, e)
            conn.execute(
                "UPDATE products SET status='error', scrape_error=?, scraped_at=CURRENT_TIMESTAMP WHERE id=?",
                (str(e)[:200], row_id),
            )
            conn.commit()
            errors += 1

    log.info("Finished. Scraped: %d, Errors: %d", scraped, errors)

    # Stats
    stats = conn.execute("""
        SELECT status, COUNT(*) FROM products GROUP BY status
    """).fetchall()
    for status, count in stats:
        log.info("  %s: %d", status, count)

    conn.close()


if __name__ == "__main__":
    main()
