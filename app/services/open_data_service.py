"""Lightweight loader for public/open datasets (CSV / GeoJSON) used as attractions.

This module provides simple helpers to fetch and normalise public datasets
into the in-memory attraction shape used by the recommender. It's intentionally
small and defensive — failures fall back to the bundled sample dataset.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
from typing import Dict, Iterable, List, Optional

import requests

logger = logging.getLogger(__name__)


def _normalise_record(rec: Dict) -> Dict:
    """Normalize a generic record into the attraction shape.

    This is permissive: only a few fields are required by the recommender.
    """
    # Attempt to extract a lat/lng from a variety of possible keys
    lat = None
    lng = None
    location = rec.get("location") or {}
    if isinstance(location, dict):
        lat = location.get("lat") or location.get("latitude")
        lng = location.get("lng") or location.get("longitude")

    # Some geojson-like records embed coordinates
    if lat is None or lng is None:
        coords = rec.get("coordinates") or rec.get("geometry")
        if isinstance(coords, dict):
            # geometry: {"coordinates": [lng, lat]}
            c = coords.get("coordinates")
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                lng, lat = c[0], c[1]

    try:
        lat = float(lat) if lat is not None else None
        lng = float(lng) if lng is not None else None
    except Exception:
        lat = None
        lng = None

    return {
        "id": str(rec.get("id") or rec.get("identifier") or rec.get("name", "unknown")[:64]),
        "name": rec.get("name") or rec.get("title") or "Unknown",
        "description": rec.get("description") or rec.get("summary") or "",
        "location": {"lat": lat, "lng": lng},
        "categories": rec.get("categories") or rec.get("tags") or [],
        "rating": rec.get("rating") or {},
        "features": {},
    }


class OpenDataService:
    """Simple fetcher for public datasets.

    Usage: call `load_from_urls([...])` with a list of HTTP(S) URLs. The
    function will attempt to download CSV or GeoJSON and return a list of
    attraction-like dictionaries.
    """

    @staticmethod
    def _parse_csv(text: str) -> List[Dict]:
        stream = io.StringIO(text)
        reader = csv.DictReader(stream)
        return [dict(row) for row in reader]

    @staticmethod
    def _parse_geojson(text: str) -> List[Dict]:
        data = json.loads(text)
        features = data.get("features") or []
        out = []
        for f in features:
            rec = {}
            props = f.get("properties") or {}
            rec.update(props)
            geom = f.get("geometry")
            if isinstance(geom, dict):
                rec["geometry"] = geom
            out.append(rec)
        return out

    @classmethod
    def load_from_urls(cls, urls: Iterable[str]) -> List[Dict]:
        attractions: List[Dict] = []
        for url in urls:
            if not url:
                continue
            try:
                logger.info("Fetching open-data URL: %s", url)
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "")
                text = resp.text

                parsed: Optional[List[Dict]] = None
                if "json" in content_type or text.strip().startswith("{"):
                    try:
                        parsed = cls._parse_geojson(text)
                    except Exception:
                        # try generic JSON list
                        try:
                            parsed = json.loads(text)
                        except Exception:
                            parsed = None
                elif "csv" in content_type or "text" in content_type:
                    parsed = cls._parse_csv(text)

                if not parsed:
                    logger.warning("Unable to parse open-data at %s; skipping", url)
                    continue

                for rec in parsed:
                    attractions.append(_normalise_record(rec))

            except Exception as exc:
                logger.warning("Failed to load open-data %s: %s", url, exc)
                continue

        # basic dedupe by id
        seen = set()
        deduped = []
        for a in attractions:
            if a["id"] in seen:
                continue
            seen.add(a["id"])
            deduped.append(a)

        return deduped


def load_default_sources() -> List[Dict]:
    """Load sources from `OPEN_DATA_SOURCES` env var (comma separated URLs).

    Returns an empty list if not configured or on failure.
    """
    raw = os.environ.get("OPEN_DATA_SOURCES", "")
    if not raw:
        return []
    urls = [u.strip() for u in raw.split(",") if u.strip()]
    if not urls:
        return []
    try:
        return OpenDataService.load_from_urls(urls)
    except Exception as exc:
        logger.warning("Open data loading failed: %s", exc)
        return []
