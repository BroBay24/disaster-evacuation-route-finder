"""Antarmuka simulasi akademik. Jalankan: streamlit run app.py."""

import math

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dijkstra import dijkstra
from graph_data import build_graph


def reset_simulation():
    """Callback berjalan sebelum widget dirender ulang oleh Streamlit."""
    st.session_state.update(source='A', target='I', blocked=[])


def draw_graph(graph, blocked, path, source, target):
    """Gambar seluruh jaringan; jalan tertutup tetap terlihat tetapi tak dilalui."""
    figure = go.Figure()
    route_edges = {frozenset((u, v)) for u, v in zip(path, path[1:])}
    legends = set()
    for u, v, data in graph.edges(data=True):
        key = f'{u}-{v}'
        if key in blocked:
            status, color, width, dash = 'Jalan terblokir', '#dc2626', 3, 'dash'
        elif frozenset((u, v)) in route_edges:
            status, color, width, dash = 'Jalur terpendek', '#15803d', 5, 'solid'
        else:
            status, color, width, dash = 'Jalan terbuka', '#94a3b8', 2, 'solid'
        x0, y0 = graph.nodes[u]['pos']
        x1, y1 = graph.nodes[v]['pos']
        figure.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode='lines',
            line=dict(color=color, width=width, dash=dash),
            name=status, legendgroup=status, showlegend=status not in legends,
            hovertemplate=f'{u} ↔ {v} · {data["weight"]} m<br>{status}<extra></extra>',
        ))
        legends.add(status)
        figure.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=f'{data["weight"]} m', showarrow=False,
            font=dict(size=12, color=color), bgcolor='rgba(255,255,255,0.92)',
        )
    for shelter, name, symbol, color in [
        (False, 'Lokasi / persimpangan', 'circle', '#2563eb'),
        (True, 'Shelter evakuasi', 'diamond', '#7c3aed'),
    ]:
        nodes = [n for n, d in graph.nodes(data=True) if d['shelter'] == shelter]
        labels = []
        for node in nodes:
            role = ' (awal & tujuan)' if node == source == target else (
                ' (awal)' if node == source else ' (tujuan)' if node == target else '')
            labels.append(node + role)
        figure.add_trace(go.Scatter(
            x=[graph.nodes[n]['pos'][0] for n in nodes],
            y=[graph.nodes[n]['pos'][1] for n in nodes],
            mode='markers+text', text=labels, textposition='top center',
            textfont=dict(size=13, color='#0f172a'), name=name,
            marker=dict(size=23, symbol=symbol, color=color,
                        line=dict(width=2, color='white')),
            customdata=[f'{n} · {graph.nodes[n]["name"]}' for n in nodes],
            hovertemplate='%{customdata}<extra></extra>',
        ))
    figure.update_layout(
        height=540, margin=dict(l=25, r=25, t=45, b=15),
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='#0f172a'), hovermode='closest',
        legend=dict(orientation='h', y=1.13, x=0),
        xaxis=dict(visible=False, range=[-0.8, 8]),
        yaxis=dict(visible=False, range=[-2.8, 5.1]),
        uirevision='evacuation-layout',
    )
    return figure


