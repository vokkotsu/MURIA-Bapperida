import streamlit as st
import pandas as pd
import uuid
import random

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Prototipe Input Data Bapperida", layout="centered")

st.title("📊 Modul Input Data Spasial Manual")
st.markdown("Prototipe ini mendemonstrasikan input multi-kolom. Anda dapat mengurutkan prioritas tabel berdasarkan salah satu kolom pilihan Anda.")
st.markdown("---")

# --- INISIALISASI STATE (Memori Aplikasi) ---
if "koleksi_tabel" not in st.session_state:
    st.session_state.koleksi_tabel = []

# Status form: 0 (tutup), 1 (setup judul & jml kolom), 2 (isi data per kolom)
if "form_step" not in st.session_state:
    st.session_state.form_step = 0

if "angka_acak_sementara" not in st.session_state:
    st.session_state.angka_acak_sementara = {}

# Variabel sementara untuk multi-step form
if "temp_judul" not in st.session_state: st.session_state.temp_judul = ""
if "temp_jml_kolom" not in st.session_state: st.session_state.temp_jml_kolom = 1
if "temp_current_col_idx" not in st.session_state: st.session_state.temp_current_col_idx = 0
if "temp_data" not in st.session_state: st.session_state.temp_data = {}
if "temp_kolom_names" not in st.session_state: st.session_state.temp_kolom_names = []

DAFTAR_KECAMATAN = ["Kaliwungu", "Kota", "Jati", "Undaan", "Mejobo", "Jekulo", "Bae", "Gebog", "Dawe"]

# --- FUNGSI PEWARNAAN (GRADIENT LOGIC) ---
def konversi_hex_ke_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def beri_warna_tabel(df, warna_hex, arah_panah_bawah, target_col):
    """Fungsi untuk memberikan background transparan HANYA pada kolom Kecamatan berdasarkan target_col"""
    r, g, b = konversi_hex_ke_rgb(warna_hex)
    nilai_min = df[target_col].min()
    nilai_max = df[target_col].max()

    def style_row(row):
        nilai = row[target_col]
        if nilai_max == nilai_min:
            opacity = 0.5 
        else:
            rasio = (nilai - nilai_min) / (nilai_max - nilai_min)
            if not arah_panah_bawah:
                rasio = 1.0 - rasio
            opacity = 0.1 + (rasio * 0.9)

        color_style = f'background-color: rgba({r}, {g}, {b}, {opacity}); font-weight: 600;'
        return [color_style if col == 'Kecamatan' else '' for col in df.columns]

    return df.style.apply(style_row, axis=1)

# --- NAVIGASI TABS ---
tab1, tab2 = st.tabs(["📝 Tab 1: Tabel Indikator Terpisah", "🏆 Tab 2: Tabel Overlapping (Akumulasi Skor)"])

