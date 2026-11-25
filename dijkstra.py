"""Dijkstra manual dengan min-heap; tidak bergantung pada NetworkX."""

import heapq
import math
from numbers import Real


def dijkstra(
    adjacency: dict[str, dict[str, float]], source: str, target: str
) -> tuple[list[str], float, list[dict]]:
    """Kembalikan (rute, jarak, iterasi); rute kosong dan inf jika terputus.

    Bobot harus numerik, finite, dan nonnegatif. Setiap iterasi mencatat
    satu node settled, setelah relaksasi tetangganya (kecuali node tujuan).
    Snapshot node lain masih dapat bersifat sementara saat pencarian berhenti.
    """
    if source not in adjacency or target not in adjacency:
        raise ValueError('Titik awal dan tujuan harus ada dalam graf.')
    # Validasi seluruh graf, termasuk komponen yang tidak terjangkau.
    for neighbors in adjacency.values():
        for neighbor, weight in neighbors.items():
            if neighbor not in adjacency:
                raise ValueError(f'Node tetangga {neighbor!r} tidak ada dalam graf.')
            if (isinstance(weight, bool) or not isinstance(weight, Real)
                    or not math.isfinite(weight) or weight < 0):
                raise ValueError('Bobot harus berupa angka finite dan tidak negatif.')

    distances = dict.fromkeys(adjacency, math.inf)
    distances[source] = 0
    previous = {}
    queue = [(0, source)]
    steps = []

    while queue:
        distance, node = heapq.heappop(queue)
        # Kandidat lama tidak dihitung sebagai iterasi atau diproses ulang.
        if distance != distances[node]:
            continue
        updates = []
        if node != target:
            for neighbor, weight in adjacency[node].items():
                candidate = distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = node
                    heapq.heappush(queue, (candidate, neighbor))
                    updates.append(f'{neighbor} = {candidate:g} m melalui {node}')
        steps.append({
            'step': len(steps) + 1,
            'node': node,
            'distance': distance,
            'updates': '; '.join(updates) or '—',
            'distances': distances.copy(),
        })
        if node == target:
            path = [target]
            while path[-1] != source:
                path.append(previous[path[-1]])
            return path[::-1], distance, steps

    return [], math.inf, steps
