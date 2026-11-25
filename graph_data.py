"""Jaringan jalan fiktif: 10 lokasi, 15 jalan dua arah, dan 2 shelter."""

import networkx as nx


def build_graph() -> nx.Graph:
    """Buat graf baru agar pemblokiran tidak mengubah data simulasi awal."""
    # Posisi hanya tata letak skematis; panjang garis bukan skala jarak jalan.
    nodes = [
        ('A', 'Permukiman Barat', (0, 2), False),
        ('B', 'Permukiman Utara', (1, 4), False),
        ('C', 'Pasar', (3, 4), False),
        ('D', 'Persimpangan Barat', (1, 1), False),
        ('E', 'Puskesmas', (3, 2), False),
        ('F', 'Persimpangan Timur', (5, 3), False),
        ('G', 'Sekolah', (2, -1), False),
        ('H', 'Balai Warga', (5, 0), False),
        ('I', 'Shelter Lapangan', (4, -2), True),
        ('J', 'Shelter Gedung Serbaguna', (7, 3), True),
    ]
    edges = [
        ('A', 'B', 300), ('A', 'D', 400), ('B', 'C', 250),
        ('B', 'E', 500), ('C', 'E', 300), ('C', 'F', 600),
        ('D', 'E', 200), ('D', 'G', 350), ('E', 'F', 250),
        ('E', 'H', 300), ('F', 'H', 200), ('F', 'J', 400),
        ('G', 'H', 250), ('G', 'I', 450), ('H', 'I', 300),
    ]
    graph = nx.Graph()
    for node, name, pos, shelter in nodes:
        graph.add_node(node, name=name, pos=pos, shelter=shelter)
    graph.add_weighted_edges_from(edges)
    return graph
