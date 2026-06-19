"""
main.py

Command-line interface for the Music Artist Collaboration Network.

Run with 'python main.py'
"""

import os
from build_graph import build_graph
from music_graph import MusicGraph, Artist


def _divider() -> None:
    print("-" * 60)


def mode_artist_profile(graph: MusicGraph) -> None:
    """
    Option 1: Artist Search & Profile View.
    Show an artist's attributes and their direct collaborators.
    """

    name = input("Enter artist name: ").strip()
    artist = graph.find_by_name(name)

    if not artist:
        print(f"  '{name}' not found in the graph.")
        return

    print(f"\n{artist}")

    if artist.lastfm_tags:
        print(f"  Last.fm tags: {', '.join(artist.lastfm_tags)}")

    neighbors = graph.get_neighbors(artist.artist_id)
    print(f"\n  Direct collaborators ({len(neighbors)}):")

    for n in sorted(neighbors, key=lambda a: a.name):
        print(f"    - {n.name}")


def mode_shortest_path(graph: MusicGraph) -> None:
    """
    Option 2: Shortest Path Finder.
    Print the step-by-step chain connecting two artists.
    """

    name_a = input("Starting artist: ").strip()
    name_b = input("Target artist: ").strip()

    artist_a = graph.find_by_name(name_a)
    artist_b = graph.find_by_name(name_b)

    if not artist_a:
        print(f"  '{name_a}' not found in the graph.")
        return
    if not artist_b:
        print(f"  '{name_b}' not found in the graph.")
        return

    path = graph.shortest_path(artist_a.artist_id, artist_b.artist_id)

    if path is None:
        print(f"  No connection found between {artist_a.name} and {artist_b.name}.")
        return

    print(f"\n  Path ({len(path) - 1} hop(s)):")

    for i, step in enumerate(path):
        prefix = "  " + ("  " * i) + "-> " if i > 0 else "  "
        print(f"{prefix}{step.name}")


def mode_influence_rankings(graph: MusicGraph) -> None:
    """
    Option 3: Influence Rankings.
    Display the top-N most-connected artists by degree centrality.
    """

    try:
        n = int(input("How many artists to show? (default 10): ").strip() or "10")
    except ValueError:
        n = 10

    ranked = graph.top_by_centrality(n)
    print(f"\n  Top {n} most-connected artists:")

    for rank, (artist, score) in enumerate(ranked, start=1):
        print(f"  {rank:2}. {artist.name:<30} centrality: {score:.4f}")


def mode_genre_filter(graph: MusicGraph) -> None:
    """
    Option 4: Genre Filter.
    List all artists in the graph that match a genre keyword.
    """

    genre = input("Enter genre keyword (e.g. 'pop', 'hip-hop', 'rock'): ").strip()
    results = graph.filter_by_genre(genre)

    if not results:
        print(f"  No artists found for genre '{genre}'.")
        return

    print(f"\n  Artists matching '{genre}' ({len(results)} found):")
    
    for artist in sorted(results, key=lambda a: a.name):
        tags = (artist.genres + artist.lastfm_tags)[:2]
        print(f"  - {artist.name}" + (f" [{', '.join(tags)}]" if tags else ""))


MODES = {"1": ("Artist Profile & Collaborators", mode_artist_profile),
         "2": ("Shortest Path Between Artists",  mode_shortest_path),
         "3": ("Influence Rankings", mode_influence_rankings),
         "4": ("Genre Filter", mode_genre_filter),}


def main() -> None:
    lastfm_key = os.environ.get("LASTFM_API_KEY", "")

    if not lastfm_key:
        print("Error: LASTFM_API_KEY must be set.")
        print("  export LASTFM_API_KEY=your_key")
        return

    print("=" * 60)
    print("  Music Artist Collaboration Network")
    print("=" * 60)

    graph = build_graph(lastfm_key)
    nodes, edges = graph.size()
    print(f"\nGraph ready: {nodes} artists, {edges} connections.\n")

    while True:
        _divider()
        print("Choose an interaction:")

        for key, (label, _) in MODES.items():
            print(f"  {key}. {label}")

        print("  q. Quit")
        _divider()

        choice = input("Enter choice: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        elif choice in MODES:
            print()
            MODES[choice][1](graph)
            print()
            
        else:
            print("  Invalid choice. Please enter 1–4 or q.")


if __name__ == "__main__":
    main()
