# Disaster Evacuation Route Finder

Aplikasi Streamlit untuk **Pencarian Jalur Terpendek Evakuasi Bencana Menggunakan Algoritma Dijkstra**. Implementasi utama memakai `heapq` secara manual; NetworkX hanya membentuk graf dan menjadi pembanding hasil minimum.

> **Simulasi akademik dengan data fiktif, bukan sistem navigasi evakuasi bencana di dunia nyata.** Kondisi jalan, shelter, dan jarak tidak mewakili wilayah atau informasi bencana aktual.

## Instalasi dan menjalankan

Gunakan **Python 3.12**. Jalankan dari folder proyek.

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Jika aktivasi PowerShell dibatasi, tidak perlu mengubah execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Buka alamat lokal yang ditampilkan, biasanya **http://localhost:8501**. Hentikan server menggunakan `Ctrl+C`. Instalasi pertama membutuhkan internet; aplikasi tidak mengambil peta atau data eksternal saat dijalankan.

## Cara demonstrasi

1. Awal **A — Permukiman Barat**, tujuan **I — Shelter Lapangan**: rute `A → D → G → I`, jarak **1200 m** (`400 + 350 + 450`). Rute lain `A → D → E → H → I` juga memiliki jarak minimum 1200 m.
2. Blokir **A-D** di sidebar. Rute dihitung ulang menjadi `A → B → E → H → I`, jarak **1400 m**. Jalan A-D tetap terlihat merah putus-putus dan tidak dilalui.
3. Ganti pemblokiran menjadi **G-I** dan **H-I**. Shelter I terisolasi: tampil pesan **tujuan tidak dapat dijangkau**, bukan jarak nol. Tidak ada garis rute hijau.
4. Pilih tujuan **J — Shelter Gedung Serbaguna** untuk mencoba shelter lain; dari A dengan G-I dan H-I terblokir, jaraknya **1250 m** melalui `A → D → E → F → J`.
5. Pilih awal dan tujuan **I**: jarak **0 m**, satu node tanpa perjalanan.
6. Klik **Reset simulasi** untuk kembali ke awal A, tujuan I, dan membuka seluruh jalan.

Semua perubahan pilihan langsung memicu perhitungan ulang. Arahkan kursor pada simpul/garis untuk detail; Plotly mendukung zoom dan pan. Shelter berbentuk belah ketupat, lokasi lain berbentuk lingkaran. Hijau tebal menunjukkan rute minimum, merah putus-putus menunjukkan jalan tertutup. Data tabel juga menampilkan status jalan dalam teks.

## Studi kasus dan model graf

Wilayah permukiman fiktif mempunyai dua titik evakuasi. Warga memilih shelter, lalu aplikasi mencari total jarak terkecil berdasarkan jalan yang masih terbuka.

`G = (V, E, W)` adalah **undirected weighted graph**: 10 simpul, 15 jalan dua arah, 2 shelter. `V` adalah lokasi/persimpangan, `E` adalah jalan, dan `W` adalah jarak dalam meter. `S` adalah titik awal dan `T` shelter tujuan. Pemblokiran berlaku untuk kedua arah dan menghapus edge dari graf aktif, bukan sekadar memberinya bobot besar.

| Node | Lokasi | Shelter |
|---|---|---|
| A | Permukiman Barat | Tidak |
| B | Permukiman Utara | Tidak |
| C | Pasar | Tidak |
| D | Persimpangan Barat | Tidak |
| E | Puskesmas | Tidak |
| F | Persimpangan Timur | Tidak |
| G | Sekolah | Tidak |
| H | Balai Warga | Tidak |
| I | Shelter Lapangan | Ya |
| J | Shelter Gedung Serbaguna | Ya |

| Jalan | Jarak (m) | Jalan | Jarak (m) | Jalan | Jarak (m) |
|---|---:|---|---:|---|---:|
| A–B | 300 | A–D | 400 | B–C | 250 |
| B–E | 500 | C–E | 300 | C–F | 600 |
| D–E | 200 | D–G | 350 | E–F | 250 |
| E–H | 300 | F–H | 200 | F–J | 400 |
| G–H | 250 | G–I | 450 | H–I | 300 |

