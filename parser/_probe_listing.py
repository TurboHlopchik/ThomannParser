#!/usr/bin/env python3
"""
Throwaway diagnostic: figure out how Thomann serves the full product list.

Fetches a few candidate listing URLs from a RESIDENTIAL connection and reports,
for each, how many product links are server-rendered in the main grid
(div.js-articles), the total product links, and whether pagination changes the
results. Run locally (the cloud IP is blocked), paste the output back.

    python3 _probe_listing.py
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://www.thomann.de"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

CANDIDATES = [
    # Does a category page render the full list when paginated (like search.html)?
    "/intl/electric_guitars.html?ls=50&pg=1",
    "/intl/electric_guitars.html?ls=50&pg=2",
    "/intl/electric_guitars.html?ls=50&pg=3",
    # A deeper leaf category:
    "/intl/st_models.html?ls=50&pg=1",
    "/intl/st_models.html?ls=50&pg=2",
]
PROBE_DELAY = 4  # be gentle: avoid Cloudflare 429


def grid_products(soup):
    grid = soup.select_one("div.js-articles")
    hrefs = []
    if grid:
        for a in grid.select("a[href*='.htm']"):
            h = a["href"].split("?")[0]
            if ".html" not in h and h not in hrefs:
                hrefs.append(h)
    return hrefs


def all_products(soup):
    out = []
    for a in soup.find_all("a", href=True):
        h = a["href"].split("?")[0]
        if re.search(r"/?[a-z0-9_]+\.htm$", h) and h not in out:
            out.append(h)
    return out


def non_carousel_products(soup):
    """Product .htm links that are NOT inside a carousel (recommendations)."""
    out = []
    for a in soup.find_all("a", href=True):
        h = a["href"].split("?")[0]
        if not re.search(r"/?[a-z0-9_]+\.htm$", h):
            continue
        if a.find_parent(class_=re.compile("carousel")):
            continue
        if h not in out:
            out.append(h)
    return out


def main():
    s = requests.Session()
    s.headers.update(HEADERS)
    # warm up
    try:
        s.get(BASE + "/intl/", timeout=20)
    except Exception as e:
        print("warmup failed:", e)
    time.sleep(1)

    for path in CANDIDATES:
        url = BASE + path
        s.headers["Referer"] = BASE + "/intl/"
        try:
            r = s.get(url, timeout=25)
        except Exception as e:
            print(f"\n{path}\n  ERROR {e}")
            time.sleep(2)
            continue
        info = f"HTTP {r.status_code}"
        if r.status_code == 403:
            info += f" deny={r.headers.get('x-deny-reason')}"
        soup = BeautifulSoup(r.text, "lxml")
        g = grid_products(soup)
        a = all_products(soup)
        nc = non_carousel_products(soup)
        title = (soup.title.get_text(strip=True) if soup.title else "")[:50]
        print(f"\n{path}")
        print(f"  {info} | bytes={len(r.text)} | title={title!r}")
        print(f"  grid(js-articles): {len(g)} | non-carousel .htm: {len(nc)} | all .htm: {len(a)}")
        print(f"  first 3 non-carousel hrefs: {nc[:3]}")
        time.sleep(PROBE_DELAY)


if __name__ == "__main__":
    sys.exit(main())
