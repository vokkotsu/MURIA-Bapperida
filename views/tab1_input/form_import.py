# views/tab1_input/form_import.py
import streamlit as st
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN

def render_step_4():
    with st.container(border=True):
        st.subheader("📁 Auto Import Data")
        st.markdown("Unggah file CSV atau Excel (.xlsx). Program akan mendeteksi dan mengambil data secara otomatis.")
        
        uploaded_file = st.file_uploader("Pilih file CSV / Excel", type=['csv', 'xlsx'])
        
        if uploaded_file is not None:
            if st.session_state.get('last_uploaded_filename') != uploaded_file.name:
                nama_tanpa_ext = uploaded_file.name.rsplit('.', 1)[0]
                nama_rapi = nama_tanpa_ext.replace('_', ' ').replace('-', ' ').title()
                st.session_state.temp_judul_import = nama_rapi
                st.session_state.last_uploaded_filename = uploaded_file.name
                st.rerun()
        else:
            st.session_state.last_uploaded_filename = None
            
        if 'temp_judul_import' not in st.session_state:
            st.session_state.temp_judul_import = ""
        
        judul_input = st.text_input("Judul Tabel (Bisa diedit jika tidak sesuai)", key="temp_judul_import")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_import = pd.read_csv(uploaded_file)
                else:
                    df_import = pd.read_excel(uploaded_file)
                    
                st.success("✅ File berhasil dibaca!")
                
                kec_col_guess = None
                for col in df_import.columns:
                    if 'kecamatan' in col.lower() or 'wilayah' in col.lower() or 'nama' in col.lower():
                        kec_col_guess = col
                        break
                
                if not kec_col_guess and len(df_import.columns) > 0:
                    kec_col_guess = df_import.columns[0]
                    
                kecamatan_col = st.selectbox("Pilih kolom yang berisi nama Kecamatan:", options=df_import.columns, index=list(df_import.columns).index(kec_col_guess) if kec_col_guess else 0)
                
                st.markdown("#### Pilih Kolom Data yang Ingin Diimpor:")
                kolom_tersedia = [col for col in df_import.columns if col != kecamatan_col]
                kolom_terpilih = []
                
                cols = st.columns(3)
                for i, col in enumerate(kolom_tersedia):
                    with cols[i % 3]:
                        if st.checkbox(col, value=True, key=f"chk_import_{col}"):
                            kolom_terpilih.append(col)
                            
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                col_save, col_cancel = st.columns([1, 4])
                
                if col_save.button("➡️ Finalisasi Data", type="primary"):
                    if judul_input.strip() == "":
                        st.warning("Judul tabel tidak boleh kosong!")
                    elif not kolom_terpilih:
                        st.warning("Pilih minimal 1 kolom data untuk diimpor!")
                    else:
                        st.session_state.temp_judul = judul_input.strip() 
                        st.session_state.temp_jml_kolom = len(kolom_terpilih)
                        st.session_state.temp_kolom_names = kolom_terpilih
                        
                        extracted_data = {}
                        import_kec_list = df_import[kecamatan_col].astype(str).str.lower().str.strip().tolist()
                        
                        for idx, col_name in enumerate(kolom_terpilih):
                            extracted_data[idx] = {}
                            for kec in DAFTAR_KECAMATAN:
                                kec_lower = kec.lower()
                                try:
                                    row_idx = next(i for i, v in enumerate(import_kec_list) if kec_lower in v)
                                    raw_val = df_import.iloc[row_idx][col_name]
                                    try:
                                        val = float(raw_val)
                                        if val.is_integer():
                                            val = int(val)
                                    except:
                                        val = 0
                                except StopIteration:
                                    val = 0
                                extracted_data[idx][kec] = val
                                
                        st.session_state.angka_acak_sementara = extracted_data
                        st.session_state.form_step = 2
                        st.rerun()
                        
                if col_cancel.button("❌ Batal"):
                    st.session_state.form_step = 0
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Gagal memproses file: {e}")
        else:
            if st.button("⬅️ Kembali"):
                st.session_state.form_step = 0
                st.rerun()