Posisi pada gambar hanya tata letak skematis, **bukan koordinat geografis atau skala jarak**. Bobot jalan merupakan data simulasi tersendiri. Tidak ada database, login, API peta, risiko, estimasi waktu, atau klaim bahwa rute terpendek adalah rute paling aman. Pengaturan hanya bertahan dalam sesi Streamlit, tidak disimpan permanen.

## Cara kerja Dijkstra

1. Set jarak awal ke 0 dan semua node lain ke tak hingga (`∞`).
2. Masukkan `(0, awal)` ke min-heap.
3. Ambil kandidat berjarak terkecil. Abaikan entri heap lama yang sudah digantikan oleh jarak lebih kecil.
4. Untuk setiap tetangga yang masih terhubung, hitung jarak kandidat. Jika lebih kecil, perbarui jarak/predecessor dan masukkan kandidat ke heap.
5. Berhenti ketika tujuan dikeluarkan dari heap; rekonstruksi rute melalui predecessor. Jika heap habis, tujuan tidak terjangkau.

Bobot harus numerik, finite, dan nonnegatif; data aplikasi memakai integer positif. Node tak dikenal dan bobot tidak valid ditolak dengan `ValueError`. Input algoritma adalah adjacency mapping; jalan terblokir sudah dikeluarkan oleh antarmuka sebelum pencarian.

### Tabel iterasi

Satu baris merepresentasikan satu simpul **settled** (jarak sudah pasti), bukan setiap operasi heap. Kolom menunjukkan simpul, jarak pasti, pembaruan tetangga, serta snapshot `d(A)` hingga `d(J)` setelah relaksasi. Tujuan tidak direlaksasi karena pencarian berhenti di sana. `∞` berarti belum ditemukan; snapshot simpul yang belum settled masih sementara, bukan hasil minimum semua simpul. Snapshot disalin agar iterasi sebelumnya tidak ikut berubah.

Untuk graf sederhana, inti Dijkstra heap memiliki waktu `O((V + E) log V)`. **Pencatatan snapshot untuk pembelajaran menambah waktu dan memori hingga O(V²)**; implementasi ini ditujukan untuk graf kecil 10 simpul, bukan jaringan jalan berskala besar.

### Validasi NetworkX

`nx.dijkstra_path_length` menggunakan graf aktif dan atribut `weight` yang sama. Jarak dibandingkan menggunakan `math.isclose`. Rute dengan urutan berbeda tetap valid jika jaraknya minimum karena solusi dapat seri. Jika NetworkX juga menyatakan tidak ada jalur, status ketakterjangkauan dinyatakan cocok. Ketidaksesuaian ditampilkan sebagai kesalahan.

## Pengujian

Setelah dependensi terpasang:

```bash
python -m unittest test_app -v
```

Tanpa aktivasi virtual environment di Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest test_app -v
```

Tes memakai `unittest` bawaan Python dan `streamlit.testing.v1.AppTest`; tidak perlu Pytest. Cakupan:

- Data graf 10/15/2, terhubung, bobot positif, dan salinan graf independen.
- Contoh manual A–I = 1200 m dan snapshot iterasi independen.
- **1600 kombinasi**: 100 pasangan awal–tujuan × 16 skenario (normal + setiap satu jalan diblokir), dibandingkan dengan NetworkX; rute juga diperiksa kontinuitas dan total bobotnya.
- Tujuan terisolasi, awal sama dengan tujuan, rute seri, bobot nol, dan entri heap usang.
- Penolakan bobot negatif/NaN/infinity/non-numerik serta node tidak dikenal.
- Integrasi UI: rute awal, hitung ulang setelah blokir, warna/status graf, kondisi terputus, jarak nol, dan reset.

AppTest dapat mengeluarkan peringatan `missing ScriptRunContext` pada thread utama dalam bare mode; peringatan tersebut bukan kegagalan tes. AppTest memeriksa struktur chart dan perilaku aplikasi, bukan tampilan piksel browser.

## Struktur file

```text
app.py            Antarmuka, visualisasi Plotly, validasi NetworkX
dijkstra.py       Algoritma manual heapq dan rekaman iterasi
graph_data.py     Data simulasi dan pembuatan graf baru
requirements.txt  Dependensi eksternal
README.md         Instalasi dan panduan demonstrasi
test_app.py       Tes algoritma dan integrasi Streamlit
```

Dokumen rancangan dan catatan implementasi tersimpan di `docs/superpowers/`.
