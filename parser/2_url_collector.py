#!/usr/bin/env python3
"""
Step 2: Collect all product URLs by walking Thomann's category hierarchy.

Thomann's listing has two kinds of pages:
  * landing/overview pages (e.g. electric_guitars.html) — JS-rendered, show only
    a handful of products and a grid of sub-categories (div.fx-category-grid);
  * leaf list pages (e.g. st_models.html) — server-render the full product list
    50 per page with working ?ls=50&pg=N pagination.

The global search.html listing is capped at ~155 pages (~7,000 products), so we
cannot get the whole 124k catalogue from it. Instead we recurse the category
tree: starting from the top categories, each page is classified — if it has
sub-categories we descend into them; if it has none it is a leaf and we
paginate it, collecting every product URL (tagged with its category path).

The category queue lives in the DB, so the crawl is fully resumable: Ctrl+C and
re-run continues with the pending categories.

Usage:
    python3 2_url_collector.py                       # full recursive crawl
    python3 2_url_collector.py --seed-category "Guitars"   # one top category
    python3 2_url_collector.py --max-leaves 5        # stop after 5 leaves (test)
    python3 2_url_collector.py --reset-queue         # rebuild the category queue
    python3 2_url_collector.py --search-mode         # old (capped) search.html crawl
    python3 2_url_collector.py --self-test
"""

import argparse
import json
import logging
import os
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
SEARCH_PATH = "/intl/search.html"
CAT_PAGE = BASE_URL + "/intl/cat.html"

# A product detail page is a single-segment slug ending in .htm (not .html).
_PRODUCT_RE = re.compile(r"^/intl/[a-z0-9][a-z0-9_.%-]*\.htm$", re.I)
# A category page is a single-segment slug ending in .html.
_CATEGORY_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]*\.html$", re.I)

# Slugs/keywords that are not real product categories.
_SKIP_SLUGS = {
    "cat", "index", "search", "guitarlab", "compinfo", "helpdesk", "mythomann",
    "cart", "wishlist", "compare", "newsletter", "gift_voucher", "giftvoucher",
    "blowouts", "prodnews", "topseller", "classified", "onlineexpert",
}
PROMO_KEYWORDS = ["bestseller", "top seller", "new arrivals", "sale", "outlet",
                  "deals", "bargains", "hot deals", "gift voucher"]


