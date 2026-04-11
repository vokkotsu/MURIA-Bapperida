🏔️ MURIA: Mesin Utama Rencana & Intervensi Area

MURIA (Multidimensional Regional Intelligent Analytics) adalah sebuah Sistem Pendukung Keputusan (DSS) dan aplikasi Kecerdasan Buatan (AI) Spasial yang dikembangkan khusus untuk Badan Perencanaan Pembangunan, Riset, dan Inovasi Daerah (Bapperida) Kabupaten Kudus.

Aplikasi web pintar ini menggabungkan metode perhitungan Scoring tradisional dengan Machine Learning (Algoritma K-Means Clustering) untuk membantu pemangku kebijakan menentukan prioritas intervensi pembangunan wilayah (Kecamatan) secara cerdas, cepat, dan berbasis data (Data-Driven).

✨ Fitur Utama (Update Terbaru)

🏠 1. Beranda Executive (Executive Dashboard)

Ringkasan Cepat: Menampilkan Key Performance Indicators (KPI) seperti total indikator yang dianalisis dan status sistem AI.

Deteksi Wilayah Kritis Dinamis: AI secara otomatis mendeteksi jumlah kecamatan yang masuk ke dalam zona terparah/paling kritis.

Top 5 Prioritas: Grafik Bar Chart interaktif yang menampilkan 5 kecamatan dengan skor kebutuhan intervensi tertinggi (mendukung penanganan nilai seri/seimbang).

📝 2. Manajemen Data Indikator (Smart Input)

Auto Import Cerdas: Mendukung unggah file CSV/Excel dengan fitur penyesuaian baris Header (bebas dari error Unnamed column).

Sanitasi Data Otomatis: Sistem otomatis membersihkan data kotor dari BPS (seperti sel kosong, tanda strip -, atau format koma) menjadi angka murni (0).

Data Editor Interaktif: Tabel dapat diedit secara langsung dengan fitur Undo/Redo kolom, manajemen arah panah (Terkecil/Terbesar), dan format pemisah ribuan otomatis.

🏆 3. Peringkat Akumulasi (Scoring System)

Kalkulasi Otomatis: Mengubah peringkat sektoral menjadi poin akumulasi untuk menentukan prioritas utama.

Proporsi Data Asli: Visualisasi Pie Chart (Plotly) untuk melihat perbandingan angka mentah antar kecamatan.

Ekspor Laporan: Tabel hasil peringkat dapat diunduh langsung ke dalam format Excel (.xlsx).

🗺️ 4. AI Peta Zonasi (K-Means Spatial Clustering)

Klastering Multi-Dimensi: Pengelompokan wilayah secara otomatis (2 hingga 4 Zona) menggunakan model algoritma Scikit-Learn.

Peta WebGIS Interaktif: Visualisasi arsiran peta wilayah Kabupaten Kudus menggunakan Folium.

Ekspor Ganda:

🗺️ Unduh Peta menjadi file HTML Interaktif (bisa dibuka offline tanpa kehilangan fitur zoom/klik).

📥 Unduh Tabel Rincian Anggota Klaster ke format Excel (.xlsx).

📁 Struktur Proyek Modular

Proyek ini telah di-refactor menggunakan arsitektur modular agar mudah dipelihara dan dikembangkan oleh staf IT Bapperida/Kominfo di masa depan:

muria-bapperida-kudus/
├── app.py                      # File Utama & Injeksi CSS (Navigasi Sidebar)
├── requirements.txt            # Daftar dependensi pustaka Python
├── README.md                   # Dokumentasi Proyek
├── data/                       # Database Lokal (JSON) & Spasial
│   ├── kudus_kecamatan.geojson # Data Batas Wilayah GeoJSON
│   ├── config_kmeans.json      # Memori Konfigurasi AI
│   └── data_bapperida.json     # Penyimpanan utama tabel indikator
├── utils/                      # Fungsi Bantuan (Logika murni)
│   ├── constants.py            # Daftar nama kecamatan & koordinat
│   ├── state_manager.py        # Pengelola Session State & File JSON
│   └── styling.py              # Fungsi pewarnaan gradasi tabel
└── views/                      # Antarmuka Pengguna (UI Layer)
    ├── home/                   # Modul 1: Beranda Executive
    ├── tab1_input/             # Modul 2: Form Import & Tabel Editor
    ├── tab2_scoring/           # Modul 3: Tabel Peringkat & Pie Chart
    └── tab3_kmeans/            # Modul 4: K-Means & WebGIS Peta


🛠️ Teknologi yang Digunakan

Aplikasi ini berjalan sepenuhnya menggunakan ekosistem Python (3.10+):

Antarmuka Web: Streamlit

Manipulasi Data: Pandas & NumPy

Kecerdasan Buatan: Scikit-Learn

Visualisasi Spasial (Peta): Folium & Streamlit-Folium

Visualisasi Grafik: Plotly Express

Utilitas Berkas: Openpyxl & IO

🚀 Panduan Instalasi & Menjalankan Aplikasi (Lokal/Server)

Kloning Repositori:

git clone [https://github.com/username-anda/muria-bapperida-kudus.git](https://github.com/username-anda/muria-bapperida-kudus.git)
cd muria-bapperida-kudus


Instalasi Pustaka (Dependencies):
Sangat disarankan untuk menggunakan Virtual Environment (opsional). Jalankan perintah berikut untuk menginstal semua kebutuhan:

pip install -r requirements.txt


Jalankan Aplikasi:

streamlit run app.py


Aplikasi akan otomatis terbuka di peramban (browser) Anda pada alamat http://localhost:8501.