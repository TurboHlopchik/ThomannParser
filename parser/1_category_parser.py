#!/usr/bin/env python3
"""
Step 1: Parse Thomann category tree from cat.html
Output: categories.json — full tree with IDs, names, URLs, parent relationships

Usage:
    python3 1_category_parser.py
    python3 1_category_parser.py --url "https://www.thomann.de/intl/cat.html"
    python3 1_category_parser.py --output my_categories.json
"""

import argparse
import json
import logging
import re
import sys
import time
from typing import Optional

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
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

BASE_URL = "https://www.thomann.de"

# Promo/special category keywords to skip
PROMO_KEYWORDS = [
    "top seller", "bestseller", "top 10", "top 15", "top 20",
    "new arrivals", "sale", "outlet", "deals", "specials",
    "featured", "recommended", "bundle", "starter", "value",
    "top artikel", "neu eingetroffen",
]


def is_promo_category(name: str) -> bool:
    name_lower = name.lower()
    return any(kw in name_lower for kw in PROMO_KEYWORDS)


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    # Warm up via homepage
    try:
        resp = session.get(BASE_URL + "/intl/", timeout=20)
        if resp.status_code == 200:
            log.info("Session warmed up (cookies: %d)", len(session.cookies))
        time.sleep(1)
    except Exception as e:
        log.warning("Warmup failed: %s", e)
    return session


