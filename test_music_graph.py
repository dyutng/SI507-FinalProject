"""
test_music_graph.py

Unit tests for  MusicGraph and Artist classes.

Run with 'python -m unittest test_music_graph.py -v'
"""

import unittest
from music_graph import Artist, MusicGraph


def make_artist(artist_id: str, name: str, genres=None, popularity=50, followers=1000, listeners=0, lastfm_tags=None) -> Artist:
    return Artist(artist_id=artist_id, name=name, genres=genres or [], popularity=popularity, 
                  followers=followers, listeners=listeners,lastfm_tags=lastfm_tags or [],)


def make_linear_graph() -> tuple[MusicGraph, list[Artist]]:
    """
    A -> B -> C -> D 
    Shortest path A->D has length 3
    """

    graph = MusicGraph()

    artists = [make_artist(str(i), name) for i, name in enumerate(["Alice", "Bob", "Carol", "Dave"])]

    for a in artists:
        graph.add_artist(a)

    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("2", "3")
    return graph, artists


def make_star_graph() -> tuple[MusicGraph, Artist, list[Artist]]:
    graph = MusicGraph()
    center = make_artist("c", "Center")
    spokes = [make_artist(str(i), f"Spoke{i}") for i in range(4)]
    graph.add_artist(center)

    for s in spokes:
        graph.add_artist(s)
        graph.add_edge("c", s.artist_id)

    return graph, center, spokes


class TestArtist(unittest.TestCase):

    def test_artist_str_includes_name_and_genre(self):
        """Artist __str__ should include the artist name and at least one genre"""

        artist = make_artist("a1", "Radiohead", genres=["art rock", "alternative"])
        result = str(artist)
        self.assertIn("Radiohead", result)
        self.assertIn("art rock", result)

    def test_artist_str_handles_no_genres(self):
        """Artist __str__ should be fine when genres list is empty"""

        artist = make_artist("a2", "Unknown", genres=[])
        result = str(artist)
        self.assertIn("Unknown", result)

    def test_artist_str_hides_zero_listeners(self):
        """Artist __str__ should not show listeners when value is 0"""

        artist = make_artist("a3", "New Artist", listeners=0)
        result = str(artist)
        self.assertNotIn("Listeners", result)

    def test_artist_str_shows_lastfm_tags(self):
        """Artist __str__ should show lastfm_tags in genres field"""

        artist = make_artist("a4", "Mitski", lastfm_tags=["indie", "art pop"])
        result = str(artist)
        self.assertIn("indie", result)


class TestMusicGraphNodes(unittest.TestCase):

    def setUp(self):
        self.graph = MusicGraph()
        self.artist = make_artist("sp1", "Olivia Rodrigo", genres=["pop"])

    def test_add_and_retrieve_artist(self):
        """Adding an artist and retrieving it by ID should return the same object"""

        self.graph.add_artist(self.artist)
        retrieved = self.graph.get_artist("sp1")
        self.assertEqual(retrieved.name, "Olivia Rodrigo")

    def test_has_artist_after_add(self):
        """has_artist returns True after the artist is added"""

        self.graph.add_artist(self.artist)
        self.assertTrue(self.graph.has_artist("sp1"))

    def test_has_artist_before_add(self):
        """has_artist returns False for an artist that has not been added"""

        self.assertFalse(self.graph.has_artist("sp1"))

    def test_duplicate_add_does_not_increase_size(self):
        """Adding the same artist twice should keep node count at 1"""

        self.graph.add_artist(self.artist)
        self.graph.add_artist(self.artist)
        nodes, _ = self.graph.size()
        self.assertEqual(nodes, 1)

    def test_get_artist_unknown_id_returns_none(self):
        """Retrieving a non-existent ID should return None"""

        self.assertIsNone(self.graph.get_artist("does_not_exist"))

    def test_find_by_name_case_insensitive(self):
        """Not case sensitive, find_by_name should match regardless of input"""

        self.graph.add_artist(self.artist)
        self.assertIsNotNone(self.graph.find_by_name("olivia rodrigo"))
        self.assertIsNotNone(self.graph.find_by_name("OLIVIA RODRIGO"))
        self.assertIsNotNone(self.graph.find_by_name("Olivia Rodrigo"))

    def test_find_by_name_not_found(self):
        """find_by_name returns None when the artist is not in the graph"""

        self.graph.add_artist(self.artist)
        self.assertIsNone(self.graph.find_by_name("Taylor Swift"))


