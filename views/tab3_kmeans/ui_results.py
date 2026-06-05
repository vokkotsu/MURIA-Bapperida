# views/tab3_kmeans/ui_results.py
import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from views.tab3_kmeans.map_core import buat_peta

def konversi_df_ke_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil Zonasi')
    processed_data = output.getvalue()
    return processed_data

def format_angka_indo(val):
    try:
        if pd.isna(val):
            return "0"
        val = float(val)
        if val.is_integer():
            return f"{int(val):,}".replace(',', '.')
        else:
            s = f"{val:,.6f}".rstrip('0').rstrip('.')
            return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return val

def render_peta_zonasi(fitur_terpilih):
    if 'hasil_kmeans' in st.session_state:
        df_hasil = st.session_state.hasil_kmeans
        
        st.markdown("#### 🗺️ Peta Prioritas Wilayah")
        
        df_hasil_map = df_hasil.copy()
        if 'Koordinat' in df_hasil_map.columns:
            df_hasil_map['Koordinat'] = df_hasil_map['Koordinat'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
            
        peta_kudus = buat_peta(df_hasil_map, tuple(fitur_terpilih))
        
        st.write("")
        st_folium(peta_kudus, width=700, height=450, returned_objects=[])
        
        map_html = peta_kudus.get_root().render()
        st.download_button(
            label="🗺️ Unduh Peta (HTML Interaktif)",
            data=map_html,
            file_name='Peta_Zonasi_AI_Kudus.html',
            mime='text/html',
            use_container_width=True
        )

def render_tabel_zonasi(fitur_terpilih):
    metrics = st.session_state.get('ai_metrics', {})
    if metrics:
        sil_score = metrics.get('silhouette', 0.0)
        inertia_score = metrics.get('inertia', 0.0)
        
        if sil_score >= 0.5:
            sil_status = "🟢 Sangat Baik"
        elif sil_score >= 0.25:
            sil_status = "🟡 Cukup Baik"
        else:
            sil_status = "🔴 Tumpang Tindih"
            
        sil_tampil = f"{sil_score:.3f}".replace('.', ',')
        inertia_tampil = f"{inertia_score:.1f}".replace('.', ',')
            
        with st.container(border=True):
            st.markdown("#### 🧪 Hasil Pengujian K-Means (Model Evaluation)")
            c1, c2, c3 = st.columns(3)
            
            c1.metric("Silhouette Score (-1 s.d 1)", sil_tampil, sil_status, help="Mengukur tingkat ketepatan pembagian zona. Semakin mendekati 1 semakin bagus.")
            c2.metric("Inertia (Kerapatan Klaster)", inertia_tampil, help="Mengukur jarak antar data di dalam klaster yang sama. Semakin kecil nilainya semakin padat.")
            c3.metric("Status Data", "Tervalidasi ✔️", help="Model telah berhasil melakukan standarisasi (Standard Scaler) pada indikator untuk menyeimbangkan skala data.")
            
            if 'sil_samples' in metrics and len(metrics['sil_samples']) > 0:
                with st.expander("📈 Buka Visualisasi Grafik", expanded=False):
                    
                    df_grafik = pd.DataFrame({
                        'Kecamatan': metrics['kecamatan_list'],
                        'Zona': metrics['zona_list'],
                        'Silhouette Score': metrics['sil_samples'],
                        'PCA Komponen 1': metrics['pca_x'],
                        'PCA Komponen 2': metrics['pca_y']
                    })
                    
                    warna_zona = {
                        "Zona 1 (Aman/Rendah)": "#198754", 
                        "Zona 2 (Waspada)": "#fd7e14",      
                        "Zona 3 (Kritis)": "#dc3545",       
                        "Zona 4 (Sangat Kritis)": "#842029" 
                    }
                    
                    st.markdown("**1. Grafik PCA (Analisis Komponen Utama)**")
                    fig_pca = px.scatter(
                        df_grafik, x='PCA Komponen 1', y='PCA Komponen 2', 
                        color='Zona', text='Kecamatan', color_discrete_map=warna_zona,
                        title="Sebaran Data Wilayah (2 Dimensi)"
                    )
                    fig_pca.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                    fig_pca.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
                    st.plotly_chart(fig_pca, use_container_width=True)
                    
                    st.markdown("---")
                    
                    st.markdown("**2. Grafik Silhouette (Tingkat Kecocokan Zona)**")
                    df_sil = df_grafik.sort_values(by=['Zona', 'Silhouette Score'], ascending=[True, True])
                    fig_sil = px.bar(
                        df_sil, x='Silhouette Score', y='Kecamatan', 
                        color='Zona', orientation='h', color_discrete_map=warna_zona,
                        title=f"Skor Siluet per Kecamatan (Rata-Rata: {sil_tampil})"
                    )
                    fig_sil.add_vline(x=0, line_width=2, line_dash="dash", line_color="black")
                    fig_sil.update_layout(height=500, margin=dict(t=50, b=20, l=20, r=20), yaxis={'categoryorder':'array', 'categoryarray':df_sil['Kecamatan']})
                    st.plotly_chart(fig_sil, use_container_width=True)
                    
                    st.markdown("---")
                    
                    st.markdown("**3. Grafik Evaluasi Inertia (Elbow Method)**")
                    if 'elbow_k' in metrics and 'elbow_inertia' in metrics:
                        df_elbow = pd.DataFrame({
                            'Jumlah Klaster (K)': metrics['elbow_k'],
                            'Nilai Inertia': metrics['elbow_inertia']
                        })
                        
                        fig_elbow = px.line(
                            df_elbow, x='Jumlah Klaster (K)', y='Nilai Inertia', 
                            markers=True, title="Metode Elbow (Pencarian Jumlah Zona Optimal)"
                        )
                        fig_elbow.update_traces(marker=dict(size=10, color="#0d6efd"), line=dict(color="#0d6efd", width=3))
                        
                        current_k = metrics.get('current_k', 3)
                        fig_elbow.add_vline(
                            x=current_k, line_width=2, line_dash="dash", line_color="red",
                            annotation_text=f"Pilihan Saat Ini (K={current_k})", 
                            annotation_position="top right"
                        )
                        
                        fig_elbow.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
                        st.plotly_chart(fig_elbow, use_container_width=True)

    st.markdown("#### 📊 Tabel Rincian Anggota Klaster")
    
    if 'hasil_kmeans' in st.session_state:
        df_asli = st.session_state.hasil_kmeans
        
        col_tg, _ = st.columns([2, 1])
        with col_tg:
            mode_terbalik = st.toggle("🗣️ Gunakan Mode Rasio Terbalik")

        df_tampil = df_asli.copy()
        
        # Menghapus Fokus_Perbaikan dari list kolom yang ditampilkan
        kolom_yang_ditampilkan = ['Kecamatan', 'Status Zona']
        kolom_yang_ditampilkan.extend(list(fitur_terpilih))
        
        if mode_terbalik:
            for col in fitur_terpilih:
                if "[Dibagi" in col:
                    nama_human = col + " (Human Ratio)"
                    if nama_human in df_tampil.columns:
                        df_tampil[col] = df_tampil[nama_human]
                        
        df_tampil = df_tampil[kolom_yang_ditampilkan].sort_values(by="Status Zona")
        
        config_kolom_tab3 = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan", width="medium"),
            "Status Zona": st.column_config.TextColumn("Status Zona", width="medium")
        }
        
        for fitur in fitur_terpilih:
            fitur_singkat = fitur if len(fitur) <= 20 else fitur[:20] + "..."
            label_tambahan = " (Terbalik)" if mode_terbalik and "[Dibagi" in fitur else ""
            config_kolom_tab3[fitur] = st.column_config.Column(
                label=fitur_singkat + label_tambahan,
                help=f"Indikator Asli: {fitur}",
                width=240
            )
        
        formatter_dict = {fitur: format_angka_indo for fitur in fitur_terpilih}
        
        st.dataframe(
            df_tampil.style.format(formatter=formatter_dict), 
            use_container_width=True, 
            hide_index=True,
            column_config=config_kolom_tab3
        )
        
        excel_data_ai = konversi_df_ke_excel(df_tampil)
        st.download_button(
            label="📥 Unduh Tabel Zonasi (Excel / .xlsx)",
            data=excel_data_ai,
            file_name='Hasil_Klastering_Zonasi_Kudus.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type="primary"
        )