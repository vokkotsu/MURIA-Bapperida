# app.py
import streamlit as st
from utils.state_manager import init_session_state
from views.tab1_input import render_tab1
from views.tab2_scoring import render_tab2
from views.tab3_kmeans import render_tab3

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="DSS & AI Clustering Bapperida", layout="wide", initial_sidebar_state="collapsed")

# --- INISIALISASI MEMORI ---
init_session_state()

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("🧭 Navigasi Menu")
    st.markdown("Pilih menu di bawah ini untuk berpindah halaman.")
    st.markdown("---")

    menu_list = [
        "📝 Input Data Indikator", 
        "🏆 Peringkat Akumulasi (Scoring)",
        "🗺️ AI Peta Zonasi (K-Means)"
    ]

    try:
        query_params = st.query_params
        default_menu = query_params.get("menu", menu_list[0])
        if default_menu not in menu_list:
            default_menu = menu_list[0]
    except AttributeError:
        query_params = st.experimental_get_query_params()
        default_menu = query_params.get("menu", [menu_list[0]])[0]
        if default_menu not in menu_list:
            default_menu = menu_list[0]

    if "active_menu_selector" not in st.session_state:
        st.session_state.active_menu_selector = default_menu

    def ganti_menu(menu_baru):
        st.session_state.active_menu_selector = menu_baru
        try:
            st.query_params["menu"] = menu_baru
        except AttributeError:
            st.experimental_set_query_params(menu=menu_baru)

    for menu in menu_list:
        tipe_tombol = "primary" if st.session_state.active_menu_selector == menu else "secondary"
        
        if st.button(menu, type=tipe_tombol, use_container_width=True):
            ganti_menu(menu)
            st.rerun()
    
    st.markdown("---")
    st.caption("✨ DSS & AI Spasial Bapperida")

selected_menu = st.session_state.active_menu_selector

# --- HEADER APLIKASI (KONTEN UTAMA) ---
st.title("📊 Sistem Pendukung Keputusan & AI Spasial")
st.markdown("Aplikasi ini menggabungkan metode *Scoring* tradisional dengan *Machine Learning* (K-Means) untuk menentukan prioritas wilayah secara cerdas.")
st.markdown("---")

# --- MEMANGGIL TAMPILAN BERDASARKAN MENU ---
if selected_menu == menu_list[0]:
    render_tab1()
elif selected_menu == menu_list[1]:
    render_tab2()
elif selected_menu == menu_list[2]:
    render_tab3()