# =====================================================================
# TAB 1: PENGELOLAAN TABEL TERPISAH
# =====================================================================
with tab1:
    # --- FITUR TAMBAH DATA (WIZARD) ---
    if st.session_state.form_step == 0:
        if st.button("➕ Tambah Data Baru", type="primary"):
            st.session_state.form_step = 1
            st.session_state.temp_judul = ""
            st.session_state.temp_jml_kolom = 1
            st.rerun()

    # LANGKAH 1: Setup Judul dan Jumlah Kolom
    if st.session_state.form_step == 1:
        with st.container(border=True):
            st.subheader("Langkah 1: Pengaturan Tabel")
            judul_input = st.text_input("Judul Tabel (misal: Infrastruktur 2024)", value=st.session_state.temp_judul)
            jml_kolom = st.number_input("Berapa jumlah kolom yang ingin ditambahkan?", min_value=1, max_value=10, value=1, step=1)
            
            col_btn1, col_btn2 = st.columns([1, 4])
            if col_btn1.button("➡️ Mulai Isi Kolom", type="primary"):
                if judul_input.strip() == "":
                    st.warning("Judul tabel tidak boleh kosong!")
                else:
                    st.session_state.temp_judul = judul_input
                    st.session_state.temp_jml_kolom = jml_kolom
                    st.session_state.temp_current_col_idx = 0
                    st.session_state.temp_data = {"Kecamatan": DAFTAR_KECAMATAN.copy()}
                    st.session_state.temp_kolom_names = []
                    st.session_state.angka_acak_sementara = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                    st.session_state.form_step = 2
                    st.rerun()
            if col_btn2.button("Batal"):
                st.session_state.form_step = 0
                st.rerun()

    # LANGKAH 2: Isi Data per Kolom
    if st.session_state.form_step == 2:
        idx_sekarang = st.session_state.temp_current_col_idx
        total_kolom = st.session_state.temp_jml_kolom
        
        with st.container(border=True):
            st.subheader(f"Langkah 2: Mengisi Kolom {idx_sekarang + 1} dari {total_kolom}")
            
            # Input nama kolom dinamis
            nama_kolom = st.text_input("Judul Kolom Ini (misal: Panjang Jalan Rusak, Jumlah RTLH)", key=f"col_name_input_{idx_sekarang}")
            
            st.write("Masukkan nilai untuk masing-masing kecamatan:")
            grid_input = st.columns(3)
            
            # Render input kecamatan
            for i, kec in enumerate(DAFTAR_KECAMATAN):
                nilai_def = st.session_state.angka_acak_sementara.get(kec, 0)
                with grid_input[i % 3]:
                    # Nilai tidak perlu ditaruh di session state langsung, kita baca by key nanti
                    st.number_input(kec, value=nilai_def, step=1, key=f"val_{idx_sekarang}_{kec}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Kontrol tombol berdasarkan apakah ini kolom terakhir atau bukan
            if idx_sekarang < total_kolom - 1:
                if st.button("➡️ Lanjut Kolom Selanjutnya", type="primary"):
                    if not nama_kolom.strip():
                        st.warning("Judul kolom tidak boleh kosong!")
                    elif nama_kolom.strip().lower() == "jumlah":
                        st.warning("Nama 'Jumlah' dicadangkan oleh sistem. Pilih nama lain!")
                    elif nama_kolom in st.session_state.temp_kolom_names:
                        st.warning("Judul kolom sudah digunakan di tabel ini, pilih nama lain!")
                    else:
                        # Simpan data kolom ini
                        data_kolom = [st.session_state[f"val_{idx_sekarang}_{kec}"] for kec in DAFTAR_KECAMATAN]
                        st.session_state.temp_data[nama_kolom] = data_kolom
                        st.session_state.temp_kolom_names.append(nama_kolom)
                        
                        # Maju ke kolom berikutnya dan acak angka baru
                        st.session_state.temp_current_col_idx += 1
                        st.session_state.angka_acak_sementara = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                        st.rerun()
            else:
                if st.button("💾 Simpan Tabel", type="primary"):
                    if not nama_kolom.strip():
                        st.warning("Judul kolom tidak boleh kosong!")
                    elif nama_kolom.strip().lower() == "jumlah":
                        st.warning("Nama 'Jumlah' dicadangkan oleh sistem. Pilih nama lain!")
                    elif nama_kolom in st.session_state.temp_kolom_names:
                        st.warning("Judul kolom sudah digunakan di tabel ini, pilih nama lain!")
                    else:
                        # Simpan data kolom terakhir
                        data_kolom = [st.session_state[f"val_{idx_sekarang}_{kec}"] for kec in DAFTAR_KECAMATAN]
                        st.session_state.temp_data[nama_kolom] = data_kolom
                        st.session_state.temp_kolom_names.append(nama_kolom)
                        
                        # Gabungkan dan jadikan tabel resmi
                        tabel_baru = {
                            "id": str(uuid.uuid4()),
                            "judul": st.session_state.temp_judul,
                            "data": st.session_state.temp_data,
                            "kolom_numerik": st.session_state.temp_kolom_names,
                            "warna": "#FF4B4B", 
                            "active_sort_col": st.session_state.temp_kolom_names[0], # Default sort: kolom pertama
                            "panah_bawah": True 
                        }
                        st.session_state.koleksi_tabel.append(tabel_baru)
                        st.session_state.form_step = 0 # Tutup form
                        st.rerun()
            
            if st.button("Batalkan Pembuatan Tabel"):
                st.session_state.form_step = 0
                st.rerun()

    st.markdown("---")

    # --- TAMPILAN TABEL YANG SUDAH DISIMPAN ---
    if not st.session_state.koleksi_tabel:
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' untuk memulai.")
    else:
        st.caption("💡 Tip: Klik tombol urutan di atas kolom untuk menjadikan kolom tersebut acuan peringkat.")
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            tabel_id = tabel['id']
            kolom_numerik = tabel['kolom_numerik']
            
            # HEADER TABEL (Judul & Kontrol Warna/Hapus)
            top_col1, top_col2, top_col3 = st.columns([7, 1, 1])
            top_col1.markdown(f"### {tabel['judul']}")
            
            warna_baru = top_col2.color_picker(
                "Warna", 
                value=tabel['warna'], 
                key=f"btn_warna_{tabel_id}", 
                label_visibility="collapsed"
            )
            if warna_baru != tabel['warna']:
                st.session_state.koleksi_tabel[i]['warna'] = warna_baru
                st.rerun()
                
            if top_col3.button("❌", key=f"btn_hapus_{tabel_id}", help="Hapus Data Ini"):
                st.session_state.koleksi_tabel.pop(i)
                st.rerun()

            # ROW TOMBOL SORTING EKSKLUSIF (Sebanyak jumlah kolom + 1 untuk Jumlah)
            st.markdown("**Acuan Urutan & Pewarnaan Tabel:**")
            kolom_tampil = kolom_numerik + ["Jumlah"]
            btn_cols = st.columns(len(kolom_tampil))
            
            for j, nama_col in enumerate(kolom_tampil):
                is_active = (tabel['active_sort_col'] == nama_col)
                # Tentukan ikon dan tampilan
                if is_active:
                    ikon = "⬇️" if tabel['panah_bawah'] else "⬆️"
                    btn_type = "primary" # Menonjol
                    help_text = "Aktif. Klik lagi untuk membalik arah urutan."
                else:
                    ikon = "⚪" 
                    btn_type = "secondary" # Pucat/Biasa
                    help_text = "Klik untuk menjadikan kolom ini sebagai acuan peringkat."
                
                with btn_cols[j]:
                    if st.button(f"{ikon} {nama_col}", key=f"sort_{tabel_id}_{nama_col}", type=btn_type, help=help_text, use_container_width=True):
                        if is_active:
                            # Jika sudah aktif, balik arah panah
                            st.session_state.koleksi_tabel[i]['panah_bawah'] = not tabel['panah_bawah']
                        else:
                            # Jika belum aktif, jadikan aktif dan reset panah ke bawah
                            st.session_state.koleksi_tabel[i]['active_sort_col'] = nama_col
                            st.session_state.koleksi_tabel[i]['panah_bawah'] = True
                        st.rerun()

            # PREPARASI DATAFRAME
            df = pd.DataFrame(tabel['data'])
            # Hitung kolom Jumlah otomatis
            df['Jumlah'] = df[kolom_numerik].sum(axis=1)
            
            # Urutkan berdasarkan kolom yang aktif
            active_col = tabel['active_sort_col']
            df = df.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            
            # Berikan warna gradient HANYA berdasarkan kolom yang aktif
            df_berwarna = beri_warna_tabel(df, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
            
            # Tampilkan editor
            edited_df = st.data_editor(
                df_berwarna, 
                use_container_width=True, 
                hide_index=True,
                disabled=["Kecamatan", "Jumlah"],
                key=f"editor_{tabel_id}"
            )
            
            # Update data jika di-edit (convert back to dict of lists, abaikan kolom Jumlah)
            data_baru = edited_df[["Kecamatan"] + kolom_numerik].to_dict(orient='list')
            if data_baru != tabel['data']:
                st.session_state.koleksi_tabel[i]['data'] = data_baru
                st.rerun()

            st.write("") 

# =====================================================================
# TAB 2: TABEL OVERLAPPING (AKUMULASI SKOR)
# =====================================================================
with tab2:
    st.subheader("🏆 Peringkat Akumulasi Prioritas Kecamatan")
    st.markdown("Skor ini dihitung **berdasarkan Kolom Acuan (yang bertombol merah)** pada masing-masing tabel di Tab 1. Kecamatan di posisi ke-1 pada suatu tabel mendapat 9 poin, ke-2 mendapat 8 poin, dst.")
    
    if not st.session_state.koleksi_tabel:
        st.info("Tambahkan minimal 1 tabel di 'Tab 1' untuk melihat perhitungan akumulasi poin.")
    else:
        # Menyiapkan kerangka data
        rekap_data = []
        for kec in DAFTAR_KECAMATAN:
            rekap_data.append({"Kecamatan": kec, "Total Poin": 0})
        df_rekap = pd.DataFrame(rekap_data)
        df_rekap.set_index("Kecamatan", inplace=True)
        
        # Menghitung poin dari SETIAP TABEL (hanya berpatokan pada kolom aktifnya saja)
        for tabel in st.session_state.koleksi_tabel:
            judul = tabel['judul']
            active_col = tabel['active_sort_col']
            kolom_numerik = tabel['kolom_numerik']
            
            # Hitung jumlah juga untuk keperluan tab overlapping jika 'Jumlah' menjadi active_col
            df_temp_full = pd.DataFrame(tabel['data'])
            df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
            
            df_temp = df_temp_full[['Kecamatan', active_col]]
            
            # Urutkan untuk menentukan peringkat dan poin
            df_temp = df_temp.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            
            df_temp['Posisi'] = range(1, len(DAFTAR_KECAMATAN) + 1)
            df_temp['Poin'] = range(len(DAFTAR_KECAMATAN), 0, -1)
            
            nama_kolom_posisi = f"Pos: {judul} ({active_col})"
            
            # Masukkan ke tabel rekap
            for _, row in df_temp.iterrows():
                kec = row['Kecamatan']
                posisi = row['Posisi']
                poin = row['Poin']
                
                df_rekap.at[kec, nama_kolom_posisi] = posisi # Tampilkan Posisi
                df_rekap.at[kec, "Total Poin"] += poin       # Tambah akumulasi poin
                
        # Format dan Sorting hasil rekap
        df_rekap = df_rekap.reset_index()
        df_rekap = df_rekap.sort_values(by="Total Poin", ascending=False).reset_index(drop=True)
        
        kolom_posisi = [col for col in df_rekap.columns if col.startswith("Pos:")]
        
        # Konversi posisi jadi integer
        for col in kolom_posisi:
            df_rekap[col] = df_rekap[col].fillna(0).astype(int)
            
        df_rekap = df_rekap[["Kecamatan"] + kolom_posisi + ["Total Poin"]]
        
        # Tampilkan tabel Heatmap
        st.dataframe(
            df_rekap.style.background_gradient(subset=["Total Poin"], cmap="Blues"),
            use_container_width=True, 
            hide_index=True
        )