#!/usr/bin/env python3
"""
Step 2: Collect all product URLs from Thomann's global search listing.

Thomann's category pages (electric_guitars.html, ...) are JS-rendered landing
pages that only server-render a handful of products, so they cannot be scraped
with requests.  The global listing at /intl/search.html, however, server-renders
the full catalogue 50 products per page with working pagination:

    https://www.thomann.de/intl/search.html?ls=50&pg=2

This step paginates through it and stores every product URL into products.db
(status = 'pending').  The crawl is resumable: the last completed page is saved,
so Ctrl+C and re-run with --resume continues where it left off.  Per-product
category is left empty here and filled later from the product page's breadcrumb
in step 3.

Usage:
    python3 2_url_collector.py                       # crawl the whole catalogue
    python3 2_url_collector.py --max-pages 20        # only 20 pages (testing)
    python3 2_url_collector.py --resume              # continue from last page
    python3 2_url_collector.py --html-file search.html   # offline parse test
    python3 2_url_collector.py --self-test
"""

import argparse
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
SEARCH_PATH = "/intl/search.html"
# A product detail page is a single-segment slug ending in .htm (not .html).
_PRODUCT_RE = re.compile(r"^/intl/[a-z0-9][a-z0-9_.%-]*\.htm$", re.I)


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
    # Kept for backwards-compatibility with older databases.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories_done (
            category_id TEXT PRIMARY KEY,
            url TEXT,
            products_found INTEGER,
            done_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Simple key/value store for resumable crawl progress.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS crawl_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON products(status)")
    conn.commit()
    return conn


