#!/usr/bin/env python3
"""
Thomann.de product parser → MODX MiniShop import file (CSV + XML).

Usage:
    python3 thomann_parser.py --url "https://www.thomann.de/gb/guitars.html"
    python3 thomann_parser.py --url "https://www.thomann.de/gb/guitars.html" --pages 5
    python3 thomann_parser.py --product "https://www.thomann.de/gb/gibson_les_paul_standard_50s.htm"
    python3 thomann_parser.py --file urls.txt --output my_products

Options:
    --url       Category URL to scrape (paginates automatically)
    --product   Single product URL
    --file      Text file with product or category URLs, one per line
    --pages     Max pages to scrape per category (default: all)
    --output    Output filename base (default: thomann_import)
    --format    Output format: csv, xml, both (default: both)
    --delay     Delay between requests in seconds (default: 2)
    --proxy     HTTP proxy URL (optional)
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse
from xml.dom import minidom

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9,de;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Cache-Control": "max-age=0",
}

BASE_URL = "https://www.thomann.de"


@dataclass
class Product:
    url: str = ""
    article: str = ""          # SKU / article number
    pagetitle: str = ""        # product name
    longtitle: str = ""        # brand + model
    alias: str = ""            # URL slug
    description: str = ""      # short description
    content: str = ""          # full HTML description
    price: str = ""            # current price
    old_price: str = ""        # before-discount price
    image: str = ""            # main image URL
    gallery: list = field(default_factory=list)   # additional images
    category: str = ""         # breadcrumb path
    properties: dict = field(default_factory=dict)  # technical specs
    brand: str = ""
    rating: str = ""
    reviews_count: str = ""
    availability: str = ""
    weight: str = ""
    tags: str = ""


class ThomannSession:
    def __init__(self, delay: float = 2.0, proxy: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self._last_request = 0
        self._warmed_up = False

    def warmup(self):
        """Visit homepage to obtain cookies and look like a real browser."""
        if self._warmed_up:
            return
        log.info("Warming up session via Thomann homepage...")
        try:
            resp = self.session.get(BASE_URL + "/gb/", timeout=20)
            self._last_request = time.time()
            if resp.status_code == 200:
                # Accept cookie consent if present
                if "cookieconsent" in resp.text or "cookie" in resp.text.lower():
                    # POST consent acceptance (common Thomann endpoint)
                    self.session.post(
                        BASE_URL + "/gb/cookie-consent-save.html",
                        data={"consent": "all"},
                        timeout=10,
                    )
                self._warmed_up = True
                log.info("Session warmed up (cookies: %d)", len(self.session.cookies))
            else:
                log.warning("Warmup returned HTTP %s", resp.status_code)
        except Exception as exc:
            log.warning("Warmup failed: %s", exc)
        time.sleep(1)

    def get(self, url: str) -> Optional[BeautifulSoup]:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.warmup()
        try:
            self.session.headers["Referer"] = BASE_URL + "/gb/"
            resp = self.session.get(url, timeout=20)
            self._last_request = time.time()
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "lxml")
            if resp.status_code == 403:
                deny = resp.headers.get("x-deny-reason", "unknown")
                if deny == "host_not_allowed":
                    log.error(
                        "IP/host blocked by Thomann (x-deny-reason: host_not_allowed). "
                        "Run from a residential IP or use --proxy with a residential proxy."
                    )
                    raise SystemExit(1)
                log.warning("HTTP 403 for %s (reason: %s)", url, deny)
            else:
                log.warning("HTTP %s for %s", resp.status_code, url)
            return None
        except SystemExit:
            raise
        except Exception as exc:
            log.error("Request failed for %s: %s", url, exc)
            return None


def clean_price(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[^\d,.]", "", text.strip())
    cleaned = cleaned.replace(",", ".")
    try:
        return str(float(cleaned))
    except ValueError:
        return cleaned


def make_alias(title: str) -> str:
    alias = title.lower()
    alias = re.sub(r"[^\w\s-]", "", alias)
    alias = re.sub(r"[\s_]+", "-", alias)
    alias = re.sub(r"-+", "-", alias).strip("-")
    return alias[:100]


def parse_product(soup: BeautifulSoup, url: str) -> Product:
    p = Product(url=url)

    # --- Title / brand ---
    title_el = soup.select_one("h1.product-title, h1[class*='title']")
    if not title_el:
        title_el = soup.select_one("h1")
    if title_el:
        p.pagetitle = title_el.get_text(strip=True)
        p.alias = make_alias(p.pagetitle)

    brand_el = soup.select_one("span[class*='brand'], a[class*='brand'], .product-brand")
    if brand_el:
        p.brand = brand_el.get_text(strip=True)
        p.longtitle = f"{p.brand} {p.pagetitle}".strip()
    else:
        p.longtitle = p.pagetitle

    # --- Article number ---
    art_el = soup.select_one("[class*='article-number'], [class*='product-id']")
    if art_el:
        p.article = re.sub(r"[^\d]", "", art_el.get_text())
    # fallback: extract from URL
    if not p.article:
        m = re.search(r"(\d{6,})", url)
        if m:
            p.article = m.group(1)

    # --- Price ---
    price_el = soup.select_one(
        ".product-price__main-price, [class*='price--current'], "
        ".our-price, .price-tag, [data-testid='price']"
    )
    if not price_el:
        price_el = soup.select_one(".fx-product-stage-price__sale")
    if price_el:
        p.price = clean_price(price_el.get_text())

    old_el = soup.select_one(
        "[class*='price--old'], [class*='price--before'], .price-before, "
        ".fx-product-stage-price__uvp"
    )
    if old_el:
        p.old_price = clean_price(old_el.get_text())

    # --- Images ---
    # Main image
    main_img = soup.select_one(
        ".product-image img, .main-image img, "
        "[class*='product-images'] img[class*='main'], "
        ".pdp-image__main img"
    )
    if not main_img:
        main_img = soup.select_one(".product-stage img, [class*='stage'] img")
    if main_img:
        p.image = main_img.get("data-src") or main_img.get("src", "")
        if p.image.startswith("//"):
            p.image = "https:" + p.image

    # Gallery images
    gallery_imgs = soup.select(
        ".product-images__thumbnails img, "
        "[class*='thumb'] img, "
        ".gallery img, "
        "[class*='gallery'] img"
    )
    seen = {p.image}
    for img in gallery_imgs:
        src = img.get("data-src") or img.get("src") or ""
        # try to get full-size from thumbnail URL
        src = re.sub(r"_\d+x\d+\.", ".", src)
        if src.startswith("//"):
            src = "https:" + src
        if src and src not in seen:
            seen.add(src)
            p.gallery.append(src)

    # --- Description ---
    desc_el = soup.select_one(
        ".product-description, [class*='description--short'], "
        ".fx-pdp-teaser, .product-teaser"
    )
    if desc_el:
        p.description = desc_el.get_text(separator=" ", strip=True)[:500]

    content_el = soup.select_one(
        "[class*='description-text'], .product-detail-description, "
        ".product-detail__description, .pdp-description"
    )
    if not content_el:
        content_el = desc_el
    if content_el:
        p.content = str(content_el)

    # --- Technical specs / properties ---
    spec_tables = soup.select(
        "table[class*='specifications'], "
        ".product-features table, "
        "[class*='spec'] table, "
        "table.features"
    )
    if not spec_tables:
        # try dl/dt/dd pattern
        spec_dls = soup.select("dl[class*='spec'], .product-features dl")
        for dl in spec_dls:
            keys = dl.select("dt")
            vals = dl.select("dd")
            for k, v in zip(keys, vals):
                key = k.get_text(strip=True)
                val = v.get_text(strip=True)
                if key:
                    p.properties[key] = val

    for table in spec_tables:
        for row in table.select("tr"):
            cells = row.select("th, td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key:
                    p.properties[key] = val

    # Also try generic feature lists
    if not p.properties:
        feature_items = soup.select(
            "[class*='features__item'], [class*='feature-list'] li"
        )
        for item in feature_items:
            label = item.select_one("[class*='label'], strong, b")
            value = item.select_one("[class*='value']")
            if label and value:
                p.properties[label.get_text(strip=True)] = value.get_text(strip=True)
            elif item.get_text(strip=True):
                p.properties[f"feature_{len(p.properties)+1}"] = item.get_text(strip=True)

    # --- Breadcrumb / category ---
    crumbs = soup.select(
        "nav[class*='breadcrumb'] a, "
        "[class*='breadcrumbs'] a, "
        ".breadcrumb a"
    )
    if crumbs:
        p.category = " > ".join(c.get_text(strip=True) for c in crumbs[1:])  # skip home

    # --- Rating ---
    rating_el = soup.select_one("[class*='rating__value'], [class*='stars__value'], [itemprop='ratingValue']")
    if rating_el:
        p.rating = rating_el.get("content") or rating_el.get_text(strip=True)

    reviews_el = soup.select_one("[class*='rating__count'], [itemprop='reviewCount']")
    if reviews_el:
        p.reviews_count = re.sub(r"[^\d]", "", reviews_el.get_text())

    # --- Availability ---
    avail_el = soup.select_one("[class*='availability'], [class*='stock'], .delivery-info")
    if avail_el:
        p.availability = avail_el.get_text(strip=True)[:100]

    return p


def get_category_product_urls(
    soup: BeautifulSoup, base_url: str
) -> list:
    urls = []
    # Try multiple selectors for product links in category listings
    selectors = [
        "article.product a.product__link",
        "a[class*='product-link']",
        "a[class*='product__link']",
        ".product-list a[href*='.htm']",
        "a[data-testid='product-link']",
        ".product a[href*='.htm']:not([href*='#'])",
    ]
    seen = set()
    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href", "")
            if href and ".htm" in href:
                full = urljoin(base_url, href)
                # Remove query params for uniqueness
                clean = full.split("?")[0]
                if clean not in seen and "thomann.de" in full:
                    seen.add(clean)
                    urls.append(clean)
        if urls:
            break
    return urls


def get_next_page_url(soup: BeautifulSoup, current_url: str) -> Optional[str]:
    next_el = soup.select_one(
        "a[rel='next'], "
        "a[class*='pagination__next'], "
        "a[class*='next-page'], "
        ".pagination a[aria-label*='next' i]"
    )
    if next_el:
        href = next_el.get("href", "")
        if href:
            return urljoin(current_url, href)

    # fallback: find current page number and increment
    m = re.search(r"[?&]pg=(\d+)", current_url)
    if m:
        page_num = int(m.group(1)) + 1
        return re.sub(r"([?&]pg=)\d+", rf"\g<1>{page_num}", current_url)

    m = re.search(r"(/pg)(\d+)(\b|\.)", current_url)
    if m:
        page_num = int(m.group(2)) + 1
        return re.sub(r"(/pg)\d+", rf"\g<1>{page_num}", current_url)

    return None


def is_category_page(soup: BeautifulSoup) -> bool:
    return bool(
        soup.select_one(
            ".product-list, [class*='listing'], "
            "article.product, [class*='product-list']"
        )
    )


def scrape_urls(
    session: ThomannSession,
    start_urls: list,
    max_pages: Optional[int] = None,
) -> list:
    products = []
    visited_products = set()
    visited_categories = set()

    for start_url in start_urls:
        soup = session.get(start_url)
        if not soup:
            log.warning("Could not fetch %s", start_url)
            continue

        if is_category_page(soup):
            # Paginate and collect product URLs
            cat_url = start_url
            page = 1
            while cat_url:
                if cat_url in visited_categories:
                    break
                visited_categories.add(cat_url)
                log.info("Category page %d: %s", page, cat_url)

                if page > 1:
                    soup = session.get(cat_url)
                    if not soup:
                        break

                product_urls = get_category_product_urls(soup, cat_url)
                log.info("  Found %d products on this page", len(product_urls))

                for purl in product_urls:
                    if purl not in visited_products:
                        visited_products.add(purl)
                        psoup = session.get(purl)
                        if psoup:
                            product = parse_product(psoup, purl)
                            products.append(product)
                            log.info("  Parsed: %s (article: %s)", product.pagetitle, product.article)

                if max_pages and page >= max_pages:
                    break
                next_url = get_next_page_url(soup, cat_url)
                if not next_url or next_url == cat_url:
                    break
                cat_url = next_url
                page += 1
        else:
            # Treat as product page
            if start_url not in visited_products:
                visited_products.add(start_url)
                product = parse_product(soup, start_url)
                products.append(product)
                log.info("Parsed product: %s (article: %s)", product.pagetitle, product.article)

    return products


# ─── Output formatters ────────────────────────────────────────────────────────

# MiniShop CSV columns
CSV_FIELDS = [
    "pagetitle", "longtitle", "alias", "description", "content",
    "price", "old_price", "article", "image", "gallery",
    "category", "brand", "rating", "reviews_count",
    "availability", "properties", "url",
]


def products_to_csv(products: list, filepath: str):
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for p in products:
            row = {
                "pagetitle": p.pagetitle,
                "longtitle": p.longtitle,
                "alias": p.alias,
                "description": p.description,
                "content": p.content,
                "price": p.price,
                "old_price": p.old_price,
                "article": p.article,
                "image": p.image,
                "gallery": "||".join(p.gallery),
                "category": p.category,
                "brand": p.brand,
                "rating": p.rating,
                "reviews_count": p.reviews_count,
                "availability": p.availability,
                "properties": json.dumps(p.properties, ensure_ascii=False),
                "url": p.url,
            }
            writer.writerow(row)
    log.info("CSV saved: %s (%d products)", filepath, len(products))


def products_to_xml(products: list, filepath: str):
    """
    Generates XML compatible with MiniShop2 msProducts import.
    Structure follows the standard used by msImport extra.
    """
    root = ET.Element("products")

    for p in products:
        item = ET.SubElement(root, "product")

        def sub(tag, text):
            el = ET.SubElement(item, tag)
            el.text = str(text) if text else ""
            return el

        sub("pagetitle", p.pagetitle)
        sub("longtitle", p.longtitle)
        sub("alias", p.alias)
        sub("description", p.description)
        sub("content", p.content)
        sub("price", p.price)
        sub("old_price", p.old_price)
        sub("article", p.article)
        sub("image", p.image)
        sub("brand", p.brand)
        sub("rating", p.rating)
        sub("reviews_count", p.reviews_count)
        sub("availability", p.availability)
        sub("category", p.category)
        sub("source_url", p.url)

        # Gallery
        gallery_el = ET.SubElement(item, "gallery")
        for img_url in p.gallery:
            img_el = ET.SubElement(gallery_el, "image")
            img_el.text = img_url

        # Properties / specs
        props_el = ET.SubElement(item, "properties")
        for key, val in p.properties.items():
            prop_el = ET.SubElement(props_el, "property")
            prop_el.set("name", key)
            prop_el.text = str(val)

    # Pretty-print XML
    xml_str = minidom.parseString(ET.tostring(root, encoding="unicode")).toprettyxml(
        indent="  ", encoding=None
    )
    # Remove the auto-added XML declaration line (we'll add our own)
    lines = xml_str.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    xml_output = "\n".join(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_output)
    log.info("XML saved: %s (%d products)", filepath, len(products))


def save_json_debug(products: list, filepath: str):
    data = []
    for p in products:
        d = p.__dict__.copy()
        data.append(d)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("JSON debug saved: %s", filepath)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Thomann.de → MODX MiniShop2 import parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--url", help="Category or product URL")
    parser.add_argument("--product", help="Single product URL")
    parser.add_argument("--file", help="Text file with URLs, one per line")
    parser.add_argument("--pages", type=int, default=None, help="Max category pages (default: all)")
    parser.add_argument("--output", default="thomann_import", help="Output filename base")
    parser.add_argument("--format", choices=["csv", "xml", "both", "all"], default="both")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    parser.add_argument("--proxy", default=None, help="HTTP/HTTPS proxy URL")
    parser.add_argument("--debug", action="store_true", help="Also save raw JSON dump")
    args = parser.parse_args()

    # Collect start URLs
    start_urls = []
    if args.url:
        start_urls.append(args.url)
    if args.product:
        start_urls.append(args.product)
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    start_urls.append(line)

    if not start_urls:
        parser.print_help()
        sys.exit(1)

    session = ThomannSession(delay=args.delay, proxy=args.proxy)
    products = scrape_urls(session, start_urls, max_pages=args.pages)

    if not products:
        log.warning("No products found.")
        sys.exit(0)

    log.info("Total products scraped: %d", len(products))

    out = args.output
    fmt = args.format

    if fmt in ("csv", "both", "all"):
        products_to_csv(products, f"{out}.csv")
    if fmt in ("xml", "both", "all"):
        products_to_xml(products, f"{out}.xml")
    if args.debug:
        save_json_debug(products, f"{out}_debug.json")

    log.info("Done.")


if __name__ == "__main__":
    main()
