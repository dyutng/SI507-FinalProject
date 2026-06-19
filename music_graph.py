"""
music_graph.py

"""

from __future__ import annotations
from dataclasses import dataclass, field
import networkx as nx

@dataclass
class Artist:
    """
    Represents a single artist node in the collaboration graph.

    Attributes
    ----------
    artist_id : str
        Unique artist ID (artist name used as key).
    name : str
        Display name of the artist.
    genres : list[str]
        Genre tags.
    popularity : int
        Spotify popularity score (0–100).
    followers : int
        Follower count.
    listeners : int
        Last.fm monthly listener count (0 if unavailable).
    lastfm_tags : list[str]
        Community genre tags from Last.fm.
    """

    artist_id: str
    name: str
    genres: list[str] = field(default_factory=list)
    popularity: int = 0
    followers: int = 0
    listeners: int = 0
    lastfm_tags: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [self.name]
        tags = (self.genres + self.lastfm_tags)[:3]

        if tags:
            parts.append(f"Genres: {', '.join(tags)}")

        if self.popularity:
            parts.append(f"Popularity: {self.popularity}")

        if self.followers:
            parts.append(f"Followers: {self.followers:,}")

        if self.listeners:
            parts.append(f"Listeners: {self.listeners:,}")

        return " | ".join(parts)


class MusicGraph:
    """
    An undirected graph of artists connected by collaboration edges. Each node stores an Artist object. Edges are added when two artists are connected via last.fm similarity relationships
    """

    def __init__(self):
        self._graph: nx.Graph = nx.Graph()

    def add_artist(self, artist: Artist) -> None:
        """Add an artist as a node. Skips if already present"""

        if artist.artist_id not in self._graph:
            self._graph.add_node(artist.artist_id, artist=artist)

    def add_edge(self, id_a: str, id_b: str, relation: str = "related") -> None:
        """Add an undirected edge between two artists"""

        if id_a in self._graph and id_b in self._graph:
            self._graph.add_edge(id_a, id_b, relation=relation)

    def has_artist(self, artist_id: str) -> bool:
        """Return True if an artist with this ID is in the graph."""

        return artist_id in self._graph

    def get_artist(self, artist_id: str) -> Artist | None:
        """Retrieve the Artist object stored at a node """

        node = self._graph.nodes.get(artist_id)
        return node["artist"] if node else None

    def find_by_name(self, name: str) -> Artist | None:

        name_lower = name.lower()

        for node_id, data in self._graph.nodes(data=True):
            if data["artist"].name.lower() == name_lower:
                return data["artist"]
            
        return None

    def get_neighbors(self, artist_id: str) -> list[Artist]:
        return [self._graph.nodes[n]["artist"] for n in self._graph.neighbors(artist_id)]

    def shortest_path(self, id_a: str, id_b: str) -> list[Artist] | None:
        """Return the shortest collaboration path between two artists using BFS"""

        try:
            path_ids = nx.shortest_path(self._graph, id_a, id_b)
            return [self._graph.nodes[n]["artist"] for n in path_ids]
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def top_by_centrality(self, n: int = 10) -> list[tuple[Artist, float]]:
        """Return the topN artists ranked by degree centrality (most connected)"""

        centrality = nx.degree_centrality(self._graph)
        ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return [(self._graph.nodes[node_id]["artist"], score) for node_id, score in ranked[:n]]

    def filter_by_genre(self, genre: str) -> list[Artist]:
        """Return all artists whose genre tags contain the given string"""

        genre_lower = genre.lower()
        results = []

        for _, data in self._graph.nodes(data=True):
            artist = data["artist"]
            all_tags = [g.lower() for g in artist.genres + artist.lastfm_tags]
            
            if any(genre_lower in tag for tag in all_tags):
                results.append(artist)

        return results


    def size(self) -> tuple[int, int]:
        """Return (number_of_nodes, number_of_edges)."""

        return self._graph.number_of_nodes(), self._graph.number_of_edges()

    def all_artists(self) -> list[Artist]:
        """Return all Artist objects in the graph."""

        return [data["artist"] for _, data in self._graph.nodes(data=True)]