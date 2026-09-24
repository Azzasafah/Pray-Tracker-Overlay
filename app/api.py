import datetime
import json
import os
import requests
from typing import Dict, List, Optional, Tuple

from app.config import CACHE_FILE, CITIES_CACHE_FILE

API_BASE = "https://api.myquran.com/v2/sholat"

class MyQuranAPI:
    """Handles communication with the public MyQuran Kemenag API."""

    @staticmethod
    def get_cities(force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Retrieves all Indonesian cities/kabupaten.
        Caches results locally to avoid repeated network calls.
        """
        if not force_refresh and os.path.exists(CITIES_CACHE_FILE):
            try:
                with open(CITIES_CACHE_FILE, "r", encoding="utf-8") as f:
                    cached_cities = json.load(f)
                    if isinstance(cached_cities, list) and len(cached_cities) > 0:
                        return cached_cities
            except Exception as e:
                print(f"[API] Error reading cities cache: {e}")

        # Fetch from API
        try:
            url = f"{API_BASE}/kota/semua"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") and "data" in data:
                    cities = data["data"]
                    # Save to cache
                    try:
                        with open(CITIES_CACHE_FILE, "w", encoding="utf-8") as f:
                            json.dump(cities, f, ensure_ascii=False, indent=2)
                    except Exception as ce:
                        print(f"[API] Could not save cities cache: {ce}")
                    return cities
        except Exception as e:
            print(f"[API] Error fetching all cities: {e}")

        # Fallback basic list if completely offline
        return [
            {"id": "1608", "lokasi": "KAB. JOMBANG"},
            {"id": "1301", "lokasi": "KOTA JAKARTA"},
            {"id": "1219", "lokasi": "KOTA BANDUNG"},
            {"id": "1638", "lokasi": "KOTA SURABAYA"},
            {"id": "1203", "lokasi": "KOTA SEMARANG"},
            {"id": "1408", "lokasi": "KOTA YOGYAKARTA"},
            {"id": "0228", "lokasi": "KOTA MEDAN"},
            {"id": "2308", "lokasi": "KOTA MAKASSAR"},
            {"id": "1701", "lokasi": "KOTA DENPASAR"},
        ]

    @staticmethod
    def search_cities(keyword: str) -> List[Dict[str, str]]:
        """Searches cities locally from cached list or via API."""
        keyword_clean = keyword.strip().upper()
        if not keyword_clean:
            return []

        all_cities = MyQuranAPI.get_cities(force_refresh=False)
        matched = [c for c in all_cities if keyword_clean in c.get("lokasi", "").upper()]
        if matched:
            return matched

        # If not found in local cache, try live API search
        try:
            url = f"{API_BASE}/kota/cari/{requests.utils.quote(keyword.strip())}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") and "data" in data:
                    return data["data"]
        except Exception as e:
            print(f"[API] Search API error: {e}")

        return []

    @staticmethod
    def get_schedule(city_id: str, date: Optional[datetime.date] = None) -> Tuple[Optional[Dict], bool]:
        """
        Fetches prayer schedule for given city_id and date.
        Returns: (schedule_dict, is_online)
        schedule_dict format:
        {
            "imsak": "04:17",
            "subuh": "04:27",
            "terbit": "05:38",
            "dhuha": "06:05",
            "dzuhur": "11:48",
            "ashar": "14:57",
            "maghrib": "17:51",
            "isya": "19:00",
            "date": "2026-09-24",
            "lokasi": "KOTA JAKARTA",
            "daerah": "DKI JAKARTA"
        }
        """
        if date is None:
            date = datetime.date.today()

        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"{city_id}_{date_str}"

        # 1. Read existing cache
        cache = {}
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception as e:
                print(f"[API] Error reading schedule cache: {e}")

        # 2. Try online fetch
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        url = f"{API_BASE}/jadwal/{city_id}/{year}/{month}/{day}"

        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("status") and "data" in res_data:
                    data = res_data["data"]
                    jadwal = data.get("jadwal", {})
                    jadwal["lokasi"] = data.get("lokasi", "")
                    jadwal["daerah"] = data.get("daerah", "")
                    jadwal["city_id"] = city_id

                    # Save to cache
                    cache[cache_key] = jadwal
                    try:
                        with open(CACHE_FILE, "w", encoding="utf-8") as f:
                            json.dump(cache, f, ensure_ascii=False, indent=2)
                    except Exception as ce:
                        print(f"[API] Error writing schedule cache: {ce}")

                    return jadwal, True
        except Exception as e:
            print(f"[API] Live schedule fetch failed: {e}")

        # 3. Fallback to cached schedule
        if cache_key in cache:
            print(f"[API] Using cached schedule for {cache_key}")
            return cache[cache_key], False

        # 4. Check if any schedule for this city exists in cache
        for k, v in cache.items():
            if k.startswith(f"{city_id}_"):
                print(f"[API] Using approximate cached schedule for city {city_id}")
                return v, False

        return None, False
