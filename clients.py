"""
clients.py

API clients for the Music Artist Collaboration Network.
Primary data source: Last.fm (fully open, no endpoint restrictions).
"""

import json
import os
import requests

CACHE_FILE = "cache.json"
LASTFM_BASE = "http://ws.audioscrobbler.com/2.0/"

class LastFmClient:
    """
    Wraps the last.fm API for artist data and graph construction.

    Gives us the following info:
      - Artist info (listeners, playcount, genre tags)
      - Similar artists (used to build graph edges)
    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
            
        return {}

    def _save_cache(self) -> None:
        with open(CACHE_FILE, "w") as f:
            json.dump(self._cache, f, indent=2)

    def _get(self, method: str, params: dict) -> dict:
        all_params = {**params, "method": method, "api_key": self._api_key, "format": "json"}
        key = "lastfm_" + method + str(sorted(params.items()))
        
        if key not in self._cache:
            resp = requests.get(LASTFM_BASE, params=all_params)
            resp.raise_for_status()
            self._cache[key] = resp.json()
            self._save_cache()

        return self._cache[key]

    def get_artist_info(self, artist_name: str) -> dict:
        """Get artist metadata: listener count, playcount, genre tags."""

        return self._get("artist.getinfo", {"artist": artist_name})

    def get_similar_artists(self, artist_name: str, limit: int = 10) -> list[dict]:
        """
        Return similar artists which are used to build edges in the graph

        Returns
        -------
        list[dict]
            Each entry has 'name' and 'match' (similarity 0.0-1.0).
        """

        data = self._get("artist.getsimilar", {"artist": artist_name, "limit": limit})
        return data.get("similarartists", {}).get("artist", [])