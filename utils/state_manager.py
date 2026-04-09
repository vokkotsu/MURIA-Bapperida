# utils/state_manager.py
import streamlit as st
import json
import os
import copy

# Pindahkan file database ke dalam folder 'data' agar direktori root tetap bersih
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data_bapperida.json")
CONFIG_FILE_KMEANS = os.path.join(DATA_DIR, "config_kmeans.json")

def pastikan_folder_ada():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# --- FUNGSI MANAJEMEN DATA JSON ---
def muat_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def simpan_data(data):
    pastikan_folder_ada()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def muat_config_kmeans():
    if os.path.exists(CONFIG_FILE_KMEANS):
        try:
            with open(CONFIG_FILE_KMEANS, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def simpan_config_kmeans(data):
    pastikan_folder_ada()
    with open(CONFIG_FILE_KMEANS, "w") as f:
        json.dump(data, f, indent=4)

# --- INISIALISASI SESSION STATE & HISTORY UNDO/REDO ---
def init_session_state():
    if "koleksi_tabel" not in st.session_state: 
        st.session_state.koleksi_tabel = muat_data() 
        
    if "form_step" not in st.session_state: st.session_state.form_step = 0
    if "angka_acak_sementara" not in st.session_state: st.session_state.angka_acak_sementara = {}
    if "temp_judul" not in st.session_state: st.session_state.temp_judul = ""
    if "temp_jml_kolom" not in st.session_state: st.session_state.temp_jml_kolom = 1
    if "temp_kolom_names" not in st.session_state: st.session_state.temp_kolom_names = []

def init_history(tabel):
    if 'history' not in tabel:
        tabel['history'] = [{
            'data': copy.deepcopy(tabel['data']),
            'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
            'hapus_jumlah': tabel.get('hapus_jumlah', False),
            'active_sort_col': tabel['active_sort_col']
        }]
        tabel['history_index'] = 0