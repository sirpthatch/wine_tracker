import httpx
from typing import Optional

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_HEADERS = {"User-Agent": "WineTracker/0.1 (personal wine tracking; non-commercial)"}


async def geocode_address(address: str) -> Optional[dict]:
    """Returns {lat, lon, display_name} or None."""
    params = {"q": address, "format": "json", "limit": 1}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(NOMINATIM_URL, params=params, headers=_HEADERS)
            resp.raise_for_status()
            results = resp.json()
        except Exception:
            return None

    if not results:
        return None
    r = results[0]
    return {
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "display_name": r.get("display_name", address),
    }
