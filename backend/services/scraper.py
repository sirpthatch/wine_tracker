"""
Wine store inventory scraper.

Tries three strategies in order:
  1. Shopify /products.json API  (many independent wine shops use Shopify)
  2. Generic HTML scraping with BeautifulSoup  (works on static / SSR sites)
  3. Returns empty list with an explanatory status message

JavaScript-heavy SPAs (React/Vue storefronts) cannot be scraped without a
headless browser, so those will fall through to the empty-list case.
"""

import re
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional

# ---------------------------------------------------------------------------
# Wine vocabulary used to identify wine products in scraped text
# ---------------------------------------------------------------------------
_VARIETALS = {
    "Cabernet Sauvignon", "Cabernet Franc", "Merlot", "Pinot Noir",
    "Syrah", "Shiraz", "Zinfandel", "Grenache", "Sangiovese", "Nebbiolo",
    "Barbera", "Tempranillo", "Malbec", "Carmenere", "Mourvedre",
    "Chardonnay", "Sauvignon Blanc", "Riesling", "Pinot Grigio",
    "Pinot Gris", "Gewurztraminer", "Viognier", "Chenin Blanc",
    "Champagne", "Prosecco", "Cava", "Sparkling", "Rosé", "Rose",
    "Bordeaux", "Burgundy", "Chianti", "Barolo", "Brunello", "Amarone",
    "Rioja", "Albariño", "Albarino", "Moscato", "Port", "Sherry",
}
_VARIETAL_LOWER = {v.lower(): v for v in _VARIETALS}

_PRICE_RE = re.compile(r"\$\s*(\d{1,4}(?:\.\d{2})?)")
_VINTAGE_RE = re.compile(r"\b(19\d{2}|20[012]\d)\b")

