# Disaster Evacuation Route Finder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Aplikasi simulasi akademik jalur evakuasi terpendek yang dapat dijalankan dengan `streamlit run app.py`.

**Architecture:** Data tetap membentuk NetworkX Graph. Dijkstra manual menerima adjacency mapping graf aktif; Streamlit menghitung ulang ketika pilihan berubah dan membandingkan jarak dengan NetworkX. Plotly menggambar seluruh jalan termasuk yang diblokir.

**Tech Stack:** Python 3.12, Streamlit, NetworkX, Plotly, heapq, Pandas, unittest.

**Spec:** `docs/superpowers/specs/2026-11-25-evacuation-design.md`

## Global Constraints
- Undirected Weighted Graph: 10 node, 15 edge, 2 shelter; bobot meter.
- Pemilihan awal, shelter tujuan, pemblokiran manual, hitung ulang otomatis, reset.
- Rute hijau, jalan terblokir merah, label jarak, tabel iterasi, validasi NetworkX.
- Tanpa database, API peta, login, risiko, estimasi waktu, atau dependensi tes tambahan.
- Komentar dan dokumentasi jelas; peringatan simulasi akademik selalu terlihat.
- Workspace bukan repositori Git; tidak membuat commit atau worktree.

## Review Focus
1. Tujuan terisolasi: hasil tidak terjangkau, bukan jarak nol.
2. Awal sama tujuan: rute satu node, jarak nol.
3. Rute optimal seri: validasi jarak, tidak mensyaratkan urutan identik.
4. Bobot negatif, NaN, infinity dan node tak dikenal: ditolak secara eksplisit.
5. Perubahan blokir/reset: tidak merusak data awal atau menampilkan hasil lama.

## Task 1: Data graf dan algoritma
**Files:** `graph_data.py`, `dijkstra.py`, `test_app.py`, `requirements.txt`.

**Interfaces:**
- `graph_data.build_graph() -> nx.Graph`: graf baru dengan atribut node `name`, `pos`, `shelter` dan edge `weight`.
- `dijkstra.dijkstra(adjacency: dict[str, dict[str, float]], source: str, target: str) -> tuple[list[str], float, list[dict]]`: rute, total, iterasi. Tidak terjangkau menghasilkan `([], math.inf, iterations)`. Iterasi memuat `step`, `node`, `distance`, `updates`, `distances`; snapshot bukan referensi bersama.

- [x] Tulis tes: 10 node/15 edge/2 shelter, graf terhubung, bobot positif, A ke I = 1200, seluruh pasangan dibandingkan dengan NetworkX pada graf normal dan setiap pemblokiran satu edge.
- [x] Tambahkan tes tujuan terisolasi, awal sama tujuan, rute seri, bobot nol, entri heap usang, bobot negatif/NaN/infinity, node tidak dikenal, dan graf baru tidak berbagi mutasi.
- [x] Jalankan `python -m unittest test_app -v`; pastikan gagal karena modul belum dibuat.
- [x] Implementasikan data sesuai desain dan Dijkstra heapq dengan validasi seluruh adjacency sebelum pencarian; lewati heap usang, simpan predecessor dan snapshot setelah relaksasi setiap simpul settled.
- [x] Pasang empat pustaka wajib melalui requirements di virtual environment; jalankan tes hingga lulus.

## Task 2: Antarmuka, visualisasi, dokumentasi
**Files:** `app.py`, `README.md`, perluas `test_app.py`.

**Interfaces:** Mengonsumsi `build_graph()` dan `dijkstra(...)` dari Task 1. Kontrol memiliki key `source`, `target`, `blocked`. Reset menggunakan callback sebelum widget dibangun ulang.

- [x] Tulis AppTest: tampilan awal tanpa exception dan hasil 1200; blokir seluruh edge menuju I menghasilkan pesan tidak terjangkau; reset memulihkan A/I/tanpa blokir dan 1200; awal I/tujuan I menghasilkan nol.
- [x] Jalankan tes UI dan pastikan gagal karena app belum dibuat.
- [x] Buat app dengan sidebar pilihan, judul/peringatan, ringkasan graf, hasil rute, Plotly berlabel, legenda, dan tabel iterasi Pandas. Validasi memakai graf aktif yang sama serta toleransi `math.isclose`; tampilkan mismatch sebagai error.
- [x] Tulis README: instalasi Python 3.12/venv, `pip install -r requirements.txt`, `streamlit run app.py`, `python -m unittest test_app -v`, definisi iterasi dan contoh blokir G–I serta H–I yang mengisolasi shelter I.
- [x] Jalankan semua tes, `python -m compileall app.py dijkstra.py graph_data.py test_app.py`, dan smoke test server Streamlit lokal. Dokumentasikan bila versi Python 3.12 tidak tersedia di host.
- [x] Lakukan review akhir terhadap spesifikasi, perbaiki temuan dan ulangi pengujian sebelum menyatakan selesai. Review independen: tidak ada temuan; verifikasi final 12/12 tes.
