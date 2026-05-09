import math
import httpx
from typing import List

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_HEADERS = {"User-Agent": "WineTracker/0.1"}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _walking_minutes(metres: float) -> int:
    return max(1, round(metres / 80))  # ~80 m/min walking pace


async def find_wine_stores(lat: float, lon: float, radius_m: int = 800) -> List[dict]:
    """Query Overpass API for wine/alcohol/liquor shops within radius_m metres."""
    query = f"""
[out:json][timeout:20];
(
  node["shop"="wine"](around:{radius_m},{lat},{lon});
  node["shop"="alcohol"](around:{radius_m},{lat},{lon});
  node["shop"="liquor"](around:{radius_m},{lat},{lon});
  way["shop"="wine"](around:{radius_m},{lat},{lon});
  way["shop"="alcohol"](around:{radius_m},{lat},{lon});
  way["shop"="liquor"](around:{radius_m},{lat},{lon});
);
out center;
"""
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            resp = await client.post(
                OVERPASS_URL, data={"data": query}, headers=_HEADERS
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

    stores: list[dict] = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        if el["type"] == "way":
            slat = el.get("center", {}).get("lat", lat)
            slon = el.get("center", {}).get("lon", lon)
        else:
            slat = el.get("lat", lat)
            slon = el.get("lon", lon)

        dist = _haversine(lat, lon, slat, slon)

        addr_parts = filter(
            None,
            [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:city"),
            ],
        )
        address = tags.get("addr:full") or " ".join(addr_parts) or "Address unavailable"

        website = tags.get("website") or tags.get("contact:website")
        if website and not website.startswith("http"):
            website = "https://" + website

        stores.append(
            {
                "name": name,
                "address": address,
                "website": website,
                "phone": tags.get("phone") or tags.get("contact:phone"),
                "distance_m": round(dist),
                "walking_minutes": _walking_minutes(dist),
            }
        )

    return sorted(stores, key=lambda s: s["distance_m"])
