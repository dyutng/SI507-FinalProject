"""
build_graph.py
"""

from clients import LastFmClient
from music_graph import Artist, MusicGraph
import json
import os

GRAPH_CACHE = "graph_cache.json"

SEED_ARTISTS = ["Kendrick Lamar", "Billie Eilish", "Bad Bunny", "Frank Ocean",
                "Ariana Grande", "Olivia Rodrigo", "TWICE", 
                "Frank Ocean", "Mitski", "Zedd", "Amy Winehouse"]

MAX_ARTISTS = 100
SIMILAR_LIMIT = 5


def build_artist_from_lastfm(name: str, lastfm: LastFmClient) -> Artist | None:
    """
    Create an Artist node from last.fm data

    Parameters
    ----------
    name : str
        Artist name.
    lastfm : LastFmClient

    Returns
    -------
    Artist or None if last.fm has no data for this artist
    """

    try:
        info = lastfm.get_artist_info(name)
        data = info.get("artist", {})

        if not data:
            return None

        listeners = int(data.get("stats", {}).get("listeners", 0))
        tags = [t["name"] for t in data.get("tags", {}).get("tag", [])[:5]]
        canonical_name = data.get("name", name)

    except Exception:
        return None

    return Artist(artist_id=canonical_name, name=canonical_name, genres=[], 
                  popularity=0, followers=0, listeners=listeners, lastfm_tags=tags,)


def save_graph(graph: MusicGraph, path: str = GRAPH_CACHE) -> None:

    nodes = [{"artist_id": a.artist_id, "name": a.name, "genres": a.genres, "popularity": a.popularity,
              "followers": a.followers, "listeners": a.listeners, "lastfm_tags": a.lastfm_tags,} for a in graph.all_artists()]
    
    edges = [{"a": u, "b": v, "relation": d.get("relation", "similar")} for u, v, d in graph._graph.edges(data=True)]
    
    with open(path, "w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

    print(f"Graph saved to {path}")


def load_graph(path: str = GRAPH_CACHE) -> MusicGraph | None:
    """Load a previously saved graph. Return None if the file is missing."""
    
    if not os.path.exists(path):
        return None
    
    with open(path) as f:
        data = json.load(f)
    graph = MusicGraph()
    
    for n in data["nodes"]:
        graph.add_artist(Artist(**n))

    for e in data["edges"]:
        graph.add_edge(e["a"], e["b"], e.get("relation", "similar"))

    return graph


def build_graph(lastfm_key: str) -> MusicGraph:
    """
    Build (or reload) the music collaboration graph

    Uses last.fm similar-artist data for edges. Saves the result to graph_cache.json for fast future loads.
    """

    existing = load_graph()

    if existing:
        nodes, edges = existing.size()
        print(f"Loaded existing graph: {nodes} artists, {edges} connections.")
        return existing

    print("Building graph from Last.fm API...")
    lastfm = LastFmClient(lastfm_key)
    graph = MusicGraph()

    name_to_id: dict[str, str] = {}
    queue = list(SEED_ARTISTS)
    seen_names: set[str] = set()

    while queue and graph.size()[0] < MAX_ARTISTS:
        name = queue.pop(0)

        if name.lower() in seen_names:
            continue

        seen_names.add(name.lower())

        artist = build_artist_from_lastfm(name, lastfm)

        if not artist:
            continue

        graph.add_artist(artist)
        name_to_id[artist.name.lower()] = artist.artist_id
        print(f"  Added: {artist.name} ({graph.size()[0]} artists)")

        try:
            similar = lastfm.get_similar_artists(artist.name, limit=SIMILAR_LIMIT)

            for sim in similar:
                sim_name = sim["name"]
                sim_lower = sim_name.lower()

                if graph.size()[0] >= MAX_ARTISTS:
                    break

                if sim_lower not in seen_names:
                    seen_names.add(sim_lower)
                    sim_artist = build_artist_from_lastfm(sim_name, lastfm)
                    
                    if sim_artist:
                        graph.add_artist(sim_artist)
                        name_to_id[sim_artist.name.lower()] = sim_artist.artist_id
                        queue.append(sim_artist.name)
                        print(f"    -> Similar: {sim_artist.name} ({graph.size()[0]} artists)")

                if sim_lower in name_to_id:
                    graph.add_edge(artist.artist_id,
                                   name_to_id[sim_lower],
                                   relation="similar")

        except Exception as e:
            print(f"    (could not get similar artists for {artist.name}: {e})")

    nodes, edges = graph.size()
    print(f"\nGraph complete: {nodes} artists, {edges} connections.")
    save_graph(graph)
    return graph