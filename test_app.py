"""Jalankan: python -m unittest test_app -v (tanpa framework tes tambahan)."""

import math
import unittest

import networkx as nx

from dijkstra import dijkstra
from graph_data import build_graph


def adjacency(graph):
    return {u: {v: data['weight'] for v, data in graph[u].items()} for u in graph}


class AlgorithmTests(unittest.TestCase):
    def test_graph_size_and_independent_copies(self):
        graph = build_graph()
        self.assertEqual((len(graph), graph.number_of_edges()), (10, 15))
        self.assertFalse(graph.is_directed())
        self.assertEqual([n for n, d in graph.nodes(data=True) if d['shelter']], ['I', 'J'])
        self.assertTrue(nx.is_connected(graph))
        self.assertTrue(all(d['weight'] > 0 for _, _, d in graph.edges(data=True)))
        graph['A']['B']['weight'] = 1
        graph.remove_node('I')
        self.assertEqual(build_graph()['A']['B']['weight'], 300)
        self.assertIn('I', build_graph())

    def test_known_route_and_independent_snapshots(self):
        path, distance, steps = dijkstra(adjacency(build_graph()), 'A', 'I')
        self.assertEqual(path, ['A', 'D', 'G', 'I'])
        self.assertEqual(distance, 1200)
        self.assertEqual(steps[0]['node'], 'A')
        self.assertEqual(steps[0]['distances']['D'], 400)
        self.assertTrue(math.isinf(steps[0]['distances']['I']))
        self.assertEqual(steps[-1]['distances']['I'], 1200)
        self.assertEqual([s['step'] for s in steps], list(range(1, len(steps) + 1)))

    def test_all_pairs_and_each_single_road_block_against_networkx(self):
        original = build_graph()
        for blocked in [None, *original.edges]:
            graph = original.copy()
            if blocked:
                graph.remove_edge(*blocked)
            for source in graph:
                expected = nx.single_source_dijkstra_path_length(graph, source)
                for target in graph:
                    with self.subTest(blocked=blocked, source=source, target=target):
                        path, distance, _ = dijkstra(adjacency(graph), source, target)
                        self.assertEqual(distance, expected.get(target, math.inf))
                        if target not in expected:
                            self.assertEqual(path, [])
                        else:
                            self.assertEqual((path[0], path[-1]), (source, target))
                            self.assertEqual(len(path), len(set(path)))
                            self.assertEqual(sum(graph[u][v]['weight'] for u, v in zip(path, path[1:])), distance)

    def test_unreachable_and_same_node(self):
        graph = build_graph()
        graph.remove_edges_from([('G', 'I'), ('H', 'I')])
        path, distance, steps = dijkstra(adjacency(graph), 'A', 'I')
        self.assertEqual(path, [])
        self.assertTrue(math.isinf(distance))
        self.assertNotIn('I', [s['node'] for s in steps])
        path, distance, steps = dijkstra(adjacency(graph), 'I', 'I')
        self.assertEqual((path, distance, len(steps)), (['I'], 0, 1))

    def test_equal_paths_and_zero_weight(self):
        graph = {'A': {'B': 0, 'C': 0}, 'B': {'A': 0, 'D': 2},
                 'C': {'A': 0, 'D': 2}, 'D': {'B': 2, 'C': 2}}
        path, distance, _ = dijkstra(graph, 'A', 'D')
        self.assertIn(path, [['A', 'B', 'D'], ['A', 'C', 'D']])
        self.assertEqual(distance, 2)

    def test_stale_heap_entries_are_not_iterations(self):
        graph = {'A': {'B': 10, 'C': 1}, 'B': {'A': 10, 'C': 1},
                 'C': {'A': 1, 'B': 1}, 'D': {}}
        _, _, steps = dijkstra(graph, 'A', 'D')
        self.assertEqual([s['node'] for s in steps], ['A', 'C', 'B'])
        self.assertEqual([s['distance'] for s in steps], [0, 1, 2])

    def test_invalid_weights_even_outside_source_component(self):
        for weight in [-1, math.nan, math.inf, -math.inf, '100', None, True]:
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                dijkstra({'A': {}, 'B': {'C': weight}, 'C': {'B': weight}}, 'A', 'A')

    def test_unknown_endpoints_and_dangling_neighbor(self):
        for graph, source, target in [({'A': {}}, 'X', 'A'),
                                      ({'A': {}}, 'A', 'X'),
                                      ({'A': {'B': 2}}, 'A', 'A')]:
            with self.subTest(graph=graph, source=source, target=target):
                with self.assertRaises(ValueError):
                    dijkstra(graph, source, target)


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from streamlit.testing.v1 import AppTest
        self.app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=20).run()

    def assert_healthy(self):
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.error), 0)

    def distance(self):
        return next(m.value for m in self.app.metric if m.label == 'Total jarak')

    def figure(self):
        import json
        return json.loads(self.app.get('plotly_chart')[0].proto.spec)

    def test_initial_result_and_visualization(self):
        self.assert_healthy()
        self.assertEqual(self.distance(), '1200 m')
        self.assertTrue(any('NetworkX' in s.value for s in self.app.success))
        figure = self.figure()
        green = [t for t in figure['data'] if t.get('line', {}).get('color') == '#15803d']
        self.assertEqual(len(green), 3)
        self.assertEqual(len(figure['layout']['annotations']), 15)
        self.assertGreater(len(self.app.dataframe[0].value), 0)

    def test_blocking_recalculates_and_reset_restores(self):
        self.app.multiselect(key='blocked').set_value(['A-D']).run()
        self.assert_healthy()
        self.assertEqual(self.distance(), '1400 m')
        red = [t for t in self.figure()['data'] if t.get('line', {}).get('color') == '#dc2626']
        self.assertEqual(len(red), 1)
        self.assertEqual(red[0]['line']['dash'], 'dash')
        self.app.selectbox(key='source').set_value('C')
        self.app.selectbox(key='target').set_value('J').run()
        self.app.button(key='reset').click().run()
        self.assert_healthy()
        self.assertEqual(self.app.selectbox(key='source').value, 'A')
        self.assertEqual(self.app.selectbox(key='target').value, 'I')
        self.assertEqual(self.app.multiselect(key='blocked').value, [])
        self.assertEqual(self.distance(), '1200 m')

    def test_unreachable_has_no_green_route(self):
        self.app.multiselect(key='blocked').set_value(['G-I', 'H-I']).run()
        self.assert_healthy()
        self.assertTrue(any('tidak dapat dijangkau' in w.value for w in self.app.warning))
        self.assertEqual(self.distance(), 'Tidak terjangkau')
        self.assertTrue(any('NetworkX' in s.value for s in self.app.success))
        self.assertFalse(any(t.get('line', {}).get('color') == '#15803d' for t in self.figure()['data']))

    def test_source_is_shelter(self):
        self.app.selectbox(key='source').set_value('I').run()
        self.assert_healthy()
        self.assertEqual(self.distance(), '0 m')
        self.assertEqual(len(self.app.dataframe[0].value), 1)


if __name__ == '__main__':
    unittest.main()
