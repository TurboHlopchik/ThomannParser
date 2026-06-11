#!/usr/bin/env python3
"""
Step 4: Translate product descriptions and specs to Russian.
Reads from products.db, writes translated fields back to products.db.

Supports: DeepL API, Claude API (Anthropic), Google Translate (free via deep_translator)

Usage:
    # DeepL (recommended, best quality)
    python3 4_translator.py --engine deepl --api-key YOUR_DEEPL_KEY

    # Claude API (Anthropic)
    python3 4_translator.py --engine claude --api-key YOUR_ANTHROPIC_KEY

    # Google Translate (free, no key needed, lower quality)
    python3 4_translator.py --engine google

    # Limit for testing
    python3 4_translator.py --engine deepl --api-key KEY --limit 10

    # Only a specific category
    python3 4_translator.py --engine deepl --api-key KEY --category "Guitars"
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ─── DeepL ────────────────────────────────────────────────────────────────────

def translate_deepl(texts: list, api_key: str, target_lang: str = "RU") -> list:
    """Translate a batch of texts via DeepL API. Returns list of translated strings."""
    import requests
    url = "https://api-free.deepl.com/v2/translate"  # free tier endpoint
    results = []
    # DeepL supports up to 50 texts per request
    for i in range(0, len(texts), 50):
        batch = texts[i:i+50]
        payload = {
            "auth_key": api_key,
            "text": batch,
            "target_lang": target_lang,
            "source_lang": "EN",
            "tag_handling": "html",  # preserve HTML tags in content
        }
        try:
            resp = requests.post(url, data=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                results.extend(t["text"] for t in data["translations"])
            elif resp.status_code == 456:
                log.error("DeepL quota exceeded for this month")
                raise RuntimeError("DeepL quota exceeded")
            else:
                log.error("DeepL error %s: %s", resp.status_code, resp.text[:200])
                results.extend(batch)  # fallback: keep original
        except RuntimeError:
            raise
        except Exception as e:
            log.error("DeepL request failed: %s", e)
            results.extend(batch)
        time.sleep(0.3)
    return results


# ─── Claude API ───────────────────────────────────────────────────────────────

def translate_claude(texts: list, api_key: str) -> list:
    """Translate texts using Claude claude-haiku-4-5 API (cheapest model)."""
    try:
        import anthropic
    except ImportError:
        log.error("Install anthropic SDK: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    results = []

    # Batch texts together to reduce API calls (up to 20 per call)
    for i in range(0, len(texts), 20):
        batch = texts[i:i+20]
        numbered = "\n---\n".join(f"[{j+1}] {t}" for j, t in enumerate(batch))

        prompt = f"""Translate the following product description texts from English to Russian.
These are musical instrument product descriptions for an online store.
Keep technical terms, brand names, and model numbers unchanged.
Preserve any HTML tags if present.
Return only the translations numbered the same way, separated by ---

{numbered}"""

        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            response = msg.content[0].text
            # Parse numbered responses
            parts = re.split(r"\n---\n", response)
            for part in parts:
                part = re.sub(r"^\[\d+\]\s*", "", part.strip())
                if part:
                    results.append(part)
            # Pad if fewer results returned
            while len(results) < i + len(batch):
                results.append(batch[len(results) - i])
        except Exception as e:
            log.error("Claude API error: %s", e)
            results.extend(batch)  # fallback

        time.sleep(1)

    return results[:len(texts)]


# ─── Google Translate (free) ──────────────────────────────────────────────────

def translate_google(texts: list) -> list:
    """Translate using deep_translator (free Google Translate wrapper)."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        log.error("Install: pip install deep-translator")
        sys.exit(1)

    translator = GoogleTranslator(source="en", target="ru")
    results = []
    for text in texts:
        if not text or not text.strip():
            results.append(text)
            continue
        try:
            # Google Translate free limit: 5000 chars per request
            if len(text) > 4500:
                # Split into chunks
                chunks = [text[j:j+4500] for j in range(0, len(text), 4500)]
                translated_chunks = []
                for chunk in chunks:
                    translated_chunks.append(translator.translate(chunk))
                    time.sleep(0.5)
                results.append(" ".join(translated_chunks))
            else:
                results.append(translator.translate(text))
            time.sleep(0.3)
        except Exception as e:
            log.warning("Google translate error: %s", e)
            results.append(text)
    return results


# ─── Main translation logic ───────────────────────────────────────────────────

