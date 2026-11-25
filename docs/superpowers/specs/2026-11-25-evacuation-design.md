# Disaster Evacuation Route Finder — Desain

## Acuan dan tujuan
Spesifikasi pengguna terakhir: simulasi akademik pencarian rute evakuasi terpendek menggunakan Dijkstra manual. Bukan navigasi bencana nyata. Seluruh teks antarmuka dan dokumentasi berbahasa Indonesia, dengan judul aplikasi sesuai permintaan.

## Batasan
Python 3.12, Streamlit, NetworkX, Plotly, heapq, Pandas. Graf tak berarah, 10 node, 15 edge unik, 2 shelter, bobot jarak positif dalam meter. Tidak ada database, API peta, login, risiko, atau estimasi waktu.

## Pendekatan
Alternatif jarak, waktu, dan bobot gabungan sudah dibahas. Pengguna menetapkan jarak saja. Graf simulasi tetap lebih sesuai daripada editor graf atau data peta nyata karena jumlah node dan edge telah ditentukan. NetworkX memodelkan graf dan memvalidasi hasil; pencarian utama tetap implementasi heapq sendiri.

## Data dan perilaku (usulan implementasi)
- Node A–J: A Permukiman Barat, B Permukiman Utara, C Pasar, D Persimpangan Barat, E Puskesmas, F Persimpangan Timur, G Sekolah, H Balai Warga, I Shelter Lapangan, J Shelter Gedung Serbaguna.
- Edge dalam meter: A–B 300, A–D 400, B–C 250, B–E 500, C–E 300, C–F 600, D–E 200, D–G 350, E–F 250, E–H 300, F–H 200, F–J 400, G–H 250, G–I 450, H–I 300.
- Koordinat gambar berupa tata letak skematis, bukan koordinat geografis atau skala jarak. Jarak adalah data simulasi jalan.
- Awal dapat berupa salah satu dari 10 node; tujuan hanya I atau J. Jika awal sama dengan tujuan, hasil adalah satu node dengan jarak nol.
- Pengguna memblokir beberapa jalan melalui multiselect. Jalan tetap terlihat merah di gambar, tetapi tidak ada di graf aktif untuk kedua algoritma.
- Setiap perubahan pilihan otomatis menghitung ulang hasil. Reset mengembalikan awal A, tujuan I, dan membuka semua jalan.
- Plotly menampilkan label node, bobot meter, shelter berbeda simbol, jalan biasa abu-abu, rute hijau, dan jalan terblokir merah. Legenda dan teks status tidak bergantung pada warna saja.
- Hasil: urutan node beserta nama, total meter, dan status validasi NetworkX. Validasi membandingkan jarak minimum, bukan kesamaan rute, karena rute optimal dapat lebih dari satu.
- Tabel iterasi mencatat setiap node yang dipastikan jaraknya (settled), jarak kumulatif, perubahan tetangga, dan snapshot jarak sementara semua node. Entri heap usang tidak dihitung sebagai iterasi.
- Jika tujuan terisolasi, tampilkan pemberitahuan dan tabel penelusuran tanpa menggambar rute.

## Struktur
- `graph_data.py`: data dan pembuatan graf baru, tanpa mutasi data awal.
- `dijkstra.py`: validasi bobot, heapq, rekonstruksi rute, dan catatan iterasi; tidak memanggil algoritma NetworkX.
- `app.py`: kontrol Streamlit, graf aktif, Plotly, tabel Pandas, dan validasi NetworkX.
- `requirements.txt`: empat dependensi eksternal wajib dengan batas versi kompatibel Python 3.12.
- `README.md`: instalasi Windows/Linux, cara menjalankan, data kasus, algoritma, batasan, demonstrasi, dan pengujian.
- `test_app.py`: pengujian menggunakan unittest bawaan Python dan Streamlit AppTest; tanpa framework tes tambahan.

## Kriteria penerimaan
Data tepat 10/15/2. Contoh A ke I bernilai 1200 meter melalui A–D–G–I (rute optimal lain mungkin ada). Hasil seluruh pasangan cocok dengan NetworkX, termasuk setelah pemblokiran. Kasus terputus, awal sama tujuan, bobot nol pada algoritma generik, bobot negatif/non-finite, node tidak dikenal, dan reset diuji. Waktu proses bukan fitur aplikasi.