def main():
    st.set_page_config(page_title='Disaster Evacuation Route Finder', page_icon='🛟', layout='wide')
    graph = build_graph()
    shelters = [n for n, data in graph.nodes(data=True) if data['shelter']]
    roads = {f'{u}-{v}': (u, v) for u, v in graph.edges}

    with st.sidebar:
        st.header('Pengaturan evakuasi')
        st.caption('Mode: Shortest Route · jarak dalam meter')
        source = st.selectbox('Titik awal warga', list(graph), key='source',
                              format_func=lambda n: f'{n} — {graph.nodes[n]["name"]}')
        target = st.selectbox('Tujuan evakuasi', shelters, key='target',
                              format_func=lambda n: f'{n} — {graph.nodes[n]["name"]}')
        blocked = st.multiselect(
            'Blokir jalan (dua arah)', list(roads), key='blocked',
            format_func=lambda key: f'{key} · {graph.edges[roads[key]]["weight"]} m',
            help='Pilih jalan terdampak. Hapus pilihan untuk membuka jalan kembali.',
        )
        st.button('Reset simulasi', key='reset', on_click=reset_simulation, width='stretch')
        st.caption('Rute dihitung ulang otomatis setiap kali pilihan berubah.')

    # Graf aktif identik dipakai kedua algoritma. Graf asli tetap utuh untuk gambar.
    active = graph.copy()
    active.remove_edges_from(roads[key] for key in blocked)
    adjacency = {u: {v: d['weight'] for v, d in active[u].items()} for u in active}
    path, distance, steps = dijkstra(adjacency, source, target)
    try:
        reference = nx.dijkstra_path_length(active, source, target, weight='weight')
    except nx.NetworkXNoPath:
        reference = math.inf
    valid = math.isclose(distance, reference, rel_tol=1e-9, abs_tol=1e-9)

    st.title('Disaster Evacuation Route Finder')
    st.caption('Pencarian Jalur Terpendek Evakuasi Bencana Menggunakan Algoritma Dijkstra')
    st.warning('Contoh Simulasi, Bukan Data Nyata ')
    for column, label, value in zip(st.columns(4),
                                    ['Lokasi', 'Jalan terbuka', 'Jalan terblokir', 'Shelter'],
                                    [len(graph), active.number_of_edges(), len(blocked), len(shelters)]):
        column.metric(label, value)

    st.subheader('Hasil pencarian')
    summary, route = st.columns([1, 3])
    summary.metric('Total jarak', f'{distance:g} m' if path else 'Tidak terjangkau')
    with route:
        if path:
            st.markdown('**' + ' → '.join(path) + '**')
            st.write(' → '.join(graph.nodes[n]['name'] for n in path))
            if source == target:
                st.info('Titik awal sudah berada di shelter tujuan; tidak perlu melewati jalan.')
        else:
            st.warning('Tujuan tidak dapat dijangkau dari titik awal. Buka jalan atau pilih shelter lain.')
    if valid:
        detail = f'{reference:g} m' if math.isfinite(reference) else 'tujuan sama-sama tidak terjangkau'
        st.success(f'Validasi NetworkX cocok: {detail}.')
    else:
        st.error('Validasi gagal: hasil manual berbeda dari NetworkX. Hasil tidak boleh digunakan.')

    st.subheader('Jaringan jalan evakuasi')
    st.plotly_chart(draw_graph(graph, blocked, path, source, target), width='stretch')
    st.caption('Hijau tebal: rute minimum · merah putus-putus: jalan terblokir · belah ketupat: shelter. '
               'Posisi skematis, bukan peta geografis atau skala jarak. Arahkan kursor untuk nama lokasi.')

    st.subheader('Tabel iterasi Dijkstra')
    st.caption('Satu baris = satu simpul yang jaraknya sudah dipastikan (settled). '
               'Snapshot setelah relaksasi; tujuan tidak direlaksasi karena pencarian berhenti di sana. '
               '∞ berarti belum ditemukan. Jarak simpul lain mungkin masih sementara.')
    rows = [{
        'Iterasi': step['step'], 'Simpul diproses': step['node'],
        'Jarak pasti (m)': step['distance'], 'Pembaruan tetangga': step['updates'],
        **{f'd({n})': '∞' if math.isinf(d) else f'{d:g}' for n, d in step['distances'].items()},
    } for step in steps]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')

    with st.expander('Lihat data lokasi dan jalan'):
        st.dataframe(pd.DataFrame([
            {'Node': n, 'Lokasi': d['name'], 'Jenis': 'Shelter' if d['shelter'] else 'Lokasi'}
            for n, d in graph.nodes(data=True)
        ]), hide_index=True, width='stretch')
        st.dataframe(pd.DataFrame([
            {'Jalan': key, 'Jarak (m)': graph.edges[edge]['weight'],
             'Status': 'Terblokir' if key in blocked else 'Terbuka'}
            for key, edge in roads.items()
        ]), hide_index=True, width='stretch')


if __name__ == '__main__':
    main()