def is_promo(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in PROMO_KEYWORDS)


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
    # The resumable category work-queue (parents to expand + leaves to paginate).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS category_queue (
            url TEXT PRIMARY KEY,
            name TEXT,
            path TEXT,
            status TEXT DEFAULT 'pending',   -- pending | done
            kind TEXT,                       -- parent | leaf
            products_found INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS crawl_state (key TEXT PRIMARY KEY, value TEXT)
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON products(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_q_status ON category_queue(status)")
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


def fetch(session: requests.Session, url: str, delay: float = 2.0,
          max_retries: int = 4) -> Optional[BeautifulSoup]:
    """Fetch with throttling, IP-block detection and 429 back-off."""
    for attempt in range(1, max_retries + 1):
        time.sleep(delay)
        try:
            session.headers["Referer"] = BASE_URL + "/intl/"
            resp = session.get(url, timeout=25)
        except Exception as e:
            log.warning("Request error (%s); retry %d/%d", e, attempt, max_retries)
            time.sleep(5 * attempt)
            continue
        if resp.status_code == 200:
            if "Just a moment" in resp.text[:2000] and "challenge" in resp.text.lower():
                log.warning("Cloudflare challenge; backing off %ds", 15 * attempt)
                time.sleep(15 * attempt)
                continue
            return BeautifulSoup(resp.text, "lxml")
        if resp.status_code == 403 and resp.headers.get("x-deny-reason") == "host_not_allowed":
            log.error("IP blocked (host_not_allowed). Run from a residential IP or use --proxy.")
            sys.exit(1)
        if resp.status_code == 429:
            wait = 15 * attempt
            log.warning("HTTP 429 (rate limited); backing off %ds (retry %d/%d)",
                        wait, attempt, max_retries)
            time.sleep(wait)
            continue
        log.warning("HTTP %s: %s", resp.status_code, url)
        return None
    log.error("Giving up on %s after %d retries", url, max_retries)
    return None


def _clean_name(text: str) -> str:
    text = re.sub(r"\s*[\d.,]+\s*items?\s*$", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*[\d.,]+\s*$", "", text).strip()
    return re.sub(r"\s+", " ", text).strip()


def extract_subcategories(soup: BeautifulSoup, base_url: str) -> list:
    """Sub-category links from cat.html (categories-list) or a landing page
    (fx-category-grid). Returns [{'url','name'}] de-duplicated."""
    seen = set()
    out = []
    selectors = [
        "ul.categories-list li.categories-list__item a.categories-list__link[href]",
        "div.fx-category-grid a[href]",
    ]
    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href", "").split("?")[0].split("#")[0]
            if not href:
                continue
            slug = href.lstrip("/").split("/")[-1]
            if not _CATEGORY_SLUG_RE.match(slug):
                continue
            if slug[:-5] in _SKIP_SLUGS:
                continue
            url = urljoin(base_url, href).replace("http://", "https://")
            if url in seen or url.rstrip("/") == base_url.rstrip("/"):
                continue
            name = _clean_name(a.get_text(" ", strip=True))
            if not name or is_promo(name):
                continue
            seen.add(url)
            out.append({"url": url, "name": name})
    return out


def extract_product_urls(soup: BeautifulSoup, base_url: str = BASE_URL) -> list:
    """Product detail URLs on a page, excluding recommendation carousels."""
    urls = []
    seen = set()
    for a in soup.find_all("a", href=True):
        if a.find_parent(class_=re.compile("carousel")):
            continue
        full = urljoin(base_url, a["href"]).split("?")[0].split("#")[0]
        full = full.replace("http://", "https://")
        path = full.split("thomann.de", 1)[-1] if "thomann.de" in full else full
        if not _PRODUCT_RE.match(path):
            continue
        if full not in seen:
            seen.add(full)
            urls.append(full)
    return urls


def article_from_url(url: str) -> str:
    m = re.search(r"_(\d{6,})\.htm", url)
    return m.group(1) if m else ""


def search_url(page: int, ls: int = 50) -> str:
    return f"{BASE_URL}{SEARCH_PATH}?ls={ls}&pg={page}"


def page_url(cat_url: str, page: int, ls: int = 50) -> str:
    sep = "&" if "?" in cat_url else "?"
    return f"{cat_url}{sep}ls={ls}&pg={page}"


# ─── Category queue helpers ───────────────────────────────────────────────────

def enqueue(conn, url, name, path):
    conn.execute(
        "INSERT OR IGNORE INTO category_queue (url, name, path, status) VALUES (?,?,?, 'pending')",
        (url, name, path),
    )


def insert_products(conn, urls, name, path):
    cid = re.sub(r"[^\w]+", "-", (name or "").lower()).strip("-")
    added = 0
    for u in urls:
        cur = conn.execute(
            """INSERT INTO products (url, article, category_id, category_name, category_path, status)
               VALUES (?,?,?,?,?, 'pending')
               ON CONFLICT(url) DO UPDATE SET
                   category_id   = COALESCE(NULLIF(products.category_id,''), excluded.category_id),
                   category_name = COALESCE(NULLIF(products.category_name,''), excluded.category_name),
                   category_path = COALESCE(NULLIF(products.category_path,''), excluded.category_path)""",
            (u, article_from_url(u), cid, name, path),
        )
        added += cur.rowcount
    return added


def seed_queue(conn, session, args):
    """Populate the category queue with top-level seeds if it is empty."""
    have = conn.execute("SELECT COUNT(*) FROM category_queue").fetchone()[0]
    if have and not args.reset_queue:
        return
    if args.reset_queue:
        conn.execute("DELETE FROM category_queue")

    seeds = []
    cats_file = args.categories
    if os.path.exists(cats_file):
        data = json.load(open(cats_file, encoding="utf-8"))
        tree = data.get("tree", data) if isinstance(data, dict) else data
        for top in tree:
            if args.seed_category and args.seed_category.lower() not in top["name"].lower():
                continue
            seeds.append((top["url"], top["name"], top["name"]))
    if not seeds:
        log.info("No categories.json seeds; starting from cat.html")
        seeds = [(CAT_PAGE, "", "")]
    with conn:
        for url, name, path in seeds:
            enqueue(conn, url, name, path)
    log.info("Seeded category queue with %d top categories", len(seeds))


def paginate_leaf(session, conn, url, name, path, ls, delay, first_soup):
    """Paginate a leaf list page, collecting product URLs. Returns count added."""
    added = 0
    seen_run = set()
    repeat = 0
    page = 1
    soup = first_soup
    while True:
        if soup is None:
            soup = fetch(session, page_url(url, page, ls), delay)
        if soup is None:
            break
        urls = extract_product_urls(soup, url)
        fresh = [u for u in urls if u not in seen_run]
        if not urls or not fresh:
            repeat += 1
            if repeat >= 2 or not urls:
                break
            page += 1
            soup = None
            continue
        repeat = 0
        seen_run.update(urls)
        with conn:
            added += insert_products(conn, urls, name, path)
        log.info("    %s p%d: %d products (%d collected)", name, page, len(urls), len(seen_run))
        page += 1
        soup = None
    return added


def crawl_categories(session, conn, args):
    seed_queue(conn, session, args)
    visited = set(r[0] for r in conn.execute(
        "SELECT url FROM category_queue WHERE status='done'"))
    leaves_done = 0
    total_added = 0

    while True:
        row = conn.execute(
            "SELECT url, name, path FROM category_queue WHERE status='pending' ORDER BY rowid LIMIT 1"
        ).fetchone()
        if not row:
            break
        url, name, path = row
        if url in visited:
            conn.execute("UPDATE category_queue SET status='done' WHERE url=?", (url,))
            conn.commit()
            continue
        visited.add(url)

        soup = fetch(session, page_url(url, 1, args.ls), args.delay)
        if soup is None:
            conn.execute("UPDATE category_queue SET status='done', kind='error' WHERE url=?", (url,))
            conn.commit()
            continue

        subs = extract_subcategories(soup, url)
        if subs:
            # Parent/landing: descend into its sub-categories.
            with conn:
                for s in subs:
                    child_path = f"{path} > {s['name']}" if path else s["name"]
                    enqueue(conn, s["url"], s["name"], child_path)
                conn.execute("UPDATE category_queue SET status='done', kind='parent' WHERE url=?", (url,))
            log.info("[parent] %s -> %d subcategories", name or url, len(subs))
        else:
            # Leaf list page: paginate and collect.
            added = paginate_leaf(session, conn, url, name, path, args.ls, args.delay, soup)
            with conn:
                conn.execute(
                    "UPDATE category_queue SET status='done', kind='leaf', products_found=? WHERE url=?",
                    (added, url),
                )
            total_added += added
            leaves_done += 1
            total_db = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            log.info("[leaf %d] %s: +%d (DB total %d)", leaves_done, name or url, added, total_db)
            if args.max_leaves and leaves_done >= args.max_leaves:
                log.info("Reached --max-leaves (%d); stopping.", args.max_leaves)
                break

    return total_added


# ─── Old global search.html crawl (capped ~155 pages) ─────────────────────────

def crawl_search(session, conn, ls, delay, max_pages=None):
    page, added_total, empty, repeat = 1, 0, 0, 0
    seen = set()
    while True:
        if max_pages and page > max_pages:
            break
        soup = fetch(session, search_url(page, ls), delay)
        if soup is None:
            break
        urls = extract_product_urls(soup)
        if not urls:
            empty += 1
            if empty >= 2:
                break
            page += 1
            continue
        empty = 0
        fresh = [u for u in urls if u not in seen]
        if not fresh:
            repeat += 1
            if repeat >= 2:
                log.info("Listing repeating — reached search.html cap.")
                break
            page += 1
            continue
        repeat = 0
        seen.update(urls)
        with conn:
            added_total += insert_products(conn, urls, "", "")
        log.info("Page %d: %d products (%d collected)", page, len(urls), len(seen))
        page += 1
    return added_total


# ─── Self-test ────────────────────────────────────────────────────────────────

def self_test() -> int:
    cat_html = """
    <div class="category"><div class="headline"><a href="guitars_and_basses.html">Guitars 33,254 items</a></div>
      <ul class="categories-list"><li class="categories-list__item">
        <a class="categories-list__link" href="electric_guitars.html">Electric Guitars</a></li></ul></div>
    """
    subs = extract_subcategories(BeautifulSoup(cat_html, "lxml"), CAT_PAGE)
    assert [s["name"] for s in subs] == ["Electric Guitars"], subs
    assert subs[0]["url"] == "https://www.thomann.de/intl/electric_guitars.html"

    landing = """
    <div class="fx-category-grid">
      <a href="st_models.html">ST Style Guitars</a>
      <a href="lp_models.html">Single Cut Guitars</a>
      <a href="guitarlab.html">GuitarLab</a>  <!-- skipped -->
    </div>
    """
    subs = extract_subcategories(BeautifulSoup(landing, "lxml"),
                                 "https://www.thomann.de/intl/electric_guitars.html")
    assert [s["name"] for s in subs] == ["ST Style Guitars", "Single Cut Guitars"], subs

    listing = """
    <div class="fx-carousel"><a href="reco.htm">x</a></div>
    <a href="harley_benton_st_20_472390.htm">HB</a>
    <a href="fender_strat.htm">Fender</a>
    <a href="electric_guitars.html">cat (ignored)</a>
    """
    urls = extract_product_urls(BeautifulSoup(listing, "lxml"),
                                "https://www.thomann.de/intl/st_models.html")
    assert urls == ["https://www.thomann.de/intl/harley_benton_st_20_472390.htm",
                    "https://www.thomann.de/intl/fender_strat.htm"], urls
    assert article_from_url(urls[0]) == "472390"
    assert page_url("https://x/st_models.html", 2) == "https://x/st_models.html?ls=50&pg=2"
    print("self-test OK: subcategory + product extraction, leaf/landing split")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Collect product URLs by crawling Thomann categories")
    ap.add_argument("--db", default="products.db")
    ap.add_argument("--categories", default="categories.json")
    ap.add_argument("--ls", type=int, default=50)
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--seed-category", default=None, help="Only crawl this top category")
    ap.add_argument("--max-leaves", type=int, default=None, help="Stop after N leaves (testing)")
    ap.add_argument("--reset-queue", action="store_true", help="Rebuild the category queue")
    ap.add_argument("--search-mode", action="store_true", help="Old global search.html crawl (capped)")
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    conn = init_db(args.db)
    session = get_session(args.proxy)
    try:
        if args.search_mode:
            added = crawl_search(session, conn, args.ls, args.delay, args.max_pages)
        else:
            added = crawl_categories(session, conn, args)
    except KeyboardInterrupt:
        conn.commit()
        log.warning("Interrupted — progress saved. Re-run to resume.")
        conn.close()
        return 130

    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    pend_cat = conn.execute("SELECT COUNT(*) FROM category_queue WHERE status='pending'").fetchone()[0]
    log.info("Done. Added %d this run. Products in DB: %d. Pending categories: %d",
             added, total, pend_cat)
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
