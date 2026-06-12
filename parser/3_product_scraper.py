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
    """Parse a Thomann (intl, European-formatted) price string to a number.

    Format: dot = thousands separator, comma = decimal — e.g. '2.555 €' = 2555,
    '5,90 €' = 5.90, '2.555,90 €' = 2555.90.
    """
    if not text:
        return ""
    s = re.sub(r"[^\d.,]", "", text.strip())
    if not s:
        return ""
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")   # dot thousands, comma decimal
    elif "," in s:
        s = s.replace(",", ".")                     # comma is the decimal mark
    else:
        s = s.replace(".", "")                      # lone dot = thousands (intl)
    try:
        return str(float(s))
    except ValueError:
        return s


def og(soup: BeautifulSoup, prop: str) -> str:
    """Return an Open Graph / meta content value."""
    m = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
    return (m.get("content") or "").strip() if m else ""


def meta_itemprop(soup: BeautifulSoup, name: str) -> str:
    """Return a schema.org microdata <meta itemprop="..."> content value."""
    m = soup.find("meta", attrs={"itemprop": name})
    return (m.get("content") or "").strip() if m else ""


def _num(value: str) -> str:
    """Machine number string (schema.org price, dot=decimal) -> normalised float str."""
    if not value:
        return ""
    try:
        return str(float(value.replace(",", ".")))
    except ValueError:
        return ""


def parse_breadcrumb(soup: BeautifulSoup) -> list:
    """Clean breadcrumb trail (the DOM duplicates it for mobile/desktop)."""
    bc = soup.select_one("[class*='readcrumb']")
    out = []
    if bc:
        for a in bc.find_all("a", href=True):
            t = a.get_text(strip=True)
            if t and t not in ("···", "All Categories", "Home") and t not in out:
                out.append(t)
    return out


def make_alias(title: str) -> str:
    alias = title.lower()
    alias = re.sub(r"[^\w\s-]", "", alias)
    alias = re.sub(r"[\s_]+", "-", alias)
    alias = re.sub(r"-+", "-", alias).strip("-")
    return alias[:120]


def parse_product(soup: BeautifulSoup, url: str) -> dict:
    """Extract product fields from a Thomann product page (current frontend).

    The page is a JS app with no JSON-LD, but ships Open Graph meta tags, a
    ``li.keyfeature`` spec list, a breadcrumb and ``.price-and-availability``
    price block — which together cover everything we need.
    """
    p = {}

    # --- Title ---
    title = og(soup, "og:title")
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
    p["pagetitle"] = title
    p["alias"] = make_alias(title)

    # --- Brand (manufacturer logo alt; fall back to last breadcrumb crumb) ---
    brand = ""
    bl = soup.select_one(
        "img[src*='manufacturer'][alt], img[src*='/logo/'][alt], img[class*='manufacturer'][alt]"
    )
    if bl:
        brand = (bl.get("alt") or "").strip()
    crumbs = parse_breadcrumb(soup)
    if not brand and crumbs:
        brand = crumbs[-1]
    p["brand"] = brand
    p["longtitle"] = title  # og:title already contains the brand

    # --- Category (breadcrumb minus the trailing brand crumb) ---
    cat_crumbs = [c for c in crumbs if c != brand]
    p["category_path"] = " > ".join(cat_crumbs)
    p["category_name"] = cat_crumbs[-1] if cat_crumbs else ""
    p["category_id"] = make_alias(p["category_name"]) if p["category_name"] else ""

    # --- Technical specs (li.keyfeature -> label/value) ---
    props = {}
    for li in soup.select("li.keyfeature"):
        lab = li.select_one(".keyfeature__label")
        if not lab:
            continue
        key = lab.get_text(strip=True)
        full = li.get_text(" ", strip=True)
        val = full[len(key):].strip() if full.startswith(key) else full.replace(key, "", 1).strip()
        if key and val:
            props[key] = val
    p["properties"] = json.dumps(props, ensure_ascii=False)

    # --- Article number (from og:image .../pics/prod/<id>.jpg, then specs) ---
    og_image = og(soup, "og:image")
    article = ""
    m = re.search(r"pics/prod/(\d+)", og_image)
    if m:
        article = m.group(1)
    if not article and "Item number" in props:
        article = re.sub(r"[^\d]", "", props["Item number"])
    if not article:
        m = re.search(r"_(\d{6,})\.htm", url)
        if m:
            article = m.group(1)
    p["article"] = article

    # --- Price ---
    # Prefer the schema.org microdata meta (present site-wide, machine-formatted
    # with dot as decimal); fall back to the visual EU-formatted buy-box price.
    p["price"] = _num(meta_itemprop(soup, "price"))
    if not p["price"]:
        box = soup.select_one(".price-and-availability") or soup
        pe = box.select_one("[class*='fx-price-group__primary']")
        p["price"] = clean_price(pe.get_text()) if pe else ""
    box = soup.select_one(".price-and-availability") or soup
    rrp = box.select_one("[class*='rrp'], [class*='uvp'], [class*='strike'], del")
    p["old_price"] = clean_price(rrp.get_text()) if rrp else ""

    # --- Images (gallery is JS-loaded; use the canonical full-size main image) ---
    if article:
        p["image"] = f"https://thumbs.static-thomann.de/thumb/thumb1000x1000/pics/prod/{article}.jpg"
    else:
        p["image"] = og_image
    p["gallery"] = ""

    # --- Description + content (build clean HTML from og:description + specs) ---
    desc = og(soup, "og:description")
    p["description"] = desc[:600]
    content = f"<p>{desc}</p>" if desc else ""
    if props:
        rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in props.items())
        content += f"<table>{rows}</table>"
    p["content"] = content

    # --- Rating / reviews ---
    rv = soup.select_one("[itemprop='ratingValue']")
    if rv:
        p["rating"] = rv.get("content") or rv.get_text(strip=True)
    rc = soup.select_one("[class*='review']")
    if rc:
        mm = re.search(r"\d+", rc.get_text())
        p["reviews_count"] = mm.group(0) if mm else ""

    # --- Availability (text in the buy box that isn't a price) ---
    avail = ""
    for s in box.find_all(string=re.compile(r"(in stock|available|delivery|weeks?|days?|sold out)", re.I)):
        t = re.sub(r"\s+", " ", s).strip()
        if t and "€" not in t and len(t) < 80:
            avail = t
            break
    p["availability"] = avail

    return p


