# views/tab3_kmeans/ai_core.py
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score # IMPORT METRIK PENGUJIAN
import textwrap
from utils.constants import KECAMATAN_KUDUS_MAP

def proses_kmeans(df_untuk_ai, df_master, fitur_terpilih, n_clusters, bobot_baru, sensitivitas):
    """Memproses algoritma K-Means dengan pembobotan, sensitivitas, dan pengamanan error."""
    try:
        X = df_untuk_ai[fitur_terpilih]
        
        if X.std().sum() == 0:
            return None, "🚨 Data terlalu seragam (semua kecamatan nilainya sama). AI tidak dapat membedakan mana wilayah yang Kritis dan mana yang Aman. Silakan ubah bobot atau tambah indikator lain."
        
        # 1. Standarisasi
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 2. Terapkan Bobot
        X_scaled_weighted = X_scaled.copy()
        for i, fitur in enumerate(fitur_terpilih):
            weight = bobot_baru.get(fitur, 1.0)
            X_scaled_weighted[:, i] *= weight
            
        # 3. Terapkan Sensitivitas
        if sensitivitas > 1.0:
            X_scaled_weighted = np.sign(X_scaled_weighted) * (np.abs(X_scaled_weighted) ** sensitivitas)
        
        # 4. K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        klaster_mentah = kmeans.fit_predict(X_scaled_weighted)
        
        # PENGUJIAN MODEL (TESTING)
        # A. Menghitung Inertia (Kerapatan klaster, semakin kecil semakin baik)
        nilai_inertia = kmeans.inertia_
        
        # B. Menghitung Silhouette Score (Rentang -1 sampai 1, semakin mendekati 1 semakin baik)
        # Syarat Silhouette: Jumlah klaster harus > 1 dan < jumlah data
        try:
            if 1 < n_clusters < len(X_scaled_weighted):
                sil_score = silhouette_score(X_scaled_weighted, klaster_mentah)
            else:
                sil_score = 0.0
        except Exception:
            sil_score = 0.0
            
        # Menyimpan metrik pengujian ke memori Streamlit untuk ditampilkan di UI
        st.session_state.ai_metrics = {
            'silhouette': sil_score,
            'inertia': nilai_inertia
        }

        # 5. Sorting Centroid
        rata_rata_klaster = []
        for i in range(n_clusters):
            rata_rata_klaster.append(X_scaled_weighted[klaster_mentah == i].mean())
        
        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
        
        # 6. Memasukkan hasil
        label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
        
        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
        
        # 7. GAP ANALYSIS (Fokus Perbaikan)
        indikator_prioritas = ["-"] * len(df_master)
        idx_zona1 = df_master.index[df_master['Klaster_ID'] == 0].tolist()
        
        if idx_zona1:
            max_z1_scaled = X_scaled[idx_zona1].max(axis=0)
            for i in range(len(df_master)):
                if df_master.loc[i, 'Klaster_ID'] > 0: 
                    selisih_gap = X_scaled[i] - max_z1_scaled
                    idx_terparah = np.argmax(selisih_gap)
                    
                    nama_lengkap = fitur_terpilih[idx_terparah]
                    try:
                        nama_tabel_raw = nama_lengkap.split('(')[1].split(')')[0]
                        nama_tabel = "<br>".join(textwrap.wrap(nama_tabel_raw, width=25))
                    except IndexError:
                        nama_tabel = "<br>".join(textwrap.wrap(nama_lengkap, width=25)) 
                    
                    indikator_prioritas[i] = nama_tabel
                    
        df_master['Fokus_Perbaikan'] = indikator_prioritas
        
        return df_master, None
        
    except Exception as e:
        return None, f"🚨 Terjadi kesalahan matematis pada Mesin AI: {str(e)}"