# Sub-pages to try when looking for wine listings
_WINE_PATHS = [
    "/collections/wine", "/collections/wines", "/collections/all",
    "/shop/wine", "/shop/wines", "/shop", "/products", "/wine",
    "/wines", "/catalog", "/inventory", "/store",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def scrape_store_inventory(url: str) -> tuple[list[dict], str]:
    """
    Returns (wines, status_message).

    Each wine dict has keys: name, varietal, vintage, price.
    """
    if not url:
        return [], "No website on file"

    base = _base_url(url)

    async with httpx.AsyncClient(
        timeout=10, follow_redirects=True, headers=_HEADERS
    ) as client:
        # Strategy 1 — Shopify JSON API
        wines = await _try_shopify(base, client)
        if wines is not None:
            return wines, f"inventory via Shopify ({len(wines)} wines)"

        # Strategy 2 — HTML scraping
        wines = await _try_html(url, base, client)
        if wines:
            return wines, f"inventory scraped from website ({len(wines)} wines)"

    return [], "Inventory not available online (visit store website to browse)"


# ---------------------------------------------------------------------------
# Strategy 1: Shopify /products.json
# ---------------------------------------------------------------------------

async def _try_shopify(base: str, client: httpx.AsyncClient) -> Optional[list[dict]]:
    """Returns list of wines if this looks like a Shopify store, else None."""
    # Shopify exposes /collections/<handle>/products.json
    for path in ("/collections/wine/products.json", "/collections/all/products.json", "/products.json"):
        try:
            resp = await client.get(f"{base}{path}", headers={"Accept": "application/json"})
        except Exception:
            continue
        if resp.status_code != 200:
            continue
        try:
            data = resp.json()
        except Exception:
            continue
        products = data.get("products", [])
        if not products:
            continue

        wines: list[dict] = []
        for p in products:
            title: str = p.get("title", "")
            body: str = _strip_html(p.get("body_html") or "")
            varietal = _find_varietal(title + " " + body)
            if not varietal:
                continue  # skip non-wine products

            price = None
            variants = p.get("variants", [])
            if variants:
                raw_price = variants[0].get("price")
                if raw_price:
                    price = f"${float(raw_price):.2f}"

            wines.append(
                {
                    "name": title,
                    "varietal": varietal,
                    "vintage": _find_vintage(title),
                    "price": price,
                }
            )
            if len(wines) >= 40:
                break

        if wines:
            return wines

    return None  # not a Shopify store, or no wine products


# ---------------------------------------------------------------------------
# Strategy 2: Generic HTML scraping
# ---------------------------------------------------------------------------

async def _try_html(url: str, base: str, client: httpx.AsyncClient) -> list[dict]:
    # First fetch the provided URL; then look for a better wine-listing sub-page
    soup = await _fetch_soup(url, client)
    if soup is None:
        return []

    wine_page_url = _find_wine_page_link(soup, base) or url
    if wine_page_url != url:
        deeper = await _fetch_soup(wine_page_url, client)
        if deeper:
            soup = deeper

    return _extract_wines_from_soup(soup)


async def _fetch_soup(url: str, client: httpx.AsyncClient) -> Optional[BeautifulSoup]:
    try:
        resp = await client.get(url)
        if resp.status_code >= 400:
            return None
        return BeautifulSoup(resp.text, "lxml")
    except Exception:
        return None


def _find_wine_page_link(soup: BeautifulSoup, base: str) -> Optional[str]:
    """Scan anchor tags for a link that looks like a wine/shop page."""
    for a in soup.find_all("a", href=True):
        href: str = a["href"].lower()
        text: str = a.get_text().lower().strip()
        if any(kw in href for kw in ("/wine", "/shop", "/catalog", "/inventory", "/store", "/products")):
            return urljoin(base, a["href"])
        if any(kw in text for kw in ("wine", "shop our", "inventory", "products")):
            full = urljoin(base, a["href"])
            # Stay on same domain
            if urlparse(full).netloc == urlparse(base).netloc:
                return full

    # Try well-known paths blindly
    parsed = urlparse(base)
    for path in _WINE_PATHS:
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    return None


def _extract_wines_from_soup(soup: BeautifulSoup) -> list[dict]:
    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    wines: list[dict] = []
    seen: set[str] = set()

    # Pass 1: look for product-card-like elements (common e-commerce patterns)
    for el in soup.select(
        "[class*=product], [class*=wine-item], [class*=item-title], "
        "[class*=product-title], [class*=product-name], [class*=item-name]"
    ):
        text = el.get_text(" ", strip=True)
        varietal = _find_varietal(text)
        if not varietal:
            continue
        name = _clean_name(text)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        # Look for a price sibling
        parent = el.parent or el
        price_match = _PRICE_RE.search(parent.get_text())
        wines.append(
            {
                "name": name,
                "varietal": varietal,
                "vintage": _find_vintage(text),
                "price": f"${price_match.group(1)}" if price_match else None,
            }
        )
        if len(wines) >= 40:
            return wines

    # Pass 2: line-by-line scan of visible text
    if not wines:
        lines = [l.strip() for l in soup.get_text("\n").splitlines() if l.strip()]
        for i, line in enumerate(lines):
            varietal = _find_varietal(line)
            if not varietal:
                continue
            name = _clean_name(line)
            if not name or len(name) < 5 or len(name) > 100 or name.lower() in seen:
                continue
            seen.add(name.lower())

            context = " ".join(lines[max(0, i - 2) : i + 3])
            price_match = _PRICE_RE.search(context)
            wines.append(
                {
                    "name": name,
                    "varietal": varietal,
                    "vintage": _find_vintage(line),
                    "price": f"${price_match.group(1)}" if price_match else None,
                }
            )
            if len(wines) >= 40:
                break

    return wines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _find_varietal(text: str) -> Optional[str]:
    lower = text.lower()
    for key, canonical in _VARIETAL_LOWER.items():
        if key in lower:
            return canonical
    return None


def _find_vintage(text: str) -> Optional[str]:
    m = _VINTAGE_RE.search(text)
    return m.group(1) if m else None


def _clean_name(text: str) -> str:
    text = _PRICE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" .,;:-")
    return text[:80]


def _strip_html(html: str) -> str:
    return BeautifulSoup(html, "lxml").get_text(" ", strip=True)