def translate_batch(texts: list, engine: str, api_key: Optional[str]) -> list:
    if engine == "deepl":
        return translate_deepl(texts, api_key)
    elif engine == "claude":
        return translate_claude(texts, api_key)
    elif engine == "google":
        return translate_google(texts)
    else:
        raise ValueError(f"Unknown engine: {engine}")


def translate_properties(props_json: str, engine: str, api_key: Optional[str]) -> str:
    """Translate keys and values in the properties JSON dict."""
    if not props_json:
        return props_json
    try:
        props = json.loads(props_json)
    except Exception:
        return props_json
    if not props:
        return props_json

    keys = list(props.keys())
    values = list(props.values())

    translated_keys = translate_batch(keys, engine, api_key)
    translated_values = translate_batch(values, engine, api_key)

    translated = {k: v for k, v in zip(translated_keys, translated_values)}
    return json.dumps(translated, ensure_ascii=False)


def init_db_columns(conn: sqlite3.Connection):
    """Add translated columns if missing."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(products)")}
    new_cols = {
        "pagetitle_ru": "TEXT",
        "longtitle_ru": "TEXT",
        "description_ru": "TEXT",
        "content_ru": "TEXT",
        "properties_ru": "TEXT",
        "translated_at": "DATETIME",
    }
    for col, col_type in new_cols.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE products ADD COLUMN {col} {col_type}")
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Translate product data to Russian")
    parser.add_argument("--db", default="products.db")
    parser.add_argument("--engine", choices=["deepl", "claude", "google"], required=True)
    parser.add_argument("--api-key", default=None, help="API key for DeepL or Claude")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--batch-size", type=int, default=20, help="Products per batch")
    args = parser.parse_args()

    if args.engine in ("deepl", "claude") and not args.api_key:
        log.error("--api-key is required for engine '%s'", args.engine)
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    init_db_columns(conn)

    # Query untranslated scraped products
    query = """
        SELECT id, pagetitle, longtitle, description, content, properties
        FROM products
        WHERE status = 'scraped' AND (translated_at IS NULL OR translated_at = '')
    """
    params = []
    if args.category:
        query += " AND category_path LIKE ?"
        params.append(f"%{args.category}%")
    if args.limit:
        query += f" LIMIT {args.limit}"

    rows = conn.execute(query, params).fetchall()
    total = len(rows)
    log.info("Products to translate: %d (engine: %s)", total, args.engine)

    translated_count = 0

    for batch_start in range(0, total, args.batch_size):
        batch_rows = rows[batch_start:batch_start + args.batch_size]
        log.info("Batch %d–%d of %d", batch_start + 1, batch_start + len(batch_rows), total)

        ids = [r["id"] for r in batch_rows]
        pagetitles = [r["pagetitle"] or "" for r in batch_rows]
        longtitles = [r["longtitle"] or "" for r in batch_rows]
        descriptions = [r["description"] or "" for r in batch_rows]

        try:
            tr_pagetitles = translate_batch(pagetitles, args.engine, args.api_key)
            tr_longtitles = translate_batch(longtitles, args.engine, args.api_key)
            tr_descriptions = translate_batch(descriptions, args.engine, args.api_key)
        except RuntimeError as e:
            log.error("Translation stopped: %s", e)
            break

        for i, row in enumerate(batch_rows):
            row_id = row["id"]

            # Translate content (HTML) — strip tags for translation, keep structure
            content = row["content"] or ""
            content_ru = ""
            if content:
                try:
                    content_translated = translate_batch([content], args.engine, args.api_key)
                    content_ru = content_translated[0] if content_translated else content
                except Exception as e:
                    log.warning("Content translation failed for id %d: %s", row_id, e)
                    content_ru = content

            # Translate properties JSON
            props_ru = ""
            try:
                props_ru = translate_properties(row["properties"], args.engine, args.api_key)
            except Exception as e:
                log.warning("Properties translation failed for id %d: %s", row_id, e)
                props_ru = row["properties"] or ""

            conn.execute("""
                UPDATE products SET
                    pagetitle_ru = ?,
                    longtitle_ru = ?,
                    description_ru = ?,
                    content_ru = ?,
                    properties_ru = ?,
                    translated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                tr_pagetitles[i],
                tr_longtitles[i],
                tr_descriptions[i],
                content_ru,
                props_ru,
                row_id,
            ))

        conn.commit()
        translated_count += len(batch_rows)
        log.info("Progress: %d/%d translated", translated_count, total)

    log.info("Done. Translated %d products.", translated_count)
    conn.close()


if __name__ == "__main__":
    main()