def fetch_page(session: requests.Session, url: str) -> Optional[BeautifulSoup]:
    try:
        resp = session.get(url, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        if resp.status_code == 403:
            deny = resp.headers.get("x-deny-reason", "")
            if deny == "host_not_allowed":
                log.error("IP blocked. Run from home internet or use --proxy.")
                sys.exit(1)
        log.warning("HTTP %s for %s", resp.status_code, url)
        return None
    except Exception as e:
        log.error("Request error: %s", e)
        return None


def extract_category_id(url: str) -> str:
    """Extract numeric ID or slug from URL."""
    m = re.search(r"/(\d+)\.html?$", url)
    if m:
        return m.group(1)
    m = re.search(r"/([^/]+)\.html?$", url)
    if m:
        return m.group(1)
    return url.split("/")[-1]


def parse_cat_page(soup: BeautifulSoup) -> list:
    """
    Parse the main cat.html page.
    Returns list of top-level categories with their subcategories.
    """
    categories = []

    # Thomann cat.html has a hierarchical list structure
    # Try multiple possible structures

    # Method 1: look for category sections with h2/h3 headings and lists
    cat_sections = soup.select(".category-nav, .cat-list, #cat-list, .catalog-categories")

    if not cat_sections:
        # Method 2: find all category links in a structured way
        cat_sections = soup.select("main, #content, .content")

    if not cat_sections:
        cat_sections = [soup]

    seen_urls = set()

    for section in cat_sections:
        # Find top-level category groups
        groups = section.select("li.top, .top-category, h2, h3")

        if not groups:
            # Fallback: parse all links hierarchically
            all_links = section.select("a[href*='/intl/']")
            for link in all_links:
                href = link.get("href", "")
                name = link.get_text(strip=True)
                if not name or not href or is_promo_category(name):
                    continue
                if not href.endswith((".html", ".htm")):
                    continue
                full_url = href if href.startswith("http") else BASE_URL + href
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                categories.append({
                    "id": extract_category_id(full_url),
                    "name": name,
                    "url": full_url,
                    "level": 1,
                    "parent_id": None,
                    "subcategories": [],
                })

    return categories


def parse_category_page(session: requests.Session, cat: dict, level: int = 1) -> dict:
    """
    Visit a category page and find subcategories.
    Returns the category dict with subcategories populated.
    """
    if level > 4:
        return cat

    soup = fetch_page(session, cat["url"])
    if not soup:
        return cat

    time.sleep(1.5)

    subcats = []
    seen = set()

    # Look for subcategory navigation blocks
    selectors = [
        ".subcategory a",
        ".sub-categories a",
        ".category-filter a",
        "nav.categories a",
        ".refinement-nav a",
        "[class*='subcat'] a",
        "[class*='subcategory'] a",
        ".category-list a",
        ".facet-nav a[href*='.html']",
    ]

    links = []
    for sel in selectors:
        found = soup.select(sel)
        if found:
            links = found
            break

    if not links:
        # Fallback: look for links that match the current URL pattern
        base_path = "/" + "/".join(cat["url"].split("/")[3:-1]) + "/"
        links = soup.select(f"a[href*='{base_path}']")

    for link in links:
        href = link.get("href", "")
        name = link.get_text(strip=True)
        if not name or not href:
            continue
        if is_promo_category(name):
            continue
        if not (href.endswith(".html") or href.endswith(".htm")):
            continue
        full_url = href if href.startswith("http") else BASE_URL + href
        if full_url == cat["url"] or full_url in seen:
            continue
        seen.add(full_url)
        subcats.append({
            "id": extract_category_id(full_url),
            "name": name,
            "url": full_url,
            "level": level + 1,
            "parent_id": cat["id"],
            "subcategories": [],
        })

    log.info("%s  L%d '%s' → %d subcats", "  " * level, level, cat["name"], len(subcats))
    cat["subcategories"] = subcats
    return cat


def build_tree_from_cat_page(session: requests.Session, cat_url: str) -> list:
    """Fetch the main catalog page and build the full category tree."""
    log.info("Fetching main catalog page: %s", cat_url)
    soup = fetch_page(session, cat_url)
    if not soup:
        log.error("Failed to fetch catalog page")
        sys.exit(1)
    return build_tree_from_soup(soup)


def build_tree_from_soup(soup: BeautifulSoup) -> list:
    """
    Parse the main catalog page soup and build the full category tree.
    Uses a different approach: parse the sitemap-style cat.html directly.

    Pure (no network) so it can be exercised offline via --html-file / --self-test.
    """
    categories = []
    seen_urls = set()

    # Thomann cat.html typically has a list of all categories in a tree
    # Look for the main catalog list
    main_list = (
        soup.select_one("#catalog, .catalog, .category-tree, .all-categories") or
        soup.select_one("main") or
        soup
    )

    # Get all section headings (top-level categories)
    # Usually h2 or strong tags within list items
    top_items = main_list.select("li.top, .top-level-cat, h2 + ul > li")

    if top_items:
        for item in top_items:
            heading = item.select_one("a, strong, h2, h3")
            if not heading:
                continue
            name = heading.get_text(strip=True)
            href = heading.get("href", "") if heading.name == "a" else ""
            if is_promo_category(name):
                continue

            cat = {
                "id": extract_category_id(href) if href else re.sub(r"\W+", "-", name.lower()),
                "name": name,
                "url": (BASE_URL + href) if href and not href.startswith("http") else href,
                "level": 1,
                "parent_id": None,
                "subcategories": [],
            }

            # Find sub-items within this section
            sub_links = item.select("ul a")
            for link in sub_links:
                sub_href = link.get("href", "")
                sub_name = link.get_text(strip=True)
                if not sub_name or not sub_href or is_promo_category(sub_name):
                    continue
                full_url = sub_href if sub_href.startswith("http") else BASE_URL + sub_href
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                cat["subcategories"].append({
                    "id": extract_category_id(full_url),
                    "name": sub_name,
                    "url": full_url,
                    "level": 2,
                    "parent_id": cat["id"],
                    "subcategories": [],
                })

            categories.append(cat)
    else:
        # Flat approach: get all category links and infer hierarchy from URL depth
        all_links = main_list.select("a[href]")
        top_cats = {}

        for link in all_links:
            href = link.get("href", "")
            name = link.get_text(strip=True)

            if not name or not href or len(name) < 2:
                continue
            if is_promo_category(name):
                continue
            if not (href.endswith(".html") or href.endswith(".htm")):
                continue
            if "thomann.de" not in href and not href.startswith("/"):
                continue

            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            # Determine depth from URL path
            path_parts = [p for p in full_url.replace(BASE_URL, "").split("/") if p]
            level = len(path_parts)

            cat_entry = {
                "id": extract_category_id(full_url),
                "name": name,
                "url": full_url,
                "level": level,
                "parent_id": None,
                "subcategories": [],
            }

            if level == 2:  # e.g. /intl/guitars.html
                top_cats[full_url] = cat_entry
                categories.append(cat_entry)
            elif level >= 3:
                # Find parent
                parent_url = "/".join(full_url.split("/")[:-1]) + ".html"
                parent = top_cats.get(parent_url)
                if parent:
                    cat_entry["parent_id"] = parent["id"]
                    parent["subcategories"].append(cat_entry)
                    top_cats[full_url] = cat_entry
                else:
                    # Orphan — add as top level
                    categories.append(cat_entry)

    log.info("Found %d top-level categories", len(categories))
    return categories


def flatten_categories(tree: list, result: list = None) -> list:
    """Flatten tree to list for easy processing."""
    if result is None:
        result = []
    for cat in tree:
        result.append({k: v for k, v in cat.items() if k != "subcategories"})
        if cat.get("subcategories"):
            flatten_categories(cat["subcategories"], result)
    return result


def count_categories(tree: list) -> int:
    total = 0
    for cat in tree:
        total += 1
        if cat.get("subcategories"):
            total += count_categories(cat["subcategories"])
    return total


def save_output(tree: list, source_url: str, output_path: str):
    """Write the category tree (+ flat list) to a JSON file and log a summary."""
    total = count_categories(tree)
    log.info("Total categories in tree: %d", total)

    output = {
        "source_url": source_url,
        "total_categories": total,
        "top_level_count": len(tree),
        "tree": tree,
        "flat": flatten_categories(tree),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("Saved to %s", output_path)
    log.info("Top-level categories:")
    for cat in tree:
        log.info("  [%d subcats] %s", len(cat.get("subcategories", [])), cat["name"])


# Sample resembling Thomann's cat.html (flat single-segment .html links plus a
# promo entry that must be skipped). Used by --self-test to validate parsing
# without hitting the network.
_SELF_TEST_HTML = """
<html><body><main>
  <a href="/intl/guitars_and_basses.html">Guitars and Basses</a>
  <a href="/intl/guitars_and_basses/electric.html">Electric Guitars</a>
  <a href="/intl/drums_and_percussion.html">Drums and Percussion</a>
  <a href="/intl/hot_deals.html">Hot Deals</a>
  <a href="https://www.facebook.com/thomann">Facebook</a>
</main></body></html>
"""


def self_test() -> int:
    """Run built-in parser checks against a sample page (no network)."""
    assert extract_category_id("https://www.thomann.de/intl/electric_guitars.html") \
        == "electric_guitars"
    assert is_promo_category("Hot Deals") is True
    assert is_promo_category("Guitars and Basses") is False

    soup = BeautifulSoup(_SELF_TEST_HTML, "lxml")
    tree = build_tree_from_soup(soup)

    names = [c["name"] for c in tree]
    assert names == ["Guitars and Basses", "Drums and Percussion"], names
    # Deeper (multi-segment) URL is nested under its parent.
    assert len(tree[0]["subcategories"]) == 1, tree[0]["subcategories"]
    assert tree[0]["subcategories"][0]["name"] == "Electric Guitars"
    # Promo ("Hot Deals") and the non-catalog Facebook link are dropped.
    assert "Hot Deals" not in names
    assert count_categories(tree) == 3

    log.info("self-test OK: parsing, promo-filtering and nesting behave as expected")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Parse Thomann category tree")
    parser.add_argument("--url", default="https://www.thomann.de/intl/cat.html")
    parser.add_argument("--output", default="categories.json")
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--html-file", default=None,
                        help="Parse a saved cat.html instead of fetching (offline).")
    parser.add_argument("--self-test", action="store_true",
                        help="Run built-in parser tests and exit (no network).")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.html_file:
        log.info("Parsing local HTML file: %s", args.html_file)
        with open(args.html_file, encoding="utf-8", errors="replace") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        tree = build_tree_from_soup(soup)
        if not tree:
            log.warning("No categories extracted — selectors may need tuning for "
                        "this page; inspect the HTML structure.")
        save_output(tree, f"file://{args.html_file}", args.output)
        return 0

    session = get_session()
    if args.proxy:
        session.proxies = {"http": args.proxy, "https": args.proxy}

    tree = build_tree_from_cat_page(session, args.url)
    save_output(tree, args.url, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