class TestMusicGraphEdges(unittest.TestCase):

    def setUp(self):
        self.graph = MusicGraph()
        self.a = make_artist("a", "Alpha")
        self.b = make_artist("b", "Beta")
        self.graph.add_artist(self.a)
        self.graph.add_artist(self.b)

    def test_add_edge_creates_connection(self):
        """After adding an edge, both artists should appear in each other's neighbors"""

        self.graph.add_edge("a", "b")
        neighbors_a = [n.artist_id for n in self.graph.get_neighbors("a")]
        neighbors_b = [n.artist_id for n in self.graph.get_neighbors("b")]
        self.assertIn("b", neighbors_a)
        self.assertIn("a", neighbors_b)

    def test_edge_not_added_for_missing_node(self):
        """add_edge should silently skip if either artist is not in the graph"""

        self.graph.add_edge("a", "GHOST")
        _, edges = self.graph.size()
        self.assertEqual(edges, 0)

    def test_size_reports_correct_edge_count(self):
        """size() should reflect the number of edges after additions"""

        self.graph.add_edge("a", "b")
        _, edges = self.graph.size()
        self.assertEqual(edges, 1)


class TestShortestPath(unittest.TestCase):

    def setUp(self):
        self.graph, self.artists = make_linear_graph()

    def test_direct_neighbor_path_length_2(self):
        """Adjacent artists should have a path of length 2 (just the two nodes)"""

        path = self.graph.shortest_path("0", "1")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 2)

    def test_path_across_chain_correct_length(self):
        """Path from first to last in A->B->C->D chain should have 4 nodes"""

        path = self.graph.shortest_path("0", "3")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 4)

    def test_path_returns_artist_objects(self):
        """Every element in the path should be an Artist instance."""

        path = self.graph.shortest_path("0", "3")

        for step in path:
            self.assertIsInstance(step, Artist)

    def test_path_starts_and_ends_correctly(self):
        path = self.graph.shortest_path("0", "3")
        self.assertEqual(path[0].artist_id, "0")
        self.assertEqual(path[-1].artist_id, "3")

    def test_self_path_is_single_node(self):
        """Path from an artist to themselves should contain just that artist (length 1)"""

        path = self.graph.shortest_path("0", "0")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 1)

    def test_disconnected_artists_returns_none(self):
        """No path should exist between disconnected nodes, returns None"""

        isolated = make_artist("iso", "Isolated")
        self.graph.add_artist(isolated)
        path = self.graph.shortest_path("0", "iso")
        self.assertIsNone(path)

    def test_nonexistent_artist_returns_none(self):
        """Requesting a path for an unknown ID should return None, not raise"""

        path = self.graph.shortest_path("0", "GHOST")
        self.assertIsNone(path)


class TestCentralityRankings(unittest.TestCase):

    def test_star_center_ranks_first(self):
        """In a star graph, the center node should have the highest centrality"""

        graph, center, _ = make_star_graph()
        ranked = graph.top_by_centrality(1)
        self.assertEqual(len(ranked), 1)
        top_artist, top_score = ranked[0]
        self.assertEqual(top_artist.artist_id, center.artist_id)

    def test_centrality_returns_artist_and_float(self):
        """Each entry in top_by_centrality should be (Artist, float)"""

        graph, _, _ = make_star_graph()
        ranked = graph.top_by_centrality(3)

        for artist, score in ranked:
            self.assertIsInstance(artist, Artist)
            self.assertIsInstance(score, float)

    def test_centrality_n_limits_results(self):
        """top_by_centrality(n) should return at most n results"""

        graph, _, _ = make_star_graph()
        ranked = graph.top_by_centrality(2)
        self.assertLessEqual(len(ranked), 2)


class TestGenreFilter(unittest.TestCase):

    def setUp(self):
        self.graph = MusicGraph()
        self.graph.add_artist(make_artist("p1", "Pop Artist A", genres=["pop", "dance pop"]))
        self.graph.add_artist(make_artist("p2", "Pop Artist B", genres=["indie pop"]))
        self.graph.add_artist(make_artist("r1", "Rock Artist", genres=["classic rock"]))
        self.graph.add_artist(make_artist("t1", "Tagged Artist", lastfm_tags=["pop punk"]))

    def test_genre_filter_matches_genres(self):
        """filter_by_genre should match artists whose genres contain the keyword"""

        results = self.graph.filter_by_genre("pop")
        ids = [a.artist_id for a in results]
        self.assertIn("p1", ids)
        self.assertIn("p2", ids)

    def test_genre_filter_excludes_non_matching(self):
        """filter_by_genre should not return artists whose genres don't match"""

        results = self.graph.filter_by_genre("pop")
        ids = [a.artist_id for a in results]
        self.assertNotIn("r1", ids)

    def test_genre_filter_matches_lastfm_tags(self):
        """filter_by_genre should also search Last.fm community tags"""

        results = self.graph.filter_by_genre("pop punk")
        ids = [a.artist_id for a in results]
        self.assertIn("t1", ids)

    def test_genre_filter_case_insensitive(self):
        """filter_by_genre should be case-insensitive"""

        results_lower = self.graph.filter_by_genre("rock")
        results_upper = self.graph.filter_by_genre("ROCK")
        self.assertEqual(len(results_lower), len(results_upper))

    def test_genre_filter_no_match_returns_empty(self):
        """filter_by_genre returns an empty list when nothing matches"""

        results = self.graph.filter_by_genre("jazz")
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main(verbosity=2)