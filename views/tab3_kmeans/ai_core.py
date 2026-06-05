# views/tab3_kmeans/ai_core.py
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA
import textwrap
from utils.constants import KECAMATAN_KUDUS_MAP

def proses_kmeans(df_untuk_ai, df_master, fitur_terpilih, n_clusters, bobot_baru, sensitivitas):
    try:
        X = df_untuk_ai[fitur_terpilih]
        
        if X.std().sum() == 0:
            return None, "🚨 Data terlalu seragam (semua kecamatan nilainya sama). AI tidak dapat membedakan mana wilayah yang Kritis dan mana yang Aman."
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        X_scaled_weighted = X_scaled.copy()
        for i, fitur in enumerate(fitur_terpilih):
            weight = bobot_baru.get(fitur, 1.0)
            X_scaled_weighted[:, i] *= weight
            
        if sensitivitas > 1.0:
            X_scaled_weighted = np.sign(X_scaled_weighted) * (np.abs(X_scaled_weighted) ** sensitivitas)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        klaster_mentah = kmeans.fit_predict(X_scaled_weighted)
        
        rata_rata_klaster = []
        for i in range(n_clusters):
            rata_rata_klaster.append(X_scaled_weighted[klaster_mentah == i].mean())
        
        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
        
        label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
        
        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
        
        nilai_inertia = kmeans.inertia_
        
        try:
            if 1 < n_clusters < len(X_scaled_weighted):
                sil_score = silhouette_score(X_scaled_weighted, klaster_mentah)
                sil_samples = silhouette_samples(X_scaled_weighted, klaster_mentah)
            else:
                sil_score = 0.0
                sil_samples = np.zeros(len(X_scaled_weighted))
        except Exception:
            sil_score = 0.0
            sil_samples = np.zeros(len(X_scaled_weighted))
            
        if len(fitur_terpilih) >= 2:
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(X_scaled_weighted)
            pca_x = pca_result[:, 0]
            pca_y = pca_result[:, 1]
        else:
            pca_x = X_scaled_weighted[:, 0]
            pca_y = np.zeros(len(X_scaled_weighted))

        elbow_k = []
        elbow_inertia = []
        max_k_test = min(9, len(X_scaled_weighted))
        
        for k in range(1, max_k_test):
            km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
            km_test.fit(X_scaled_weighted)
            elbow_k.append(k)
            elbow_inertia.append(km_test.inertia_)
            
        st.session_state.ai_metrics = {
            'silhouette': sil_score,
            'inertia': nilai_inertia,
            'sil_samples': sil_samples.tolist(),
            'pca_x': pca_x.tolist(),
            'pca_y': pca_y.tolist(),
            'kecamatan_list': df_master['Kecamatan'].tolist(),
            'zona_list': df_master['Status Zona'].tolist(),
            'elbow_k': elbow_k,
            'elbow_inertia': elbow_inertia,
            'current_k': n_clusters
        }

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