def get_state(conn, key, default=None):
    row = conn.execute("SELECT value FROM crawl_state WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_state(conn, key, value):
    conn.execute(
        "INSERT INTO crawl_state (key, value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


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
    """Fetch a page with throttling, IP-block detection and 429 back-off.

    Returns a BeautifulSoup on success, or None on a non-recoverable error.
    Exits the process on Thomann's host_not_allowed block.
    """
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
            # Cloudflare interstitial sometimes returns 200 with a challenge page.
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


def search_url(page: int, ls: int = 50) -> str:
    return f"{BASE_URL}{SEARCH_PATH}?ls={ls}&pg={page}"


def extract_product_urls(soup: BeautifulSoup, base_url: str = BASE_URL + SEARCH_PATH) -> list:
    """Return absolute product detail URLs from a search results page.

    Products are single-segment '.htm' links; recommendation carousels are
    excluded so only the actual result list is collected.
    """
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


def detect_total_pages(soup: BeautifulSoup, ls: int) -> Optional[int]:
    """Best-effort total page count from the result-count text, if present.

    Picks the LARGEST number that precedes a results/items keyword (the
    catalogue total, e.g. '124,152 results'), ignoring small incidental counts.
    """
    text = soup.get_text(" ", strip=True)
    counts = []
    for m in re.finditer(r"(\d[\d,.]{2,})\s*(?:results|items|Artikel|products)", text, re.I):
        digits = re.sub(r"[^\d]", "", m.group(1))
        if digits:
            counts.append(int(digits))
    if not counts:
        return None
    total = max(counts)
    if total <= ls:
        return None
    return -(-total // ls)  # ceil


def crawl_search(session, conn, ls, start_page, max_pages, delay) -> int:
    page = start_page
    last_page = start_page + max_pages - 1 if max_pages else None
    added_total = 0
    empty_streak = 0
    repeat_streak = 0
    total_pages = None
    seen_this_run = set()  # detect Thomann repeating pages at the real end/cap

    while True:
        if last_page and page > last_page:
            log.info("Reached page limit (%d)", last_page)
            break

        soup = fetch(session, search_url(page, ls), delay)
        if soup is None:
            log.warning("Page %d failed; stopping (resume with --resume)", page)
            break

        if total_pages is None:
            total_pages = detect_total_pages(soup, ls)
            if total_pages:
                log.info("Catalogue spans ~%d pages (ls=%d)", total_pages, ls)

        urls = extract_product_urls(soup)
        if not urls:
            empty_streak += 1
            log.info("Page %d: 0 products (empty streak %d)", page, empty_streak)
            if empty_streak >= 2:
                log.info("Two empty pages in a row — assuming end of catalogue.")
                break
            page += 1
            continue
        empty_streak = 0

        # Stop when the listing starts repeating pages we've already walked THIS
        # run (Thomann caps deep pagination by re-serving the last page). This is
        # independent of what's already in the DB, so re-runs don't stop early.
        fresh = [u for u in urls if u not in seen_this_run]
        if not fresh:
            repeat_streak += 1
            log.info("Page %d: all %d already seen this run (repeat streak %d)",
                     page, len(urls), repeat_streak)
            if repeat_streak >= 2:
                log.info("Listing is repeating — reached the end of the catalogue.")
                break
            page += 1
            continue
        repeat_streak = 0
        seen_this_run.update(urls)

        added = 0
        for purl in urls:
            cur = conn.execute(
                "INSERT OR IGNORE INTO products (url, article, status) VALUES (?,?, 'pending')",
                (purl, article_from_url(purl)),
            )
            added += cur.rowcount
        added_total += added
        set_state(conn, "search_last_page", page)
        conn.commit()

        suffix = f"/{total_pages}" if total_pages else ""
        log.info("Page %d%s: %d products, +%d new to DB (%d new this run)",
                 page, suffix, len(urls), added, len(seen_this_run))

        page += 1

    return added_total


# ─── Offline test helpers ─────────────────────────────────────────────────────

_SELF_TEST_HTML = """
<html><body>
  <div class="fx-carousel"><a href="recommended_product.htm">Reco</a></div>
  <ul class="search-results">
    <li><a href="peavey_112_1x12_cab.htm">Peavey 112</a></li>
    <li><a href="gibson_les_paul_standard_60s_aaa_lb.htm">Gibson LP</a></li>
    <li><a href="harley_benton_st_20_bk_472390.htm">HB ST-20</a></li>
  </ul>
  <a href="electric_guitars.html">a category (ignored)</a>
  <a href="peavey_112_1x12_cab.htm">duplicate</a>
</body></html>
"""


def self_test() -> int:
    soup = BeautifulSoup(_SELF_TEST_HTML, "lxml")
    urls = extract_product_urls(soup)
    assert urls == [
        "https://www.thomann.de/intl/peavey_112_1x12_cab.htm",
        "https://www.thomann.de/intl/gibson_les_paul_standard_60s_aaa_lb.htm",
        "https://www.thomann.de/intl/harley_benton_st_20_bk_472390.htm",
    ], urls
    assert article_from_url("https://www.thomann.de/intl/harley_benton_st_20_bk_472390.htm") == "472390"
    assert article_from_url("https://www.thomann.de/intl/peavey_112_1x12_cab.htm") == ""
    assert search_url(2) == "https://www.thomann.de/intl/search.html?ls=50&pg=2"
    print("self-test OK: product extraction, carousel exclusion and paging URLs")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Collect product URLs from Thomann search.html")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--ls", type=int, default=50, help="Products per page (Thomann: 25/50/100)")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit number of pages (testing)")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--resume", action="store_true", help="Continue from the last completed page")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--html-file", default=None, help="Parse a saved search.html (offline)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.html_file:
        with open(args.html_file, encoding="utf-8", errors="replace") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        urls = extract_product_urls(soup)
        log.info("Extracted %d product URLs from %s", len(urls), args.html_file)
        for u in urls[:20]:
            print("  ", u)
        return 0

    conn = init_db(args.db)
    session = get_session(args.proxy)

    start_page = args.start_page
    if args.resume:
        last = get_state(conn, "search_last_page")
        if last:
            start_page = int(last) + 1
            log.info("Resuming from page %d", start_page)

    log.info("Collecting product URLs from %s (ls=%d, from page %d)",
             BASE_URL + SEARCH_PATH, args.ls, start_page)
    try:
        added = crawl_search(session, conn, args.ls, start_page, args.max_pages, args.delay)
    except KeyboardInterrupt:
        conn.commit()
        log.warning("Interrupted — progress saved. Re-run with --resume to continue.")
        conn.close()
        return 130

    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    log.info("Done. Added %d new URLs this run. Total product URLs in DB: %d", added, total)
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
