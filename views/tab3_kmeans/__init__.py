# views/tab3_kmeans/__init__.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
from streamlit_folium import st_folium

from utils.constants import DAFTAR_KECAMATAN, KECAMATAN_KUDUS_MAP
from utils.state_manager import muat_config_kmeans, simpan_config_kmeans

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca indikator yang dipilih dan **menyelaraskan nilainya secara otomatis** (berdasarkan arah pengurutan Terbesar/Terkecil di Tab 1), lalu mengelompokkan kecamatan ke dalam zona prioritas (Natural Breaks/Multi-dimensional Clustering).")
    
    if not st.session_state.koleksi_tabel:
        st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
    else:
        df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
        df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN}) 
        fitur_tersedia = []
        
        for tabel in st.session_state.koleksi_tabel:
            df_tabel = pd.DataFrame(tabel['data'])
            arah_panah_bawah = tabel['panah_bawah'] 
            
            if len(tabel['kolom_numerik']) > 0:
                df_tabel['Jumlah'] = df_tabel[tabel['kolom_numerik']].sum(axis=1)
                kolom_analisis = tabel['kolom_numerik'] + ["Jumlah"]
            else:
                kolom_analisis = ["Jumlah"]
            
            for col in kolom_analisis:
                nama_unik = f"{col} ({tabel['judul']})"
                df_master[nama_unik] = df_tabel[col]
                
                if arah_panah_bawah:
                    df_untuk_ai[nama_unik] = df_tabel[col]
                else:
                    df_untuk_ai[nama_unik] = df_tabel[col] * -1 
                    
                fitur_tersedia.append(nama_unik)
        
        if len(fitur_tersedia) < 1:
            st.info("⚠️ AI K-Means membutuhkan minimal 1 indikator (kolom) untuk bisa mengelompokkan wilayah.")
        else:
            col_ai1, col_ai2 = st.columns([1, 2])
            
            with col_ai1:
                st.markdown("#### ⚙️ Pengaturan AI")
                
                config_ai = muat_config_kmeans()
                saved_features = config_ai.get('ai_selected_features', fitur_tersedia)
                valid_features = [f for f in saved_features if f in fitur_tersedia]
                
                if not valid_features and fitur_tersedia:
                    valid_features = fitur_tersedia

                fitur_terpilih = st.multiselect(
                    "Pilih Indikator yang Dianalisis:", 
                    fitur_tersedia, 
                    default=valid_features
                )
                
                if fitur_terpilih != config_ai.get('ai_selected_features'):
                    config_ai['ai_selected_features'] = fitur_terpilih
                    simpan_config_kmeans(config_ai)
                
                saved_cluster = config_ai.get('ai_n_clusters', 3)
                n_clusters = st.slider(
                    "Jumlah Zona Prioritas (Klaster)", 
                    min_value=2, max_value=4, 
                    value=saved_cluster, 
                    help="Membagi Kudus menjadi berapa kelompok?"
                )
                
                if n_clusters != config_ai.get('ai_n_clusters'):
                    config_ai['ai_n_clusters'] = n_clusters
                    simpan_config_kmeans(config_ai)
                
                warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
                label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
                
                if st.button("🚀 Jalankan AI K-Means", type="primary") or 'Klaster_ID' not in df_master.columns:
                    if len(fitur_terpilih) >= 1:
                        X = df_untuk_ai[fitur_terpilih]
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        klaster_mentah = kmeans.fit_predict(X_scaled)
                        
                        rata_rata_klaster = []
                        for i in range(n_clusters):
                            rata_rata_klaster.append(X_scaled[klaster_mentah == i].mean())
                        
                        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
                        
                        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
                        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
                        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
                        st.session_state.hasil_kmeans = df_master
            
            with col_ai2:
                if 'hasil_kmeans' in st.session_state:
                    df_hasil = st.session_state.hasil_kmeans
                    st.markdown("#### 🗺️ Peta Prioritas Wilayah")
                    
                    peta_kudus = folium.Map(location=[-6.8048, 110.8405], zoom_start=11)
                    for idx, row in df_hasil.iterrows():
                        koordinat = row['Koordinat']
                        klaster_id = row['Klaster_ID']
                        
                        tooltip_html = f"<b>{row['Kecamatan']}</b><br><i>{row['Status Zona']}</i><hr>"
                        for fitur in fitur_terpilih:
                            tooltip_html += f"<small>{fitur}: {row[fitur]}</small><br>"
                        
                        folium.Marker(
                            location=koordinat,
                            popup=folium.Popup(tooltip_html, max_width=300),
                            tooltip=row['Kecamatan'],
                            icon=folium.Icon(color=warna_klaster.get(klaster_id, 'blue'), icon='info-sign')
                        ).add_to(peta_kudus)
                    
                    st_folium(peta_kudus, width=700, height=450)
            
            st.markdown("#### 📊 Tabel Rincian Anggota Klaster")
            if 'hasil_kmeans' in st.session_state:
                df_tampil = st.session_state.hasil_kmeans[['Kecamatan', 'Status Zona'] + fitur_terpilih]
                df_tampil = df_tampil.sort_values(by="Status Zona")
                st.dataframe(df_tampil, use_container_width=True, hide_index=True)