_SELF_TEST_HTML = """
<html><head>
  <meta property="og:title" content="Gibson Les Paul Standard 60s AAA LB">
  <meta property="og:description" content="Electric Guitar, Top: AAA flamed maple, Body: Mahogany">
  <meta property="og:image" content="https://www.thomann.de/thumb/opengraph/pics/prod/617050.jpg">
  <meta itemprop="price" content="2555">
  <meta itemprop="priceCurrency" content="EUR">
</head><body>
  <nav class="fx-breadcrumb">
    <a href="/intl/cat.html">All Categories</a>
    <a href="/intl/guitars_and_basses.html">Guitars &amp; Basses</a>
    <a href="/intl/electric_guitars.html">Electric Guitars</a>
    <a href="/intl/lp_models.html">Single Cut Guitars</a>
    <a href="/intl/gibson_brand.html">Gibson</a>
  </nav>
  <img src="/manufacturer/gibson_logo.png" alt="Gibson">
  <div class="price-and-availability">
    <div class="fx-price-group"><span class="fx-price-group__primary">2.555&nbsp;€</span></div>
    <span class="availability__text">In stock</span>
  </div>
  <ul>
    <li class="keyfeature"><span class="keyfeature__label">Colour</span> <span>Lemon Burst</span></li>
    <li class="keyfeature"><span class="keyfeature__label">Body</span> <span>Mahogany</span></li>
    <li class="keyfeature"><span class="keyfeature__label">Item number</span> <span>617050</span></li>
  </ul>
  <span itemprop="ratingValue">4.5</span>
  <div class="review-count">2 Customer ratings</div>
</body></html>
"""


def self_test() -> int:
    assert _num("2555") == "2555.0" and _num("5.90") == "5.9" and _num("") == ""
    assert clean_price("2.555 €") == "2555.0", clean_price("2.555 €")
    assert clean_price("5,90 €") == "5.9", clean_price("5,90 €")
    assert clean_price("2.555,90 €") == "2555.9", clean_price("2.555,90 €")
    assert clean_price("125 €") == "125.0"

    soup = BeautifulSoup(_SELF_TEST_HTML, "lxml")
    d = parse_product(soup, "https://www.thomann.de/intl/gibson_les_paul_standard_60s_aaa_lb.htm")
    assert d["pagetitle"] == "Gibson Les Paul Standard 60s AAA LB", d["pagetitle"]
    assert d["brand"] == "Gibson", d["brand"]
    assert d["price"] == "2555.0", d["price"]
    assert d["article"] == "617050", d["article"]
    assert d["category_path"] == "Guitars & Basses > Electric Guitars > Single Cut Guitars", d["category_path"]
    assert d["category_name"] == "Single Cut Guitars"
    assert d["image"].endswith("/pics/prod/617050.jpg")
    assert d["rating"] == "4.5"
    assert d["reviews_count"] == "2", d["reviews_count"]
    props = json.loads(d["properties"])
    assert props.get("Colour") == "Lemon Burst" and props.get("Body") == "Mahogany"
    assert d["availability"] == "In stock", d["availability"]
    print("self-test OK: og/title/brand/price(EU)/article/category/specs/rating")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Scrape product data for URLs in products.db")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--limit", type=int, default=None, help="Max products to scrape (for testing)")
    parser.add_argument("--category", default=None, help="Filter by category name")
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--html-file", default=None,
                        help="Parse a saved product page and print the result (offline).")
    parser.add_argument("--url", default="https://www.thomann.de/intl/product.htm",
                        help="URL context to use with --html-file.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.html_file:
        import json as _json
        with open(args.html_file, encoding="utf-8", errors="replace") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        data = parse_product(soup, args.url)
        for k, v in data.items():
            if k == "properties":
                props = _json.loads(v or "{}")
                print(f"  {k:13s}: {len(props)} specs -> {list(props.items())[:3]}")
            else:
                print(f"  {k:13s}: {str(v)[:90]}")
        return 0

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
                    article = COALESCE(NULLIF(?, ''), article),
                    category_id = COALESCE(NULLIF(?, ''), category_id),
                    category_name = COALESCE(NULLIF(?, ''), category_name),
                    category_path = COALESCE(NULLIF(?, ''), category_path),
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
                data.get("article") or "",
                data.get("category_id") or "",
                data.get("category_name") or "",
                data.get("category_path") or "",
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
    sys.exit(main())
