# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
import time # Untuk menghitung waktu proses
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import Birch
from sklearn.metrics import silhouette_score, davies_bouldin_score, silhouette_samples
# (MODIFIKASI) Import f_classif
from sklearn.feature_selection import f_classif
import numpy as np
import re # Untuk membersihkan nama sheet

# (BARU) Import untuk Grafik Silhouette & Scatter
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA # (BARU) Untuk Scatter Plot

# (MODIFIKASI) Import untuk menyisipkan gambar & auto-sizing
try:
    from openpyxl.drawing.image import Image
    from openpyxl.utils import get_column_letter # (BARU) Untuk auto-sizing
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


# Peta file untuk memetakan pilihan radio button ke nama file CSV
FILE_MAP = {
    "PAUD": "data/PAUD 2024.xlsx",
    "PKBM": "data/PKBM 2024.xlsx",
    "SD": "data/SD 2024.xlsx",
    "SLB": "data/SLB 2024.xlsx",
    "SMA": "data/SMA 2024.xlsx",
    "SMK": "data/SMK 2024.xlsx",
    "SMP": "data/SMP 2024.xlsx"
}

# Kolom untuk template Excel untuk User
TEMPLATE_COLUMNS = [
    'kecamatan', 'kelurahan', 'jenjang', 'nama_sekolah', 'jumlah_siswa', 
    'jumlah_guru', 'jumlah_tendik', 'jumlah_kamar_mandi_wc_guru_laki_laki', 
    'jumlah_kamar_mandi_wc_guru_perempuan', 'jumlah_kamar_mandi_wc_siswa_laki_laki', 
    'jumlah_kamar_mandi_wc_siswa_perempuan', 'jumlah_laboratorium_kimia', 
    'jumlah_ruang_guru', 'jumlah_ruang_kelas', 'jumlah_ruang_kepala_sekolah', 
    'jumlah_ruang_laboratorium_bahasa', 'jumlah_ruang_laboratorium_biologi', 
    'jumlah_ruang_laboratorium_fisika', 'jumlah_ruang_laboratorium_ipa', 
    'jumlah_ruang_laboratorium_komputer', 'jumlah_ruang_perpustakaan', 
    'jumlah_ruang_tu', 'jumlah_ruang_uks'
]
# Definisikan kolom teks dan integer untuk validasi
STRING_COLS = ['kecamatan', 'kelurahan', 'jenjang', 'nama_sekolah']
# Ambil semua kolom yang mulai dengan 'jumlah_'
INTEGER_COLS = [col for col in TEMPLATE_COLUMNS if col.startswith('jumlah_')]

# --- FUNGSI HELPER BARU ---

@st.cache_data 
def create_template_excel():
    """Membuat file Excel template di dalam memori."""
    df_template = pd.DataFrame(columns=TEMPLATE_COLUMNS)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='DataSekolah')
    processed_data = output.getvalue()
    return processed_data

# (FUNGSI BARU) Untuk auto-sizing kolom Excel
def auto_adjust_excel_columns(worksheet):
    """Mer resizing kolom di worksheet openpyxl berdasarkan konten."""
    for col in worksheet.columns:
        max_length = 0
        # Dapatkan huruf kolom (cth: 'A')
        column_letter = col[0].column_letter 
        
        # Iterasi setiap sel di kolom
        for cell in col:
            try:
                # Cek panjang value di sel (termasuk header)
                if cell.value:
                    # Konversi ke string dan hitung panjangnya
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass # Abaikan error jika ada
        
        # Atur lebar kolom
        # Tambah sedikit padding (misal, + 2)
        # Batasi lebar maksimum (misal 70) agar tidak terlalu lebar
        adjusted_width = min(max_length + 2, 70) 
        
        # Atur lebar minimum (misal 10)
        if adjusted_width < 10:
             adjusted_width = 10
             
        worksheet.column_dimensions[column_letter].width = adjusted_width


# (MODIFIKASI) Fungsi diubah untuk membuat DataFrame baru untuk Excel
# dari dictionary hasil analisis naratif
@st.cache_data
def convert_analysis_to_excel(analysis_dict):
    """Mengonversi dictionary hasil analisis naratif ke Excel."""
    output = io.BytesIO()
    
    # Buat list of dictionaries untuk DataFrame
    excel_data = []
    for cluster_name, details in analysis_dict.items():
        row = {"Cluster": cluster_name}
        # Gabungkan semua list karakteristik jadi satu string per kategori
        row["Rasio & Kepadatan"] = "; ".join(details.get("Rasio & Kepadatan", ["-"]))
        row["Fasilitas Lengkap"] = "; ".join(details.get("Fasilitas Lengkap", ["-"]))
        row["Fasilitas Kurang"] = "; ".join(details.get("Fasilitas Kurang", ["-"]))
        # row["Ciri Khas Lain"] = "; ".join(details.get("Ciri Khas Lain", ["-"])) # Ciri khas sudah masuk ke Fitur Pembeda
        
        # Tambahkan fitur pembeda utama (sampai 5)
        top_features = details.get("Fitur Pembeda", [])
        for i in range(5):
            if i < len(top_features):
                 row[f"Fitur Pembeda {i+1}"] = top_features[i]["Fitur"]
                 row[f"Status Fitur {i+1}"] = top_features[i]["Status"]
            else:
                 row[f"Fitur Pembeda {i+1}"] = "-"
                 row[f"Status Fitur {i+1}"] = "-"
            
        excel_data.append(row)
        
    df_excel = pd.DataFrame(excel_data)
    # Urutkan kolom jika perlu (sesuaikan nama kolom)
    col_order = ["Cluster", "Rasio & Kepadatan", "Fasilitas Lengkap", "Fasilitas Kurang"] + \
                [f"{kind} {i+1}" for i in range(5) for kind in ["Fitur Pembeda", "Status Fitur"]]
    # Filter kolom yang ada di DataFrame sebelum mengurutkan
    col_order = [col for col in col_order if col in df_excel.columns]
    df_excel = df_excel[col_order]

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='KarakteristikCluster')
        
        # Panggil fungsi auto-adjust
        if OPENPYXL_AVAILABLE:
            try:
                worksheet = writer.sheets['KarakteristikCluster']
                auto_adjust_excel_columns(worksheet)
            except Exception as e:
                st.warning(f"Gagal menyesuaikan lebar kolom: {e}")
                
    processed_data = output.getvalue()
    return processed_data


# (MODIFIKASI) Panggil auto_adjust_excel_columns
@st.cache_data
def convert_clusters_to_excel(df_results_download, df_results_display, features, pretty_names_map, cluster_col='Cluster'):
    """
    (MODIFIED)
    Mengonversi data anggota cluster ke file Excel, satu sheet per cluster.
    Juga mencoba menyisipkan box plot dari fitur-fitur yang di-scale untuk setiap cluster.
    """
    
    # Cek dependensi untuk plotting
    can_draw_plots = True
    if not OPENPYXL_AVAILABLE:
        st.warning("`openpyxl` tidak terinstal dengan lengkap. Plot tidak dapat ditambahkan ke Excel.", icon="⚠️")
        can_draw_plots = False
        
    try:
        import kaleido # Tes apakah kaleido terinstal
    except ImportError:
        st.warning("Library `kaleido` tidak ditemukan. Box plot tidak akan ditambahkan ke Excel. "
                 "Instal (`pip install kaleido`) untuk fitur ini.", icon="⚠️")
        can_draw_plots = False


    output = io.BytesIO()
    # Urutkan data berdasarkan cluster dan nama sekolah untuk konsistensi (download Data)
    df_sorted = df_results_download.sort_values(by=[cluster_col, 'nama_sekolah'])

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for cluster_name in sorted(df_sorted[cluster_col].unique()):
            
            # --- 1. Tabel Data Anggota (Logika Asli) ---
            df_cluster = df_sorted[df_sorted[cluster_col] == cluster_name].copy()
            df_cluster_output = df_cluster[['nama_sekolah', 'kecamatan', 'kelurahan']]
            df_cluster_output.reset_index(drop=True, inplace=True)
            df_cluster_output.index = df_cluster_output.index + 1
            df_cluster_output.index.name = "No"
            df_cluster_output.rename(columns={
                'nama_sekolah': 'Nama Sekolah', 
                'kecamatan': 'Kecamatan', 
                'kelurahan': 'Kelurahan'
            }, inplace=True)
            
            safe_sheet_name = re.sub(r'[\\/*?:\[\]]', '_', cluster_name)[:31] 
            df_cluster_output.to_excel(writer, index=True, sheet_name=safe_sheet_name) 
            
            # --- 2. Auto-size kolom (Logika Baru) ---
            if OPENPYXL_AVAILABLE:
                try:
                    worksheet = writer.sheets[safe_sheet_name]
                    auto_adjust_excel_columns(worksheet) # Panggil di sini
                except Exception as e:
                    st.warning(f"Gagal menyesuaikan lebar kolom untuk sheet '{safe_sheet_name}': {e}")

            # --- 3. Tambahkan Box Plot (Logika Lama) ---
            
    processed_data = output.getvalue()
    return processed_data


def clear_data_state():
    """Hapus data yang tersimpan jika user ganti sumber data."""
    keys_to_delete = [
        'data_to_process', 'file_name', 'analysis_results',
        'selected_pretty_features', 'selected_kecamatan',
        'selected_kelurahan' # (BARU) Hapus state kelurahan
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.auto_cluster = False
    st.session_state.auto_cluster_gabungan = False


def preprocess_data(df, features):
    """Membersihkan dan men-scaling data. Mengembalikan data asli & data yang di-scale."""
    df_processed = df[features].copy()
    df_processed.fillna(0, inplace=True)
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df_processed)
    # (BARU) Konversi hasil scaling kembali ke DataFrame untuk kemudahan
    df_scaled_processed = pd.DataFrame(df_scaled, index=df_processed.index, columns=features)
    return df_processed, df_scaled_processed

# (DIHAPUS) Fungsi get_feature_importance tidak dipakai lagi

# (DIHAPUS) Fungsi plot_feature_importance tidak dipakai lagi


# (MODIFIKASI) Fungsi ini sekarang menggunakan data ASLI (df_results)
def plot_individual_box_plots(df_results, features, pretty_names_map, cluster_col='Cluster'):
    """Membuat box plot terpisah untuk setiap fitur."""
    st.markdown("#### 2. Perbandingan Fitur Antar Cluster (Nilai Asli)") # Judul Bagian
    # (BARU) Tambahkan penjelasan box plot
    st.caption("""
        **Bagaimana membaca Box Plot ini?**
        Grafik ini menunjukkan **sebaran (distribusi) nilai asli** dari setiap fitur di dalam masing-masing cluster.
        - **Garis di tengah kotak:** Median (nilai tengah).
        - **Kotak (Box):** Menunjukkan rentang 50% data di bagian tengah.
        - **Garis (Whiskers):** Menunjukkan jangkauan data normal.
        - **Titik di luar garis:** Outlier (nilai ekstrem) dalam cluster tersebut.
        Ini **bukan rata-rata**, tapi gambaran lengkap sebaran nilai asli.
    """)
    
    color_map = {
        'Cluster 0': '#1f77b4', 'Cluster 1': '#ff7f0e', 'Cluster 2': '#2ca02c',
        'Cluster 3': '#d62728', 'Cluster 4': '#9467bd', 'Cluster 5': '#8c564b',
        'Cluster 6': '#e377c2', 'Cluster 7': '#7f7f7f', 'Cluster 8': '#bcbd22', 'Cluster 9': '#17becf', 'Cluster 10': '#17becf',
        'Inlier': '#FFC300', # Kuning
        'Outlier': '#900C3F', # Merah Tua
        'Cluster Outlier': '#900C3F' # Merah Tua
    }
    
    col1, col2 = st.columns(2)
    cols = [col1, col2]
    
    for i, feature in enumerate(features):
        with cols[i % 2]:
            fig = px.box(
                df_results,
                x=cluster_col,
                y=feature,
                color=cluster_col,
                title=f"Distribusi Fitur: {pretty_names_map[feature]}",
                color_discrete_map=color_map
            )
            # (MODIFIKASI) Ubah yaxis_title
            fig.update_layout(xaxis_title='Cluster', yaxis_title='Nilai Asli')
            st.plotly_chart(fig, use_container_width=True)

# (MODIFIKASI) Judul diubah ke "2. Persebaran..."
def plot_region_distribution_filtered(df_results, cluster_col='Cluster'):
    """Membuat bar chart persebaran cluster per kecamatan dengan filter multiselect."""
    st.markdown("#### 2. Persebaran Cluster per Kecamatan")
    
    if 'kecamatan' not in df_results.columns:
        st.warning("Kolom 'kecamatan' tidak ditemukan, tidak dapat menampilkan persebaran wilayah.")
        return
        
    df_region = df_results.groupby(['kecamatan', cluster_col]).size().reset_index(name='Jumlah')
    all_kecamatan = sorted(df_region['kecamatan'].unique().tolist())
    
    if 'selected_kecamatan' not in st.session_state:
        st.session_state.selected_kecamatan = all_kecamatan[:5] # Default 5 pertama

    col_k1, col_k2, col_k3_spacer = st.columns([1,1,2])
    with col_k1:
        if st.button("Pilih Semua Kecamatan"):
            st.session_state.selected_kecamatan = all_kecamatan
            st.rerun()
    with col_k2:
        if st.button("Hapus Semua Kecamatan"):
            st.session_state.selected_kecamatan = []
            st.rerun()

    selected_kecamatan = st.multiselect(
        "Pilih Kecamatan untuk ditampilkan:", 
        options=all_kecamatan, 
        default=st.session_state.selected_kecamatan,
        key="ms_kecamatan" # (BARU) Tambah key unik
    )
    st.session_state.selected_kecamatan = selected_kecamatan 
    
    if not selected_kecamatan:
        st.info("Silakan pilih satu atau lebih kecamatan untuk menampilkan grafik.")
        return

    df_region_filtered = df_region[df_region['kecamatan'].isin(selected_kecamatan)]
    
    fig = px.bar(
        df_region_filtered,
        x='kecamatan',
        y='Jumlah',
        color=cluster_col,
        title='Persebaran Cluster per Kecamatan (Data Terfilter)',
        color_discrete_map={
            'Cluster 0': '#1f77b4', 'Cluster 1': '#ff7f0e', 'Cluster 2': '#2ca02c',
            'Cluster 3': '#d62728', 'Cluster 4': '#9467bd', 'Cluster 5': '#8c564b',
            'Cluster 6': '#e377c2', 'Cluster 7': '#7f7f7f', 'Cluster 8': '#bcbd22', 'Cluster 9': '#17becf', 'Cluster 10': '#17becf',
            'Inlier': '#FFC300', # Kuning
            'Outlier': '#900C3F', # Merah Tua
            'Cluster Outlier': '#900C3F' # Merah Tua
        }
    )
    fig.update_layout(barmode='group', xaxis_title='Kecamatan', yaxis_title='Jumlah Sekolah', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# (FUNGSI BARU) Dibuat untuk plot persebaran per kelurahan
def plot_region_distribution_filtered_kelurahan(df_results, cluster_col='Cluster'):
    """Membuat bar chart persebaran cluster per kelurahan dengan filter multiselect."""
    st.markdown("#### 3. Persebaran Cluster per Kelurahan")
    
    if 'kelurahan' not in df_results.columns:
        st.warning("Kolom 'kelurahan' tidak ditemukan, tidak dapat menampilkan persebaran wilayah.")
        return
        
    df_region = df_results.groupby(['kelurahan', cluster_col]).size().reset_index(name='Jumlah')
    all_kelurahan = sorted(df_region['kelurahan'].unique().tolist())
    
    if 'selected_kelurahan' not in st.session_state:
        st.session_state.selected_kelurahan = all_kelurahan[:5] # Default 5 pertama

    col_k1, col_k2, col_k3_spacer = st.columns([1,1,2])
    with col_k1:
        if st.button("Pilih Semua Kelurahan"):
            st.session_state.selected_kelurahan = all_kelurahan
            st.rerun()
    with col_k2:
        if st.button("Hapus Semua Kelurahan"):
            st.session_state.selected_kelurahan = []
            st.rerun()

    selected_kelurahan = st.multiselect(
        "Pilih Kelurahan untuk ditampilkan:", 
        options=all_kelurahan, 
        default=st.session_state.selected_kelurahan,
        key="ms_kelurahan" # Key unik
    )
    st.session_state.selected_kelurahan = selected_kelurahan 
    
    if not selected_kelurahan:
        st.info("Silakan pilih satu atau lebih kelurahan untuk menampilkan grafik.")
        return

    df_region_filtered = df_region[df_region['kelurahan'].isin(selected_kelurahan)]
    
    fig = px.bar(
        df_region_filtered,
        x='kelurahan',
        y='Jumlah',
        color=cluster_col,
        title='Persebaran Cluster per Kelurahan (Data Terfilter)',
        color_discrete_map={
            'Cluster 0': '#1f77b4', 'Cluster 1': '#ff7f0e', 'Cluster 2': '#2ca02c',
            'Cluster 3': '#d62728', 'Cluster 4': '#9467bd', 'Cluster 5': '#8c564b',
            'Cluster 6': '#e377c2', 'Cluster 7': '#7f7f7f', 'Cluster 8': '#bcbd22', 'Cluster 9': '#17becf', 'Cluster 10': '#17becf',
            'Inlier': '#FFC300', # Kuning
            'Outlier': '#900C3F', # Merah Tua
            'Cluster Outlier': '#900C3F' # Merah Tua
        }
    )
    fig.update_layout(barmode='group', xaxis_title='Kelurahan', yaxis_title='Jumlah Sekolah', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


# (MODIFIKASI BESAR) Kembali ke format naratif expander, tapi konten dirapikan + tabel fitur pembeda di DALAM expander
def get_cluster_analysis_narrative(df_results_scaled, df_results_original, features, pretty_names_map, cluster_col='Cluster'):
    """
    (REWORKED AGAIN)
    Menganalisis karakteristik setiap cluster secara naratif menggunakan expander,
    dengan konten yang lebih terstruktur (subjudul, bullet points, tabel fitur pembeda).
    Mengembalikan dictionary berisi detail analisis per cluster (untuk download Excel).
    """
    st.markdown("#### 3. Karakteristik Cluster") # Judul diubah
    st.write("Klik setiap cluster di bawah untuk melihat rangkuman ciri khasnya, termasuk rasio, fasilitas, dan 5 fitur pembeda utamanya dibandingkan rata-rata global.")
    
    analysis_details_dict = {} # Dictionary untuk menyimpan hasil naratif

    # --- 1. Validasi & Persiapan Data ---
    # (Sama seperti sebelumnya...)
    if not isinstance(df_results_scaled, pd.DataFrame):
        st.error("Data hasil (scaled) tidak valid untuk analisis.")
        return analysis_details_dict
    if not isinstance(df_results_original, pd.DataFrame):
        st.error("Data hasil (original) tidak valid untuk analisis.")
        return analysis_details_dict
        
    valid_scaled_features = [f for f in features if f in df_results_scaled.columns]
    if valid_scaled_features:
        global_mean_scaled = df_results_scaled[valid_scaled_features].mean()
    else:
        global_mean_scaled = pd.Series(dtype=float) 

    df_global_original = df_results_original.copy()
    def safe_ratio(numerator, denominator):
        num = pd.to_numeric(numerator, errors='coerce')
        den = pd.to_numeric(denominator, errors='coerce')
        if pd.isna(num) or pd.isna(den) or den == 0: return np.nan
        return num / den
        
    global_student_teacher_ratio = np.nan
    if 'jumlah_siswa' in df_global_original and 'jumlah_guru' in df_global_original:
        ratios = [safe_ratio(s, g) for s, g in zip(df_global_original['jumlah_siswa'], df_global_original['jumlah_guru'])]
        global_student_teacher_ratio = pd.Series(ratios).mean(skipna=True)

    global_student_classroom_ratio = np.nan
    if 'jumlah_siswa' in df_global_original and 'jumlah_ruang_kelas' in df_global_original:
        ratios = [safe_ratio(s, rc) for s, rc in zip(df_global_original['jumlah_siswa'], df_global_original['jumlah_ruang_kelas'])]
        global_student_classroom_ratio = pd.Series(ratios).mean(skipna=True)

    main_facilities = [
        'jumlah_laboratorium_kimia', 'jumlah_laboratorium_bahasa', 
        'jumlah_laboratorium_biologi', 'jumlah_laboratorium_fisika', 
        'jumlah_ruang_laboratorium_ipa', 'jumlah_ruang_laboratorium_komputer',
        'jumlah_ruang_perpustakaan', 'jumlah_ruang_uks', 'jumlah_ruang_tu'
    ]
    global_facility_means = {}
    for fac in main_facilities:
        if fac in df_global_original.columns:
            fac_num_g = pd.to_numeric(df_global_original[fac], errors='coerce').fillna(0)
            global_facility_means[fac] = fac_num_g.mean()

    # --- 2. Iterasi per Cluster & Tampilkan di Expander ---
    sorted_clusters = sorted(df_results_original[cluster_col].unique())
    for cluster_name in sorted_clusters:
        cluster_details = { # Dictionary untuk menyimpan detail sebelum ditampilkan & di-return
            "Rasio & Kepadatan": [],
            "Fasilitas Lengkap": [],
            "Fasilitas Kurang": [],
            "Fitur Pembeda": []
            # "Ciri Khas Lain" tidak perlu disimpan terpisah, sudah terwakili di Fitur Pembeda
        }
        
        # Ambil data cluster
        df_cluster_original = df_results_original[df_results_original[cluster_col] == cluster_name]
        df_cluster_scaled = df_results_scaled[df_results_scaled[cluster_col] == cluster_name]
        if df_cluster_original.empty: continue

        # --- Lakukan Analisis (Sama seperti sebelumnya) ---
        # Rasio Siswa:Guru
        if 'jumlah_siswa' in df_cluster_original and 'jumlah_guru' in df_cluster_original:
            ratios_c = [safe_ratio(s, g) for s, g in zip(df_cluster_original['jumlah_siswa'], df_cluster_original['jumlah_guru'])]
            mean_ratio_c = pd.Series(ratios_c).mean(skipna=True)
            if not pd.isna(mean_ratio_c):
                status = "Ideal"
                if mean_ratio_c > 35: status = "Sangat Tinggi"
                elif mean_ratio_c > 30: status = "Diatas Ideal"
                elif mean_ratio_c < 20: status = "Sangat Rendah"
                cluster_details["Rasio & Kepadatan"].append(f"Rasio Siswa:Guru {status} (rata-rata {mean_ratio_c:.1f}:1)")
        # Kepadatan Kelas
        if 'jumlah_siswa' in df_cluster_original and 'jumlah_ruang_kelas' in df_cluster_original:
            ratios_c = [safe_ratio(s, rc) for s, rc in zip(df_cluster_original['jumlah_siswa'], df_cluster_original['jumlah_ruang_kelas'])]
            mean_ratio_c = pd.Series(ratios_c).mean(skipna=True)
            if not pd.isna(mean_ratio_c):
                status = "Ideal"
                if mean_ratio_c > 50: status = "Sangat Tinggi"
                elif mean_ratio_c > 40: status = "Cukup Tinggi"
                cluster_details["Rasio & Kepadatan"].append(f"Kepadatan Kelas {status} (rata-rata {mean_ratio_c:.1f} siswa/ruang)")
        # Fasilitas
        for fac in main_facilities:
            if fac in df_cluster_original.columns:
                fac_num_c = pd.to_numeric(df_cluster_original[fac], errors='coerce').fillna(0)
                mean_fac_c = fac_num_c.mean()
                global_mean_fac = global_facility_means.get(fac, 0)
                pretty_fac_name = pretty_names_map.get(fac, fac).replace('Jumlah ', '').replace('Ruang ', '')
                if mean_fac_c >= 0.8: cluster_details["Fasilitas Lengkap"].append(pretty_fac_name)
                elif mean_fac_c < 0.1 and global_mean_fac > 0.2: cluster_details["Fasilitas Kurang"].append(pretty_fac_name)
        # Ruang TU Khusus
        if 'jumlah_tendik' in df_cluster_original and 'jumlah_ruang_tu' in df_cluster_original:
            tendik_num_c = pd.to_numeric(df_cluster_original['jumlah_tendik'], errors='coerce').fillna(0)
            ruang_tu_num_c = pd.to_numeric(df_cluster_original['jumlah_ruang_tu'], errors='coerce').fillna(0)
            missing_tu_cluster = df_cluster_original[(tendik_num_c > 0) & (ruang_tu_num_c == 0)].shape[0]
            total_with_tendik_cluster = df_cluster_original[tendik_num_c > 0].shape[0]
            if total_with_tendik_cluster > 0:
                cluster_missing_tu_pct = (missing_tu_cluster / total_with_tendik_cluster) * 100
                # (MODIFIKASI) Perjelas teks
                if cluster_missing_tu_pct > 50: 
                    cluster_details["Fasilitas Kurang"].append(f"Ruang TU (Meskipun punya Tendik, >{cluster_missing_tu_pct:.0f}% sekolah *tidak punya*)")

        # Fitur Pembeda
        if not global_mean_scaled.empty and not df_cluster_scaled.empty:
            cluster_mean_scaled = df_cluster_scaled[valid_scaled_features].mean()
            deviations = cluster_mean_scaled - global_mean_scaled
            sorted_deviations = deviations.abs().sort_values(ascending=False)
            top_5_features = sorted_deviations.head(5).index
            for feature in top_5_features:
                dev_val = deviations[feature]
                pretty_name = pretty_names_map.get(feature, feature)
                status = "Dekat Rata-rata"
                if dev_val > 0.3: status = "Sangat Tinggi"
                elif dev_val > 0.1: status = "Diatas Rata-rata"
                elif dev_val < -0.3: status = "Sangat Rendah"
                elif dev_val < -0.1: status = "Dibawah Rata-rata"
                if status != "Dekat Rata-rata": 
                    cluster_details["Fitur Pembeda"].append({"Fitur": pretty_name, "Status": status})

        # --- Tampilkan di Expander ---
        with st.expander(f"**{cluster_name}**"):
            st.markdown("##### Rasio & Kepadatan")
            if cluster_details["Rasio & Kepadatan"]:
                for item in cluster_details["Rasio & Kepadatan"]: st.markdown(f"- {item}")
            else: st.markdown("- *Tidak ada data rasio signifikan atau fitur tidak dipilih.*")

            st.markdown("##### Fasilitas Utama")
            if cluster_details["Fasilitas Lengkap"]:
                 st.markdown(f"- **Cenderung Lengkap:** {', '.join(cluster_details['Fasilitas Lengkap'])}")
            if cluster_details["Fasilitas Kurang"]:
                 # Set untuk hapus duplikat Ruang TU jika muncul dari analisis umum dan khusus
                 st.markdown(f"- **Cenderung Kurang:** {', '.join(list(set(cluster_details['Fasilitas Kurang'])))}") 
            if not cluster_details["Fasilitas Lengkap"] and not cluster_details["Fasilitas Kurang"]:
                 st.markdown("- *Kelengkapan fasilitas mendekati rata-rata global.*")
                 
            st.markdown("##### Fitur Pembeda Utama (Top 5 vs Rata-rata Global)")
            if cluster_details["Fitur Pembeda"]:
                 df_fitur = pd.DataFrame(cluster_details["Fitur Pembeda"])
                 df_fitur.index = df_fitur.index + 1 # Index 1-based
                 df_fitur.index.name = "Peringkat"
                 # Tampilkan tabel di dalam expander
                 st.dataframe(df_fitur, use_container_width=True) 
            else: st.markdown("- *Tidak ada fitur pembeda signifikan yang dipilih atau ditemukan.*")

        analysis_details_dict[cluster_name] = cluster_details # Simpan detail untuk download & tabel terpisah

    return analysis_details_dict # Kembalikan dictionary

# (DIHAPUS) Fungsi display_feature_importance_table tidak dipakai lagi


def evaluate_clusters(score, metric_type):
    """Memberikan label dan warna evaluasi berdasarkan skor."""
    if metric_type == 'silhouette':
        if score > 0.7: return "Sangat Baik", "normal"
        if score > 0.5: return "Baik", "normal"
        if score > 0.25: return "Sedang", "normal"
        if score > 0: return "Kurang Baik", "inverse"
        return "Buruk", "inverse"
    elif metric_type == 'dbi':
        if score < 0.5: return "Sangat Baik", "inverse"
        if score < 0.75: return "Baik", "inverse"
        if score < 1.0: return "Sedang", "inverse"
        if score < 1.5: return "Kurang Baik", "normal"
        return "Buruk", "normal"

# (MODIFIKASI) Sesuaikan ukuran plot
def plot_silhouette(X, labels):
    """Membuat dan mengembalikan figure Matplotlib untuk plot Silhouette."""
    n_clusters = len(np.unique(labels))
    # Handle jika hanya 1 cluster
    if n_clusters < 2:
        # st.warning("Plot Silhouette tidak dapat dibuat karena hanya ada 1 cluster.") # Pindah ke tempat pemanggilan
        return None 
    
    silhouette_avg = silhouette_score(X, labels)
    sample_silhouette_values = silhouette_samples(X, labels)
    
    plt.style.use('seaborn-v0_8-darkgrid') # (BARU) Ganti style
    fig, ax1 = plt.subplots(1, 1)
    fig.set_size_inches(6, 4) # (MODIFIKASI) Ukuran plot diperkecil
    
    ax1.set_xlim([-0.1, 1.0])
    ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])
    
    y_lower = 10
    
    # Buat colormap
    try:
        colors = cm.nipy_spectral(np.linspace(0, 1, n_clusters))
    except:
        # Fallback jika nipy_spectral tidak ada (jarang terjadi)
        colors = cm.get_cmap("Spectral")(np.linspace(0, 1, n_clusters))

    
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[labels == i]
        ith_cluster_silhouette_values.sort()
        
        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = colors[i]
        ax1.fill_betweenx(
            np.arange(y_lower, y_upper),
            0,
            ith_cluster_silhouette_values,
            facecolor=color,
            edgecolor=color,
            alpha=0.7,
        )
        
        # Label cluster
        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, f"Cluster {i}")
        y_lower = y_upper + 10 # 10 untuk spasi antar cluster

    ax1.set_title("Grafik Plot Silhouette untuk Setiap Cluster")
    ax1.set_xlabel("Nilai Koefisien Silhouette")
    ax1.set_ylabel("Label Cluster")
    
    # Garis merah untuk rata-rata
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")
    ax1.set_yticks([]) # Hapus label Y
    ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
    
    plt.tight_layout()
    return fig

# (MODIFIKASI) Tambah style
def plot_cluster_scatter(X_scaled, labels, cluster_names_map): # Tambah parameter mapping
    """Membuat dan mengembalikan figure Matplotlib untuk scatter plot PCA."""
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    # Handle jika hanya 1 cluster
    if n_clusters < 2:
        # st.warning("Plot Scatter tidak dapat dibuat karena hanya ada 1 cluster.") # Pindah ke tempat pemanggilan
        return None
        
    # Reduksi dimensi dengan PCA
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.style.use('seaborn-v0_8-darkgrid') # (BARU) Ganti style
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(6, 4) # Ukuran plot
    
    # Buat colormap
    try:
        colors = cm.nipy_spectral(np.linspace(0, 1, n_clusters))
    except:
        colors = cm.get_cmap("Spectral")(np.linspace(0, 1, n_clusters))

    for i, numeric_label in enumerate(unique_labels):
        cluster_data = X_pca[labels == numeric_label]
        # Dapatkan nama cluster dari map, fallback ke nama numerik jika tidak ada
        label_name = cluster_names_map.get(numeric_label, f"Label {numeric_label}") 
        ax.scatter(
            cluster_data[:, 0], 
            cluster_data[:, 1], 
            marker='.', 
            s=30, 
            lw=0, 
            alpha=0.7, 
            color=colors[i], 
            label=label_name # Gunakan nama cluster
        )
        
    ax.set_title("Visualisasi Sebaran Cluster (PCA 2D)")
    ax.set_xlabel("Komponen Utama 1")
    ax.set_ylabel("Komponen Utama 2")
    ax.legend(scatterpoints=1, fontsize='small') # Perkecil legend
    # ax.grid(True, linestyle='--', alpha=0.5) # Style sudah ada grid
    
    plt.tight_layout()
    return fig


# (MODIFIKASI) Fungsi ini sekarang mengembalikan Siluet DAN DBI untuk n terbaik
@st.cache_data(show_spinner=False) 
def find_best_cluster(data_scaled, birch_params, max_clusters=11):
    """Mencari n_cluster terbaik menggunakan Silhouette Score (Maks 11)."""
    st.write(f"Mencari jumlah cluster optimal (2 s/d {max_clusters})...")
    best_silhouette = -2 
    best_n = 2
    best_dbi = float('inf') # Inisialisasi DBI terbaik (cari minimum)
    
     # Pastikan data_scaled adalah numpy array
    if isinstance(data_scaled, pd.DataFrame):
        data_scaled_np = data_scaled.values
    else:
        data_scaled_np = data_scaled

    for n in range(2, max_clusters + 1): 
        model = Birch(n_clusters=n, **birch_params)
        labels = model.fit_predict(data_scaled_np)
        
        # Cek jika hanya 1 cluster terbentuk (meski n > 1)
        unique_labels = np.unique(labels)
        if len(unique_labels) < 2:
            continue 
            
        try:
            current_silhouette = silhouette_score(data_scaled_np, labels)
            
            if current_silhouette > best_silhouette:
                best_silhouette = current_silhouette
                best_n = n
                # Hitung DBI hanya untuk n terbaik sementara
                best_dbi = davies_bouldin_score(data_scaled_np, labels)
                
        except ValueError: 
            continue
            
    # (BARU) Kembalikan juga DBI terbaik
    if best_n < 2: # Jika tidak ada n > 1 yang valid
        st.warning("Tidak dapat menemukan jumlah cluster optimal > 1.")
        return 2, -2, float('inf') # Default values

    return best_n, best_silhouette, best_dbi

# --- FUNGSI UTAMA APLIKASI ---

def app():
    st.title("Analisa Clustering Sekolah 📊")
    st.write("Halaman ini akan memandu Anda melalui proses clustering data sekolah.")

    # (BARU) Inisialisasi session state di awal
    if "data_to_process" not in st.session_state:
        st.session_state.data_to_process = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None

    # --- 1. Pilih Sumber Data ---
    st.subheader("Langkah 1: Pilih Sumber Data")
    sumber_data = st.radio(
        "Pilih sumber data untuk dianalisa:",
        ["Gunakan data default (rekomendasi)", "Upload file Excel baru"],
        key="sumber_data_radio",
        horizontal=True,
        on_change=clear_data_state # Hapus state lama jika pilihan berubah
    )

    # (DIHAPUS) Inisialisasi tidak perlu di sini lagi
    # if "data_to_process" not in st.session_state:
    #     st.session_state.data_to_process = None
    #     st.session_state.file_name = None

    if sumber_data == "Gunakan data default (rekomendasi)":
        with st.container(border=True):
            st.markdown("Pilih jenjang sekolah yang ingin Anda proses:")
            jenjang = st.radio("Pilih Jenjang:", ["PAUD", "SD", "SMP", "SMA", "SMK", "SLB", "PKBM"], horizontal=True, key="jenjang_radio")
            if st.button("Muat Data Default"):
                try:
                    file_to_load = FILE_MAP[jenjang]
                    df = pd.read_excel(file_to_load)
                    total_rows = df.shape[0]
                    st.success(f"Berhasil memuat data: **{file_to_load}**")
                    st.write(f"Menampilkan 5 baris pertama dari total **{total_rows}** baris data {jenjang}:")
                    
                    df_head_display = df.head()
                    df_head_display.columns = [col.replace('_', ' ').title() for col in df_head_display.columns]
                    st.dataframe(df_head_display)
                    
                    st.session_state.data_to_process = df
                    st.session_state.file_name = file_to_load 
                    
                except FileNotFoundError: st.error(f"File **{file_to_load}** tidak ditemukan. Pastikan file ada di dalam folder `data/`.")
                except Exception as e: st.error(f"Terjadi kesalahan saat membaca file: {e}")

    # (MODIFIKASI) Logika Upload File dengan Validasi yang Diperketat
    elif sumber_data == "Upload file Excel baru":
        with st.container(border=True):
            st.markdown("Jika Anda memiliki data sendiri, silakan siapkan file Excel Anda.")
            excel_template_bytes = create_template_excel()
            st.download_button(label="📥 Download Template Excel", data=excel_template_bytes, file_name="Template_Data_Sekolah.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.markdown("---")
            uploaded_file = st.file_uploader("Upload file Excel Anda (wajib sesuai template)", type=["xlsx"])
            
            if uploaded_file is not None:
                try:
                    # Baca sheet pertama saja
                    df = pd.read_excel(uploaded_file, sheet_name=0) 
                    st.success(f"File **{uploaded_file.name}** berhasil di-upload!")
                    
                    # --- MULAI VALIDASI ---
                    is_valid = True
                    error_messages = []

                    # 1. Validasi Struktur Kolom
                    if df.columns.tolist() != TEMPLATE_COLUMNS:
                        is_valid = False
                        error_messages.append(f"- **Struktur Kolom Tidak Sesuai:** Nama dan urutan kolom harus sama persis dengan template.")
                        st.write("Kolom di file Anda:", df.columns.tolist())
                        st.write("Kolom yang diharapkan:", TEMPLATE_COLUMNS)

                    # (BARU) 2. Validasi Data Kosong (hanya jika struktur OK)
                    if is_valid and df.empty:
                         is_valid = False
                         error_messages.append(f"- **File Kosong:** File tidak berisi data sekolah (tidak ada baris data).")

                    # 3. Validasi Tipe Data (hanya jika struktur OK dan tidak kosong)
                    if is_valid:
                        # Cek Kolom String
                        for col in STRING_COLS:
                            if col not in df.columns: continue # Seharusnya sudah dicek di struktur
                            # Cek apakah ada nilai non-null yang BUKAN string
                            # Menggunakan .apply() lebih aman untuk tipe campuran
                            # Mengabaikan NaN saat pengecekan tipe
                            # pd.isna(x) handles various forms of missing values like None, np.nan
                            if not df[col].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                                is_valid = False
                                error_messages.append(f"- **Tipe Data Salah:** Kolom '{col}' harus berisi teks (string). Ditemukan tipe data lain.")
                                # break # Bisa di-break jika mau satu error per tipe

                        # Cek Kolom Integer
                        if is_valid: # Lanjut jika belum ada error
                            for col in INTEGER_COLS:
                                if col not in df.columns: continue # Seharusnya sudah dicek di struktur
                                # Coba konversi ke numerik, error = 'coerce' akan jadi NaN
                                numeric_col = pd.to_numeric(df[col], errors='coerce')
                                
                                # Cek jika ada NaN SETELAH konversi DAN nilai asli TIDAK NaN
                                if numeric_col.isnull().any() and df[col].notnull().any():
                                     is_valid = False
                                     error_messages.append(f"- **Tipe Data Salah:** Kolom '{col}' harus berisi angka bulat (integer). Ditemukan nilai non-numerik.")
                                     # break 
                                else:
                                    # Cek apakah ada nilai float dengan desimal (setelah konversi)
                                    # Gunakan modulo % 1 != 0 untuk cek desimal, abaikan NaN
                                    if (numeric_col.notna() & (numeric_col % 1 != 0)).any():
                                        is_valid = False
                                        error_messages.append(f"- **Tipe Data Salah:** Kolom '{col}' harus berisi angka bulat (integer), ditemukan angka desimal (float).")
                                        # break
                    # --- AKHIR VALIDASI ---

                    if is_valid:
                        total_rows = df.shape[0]
                        st.write(f"Menampilkan 5 baris pertama dari total **{total_rows}** baris data yang Anda upload:")
                        df_head_display = df.head()
                        df_head_display.columns = [col.replace('_', ' ').title() for col in df_head_display.columns]
                        st.dataframe(df_head_display)
                        
                        st.session_state.data_to_process = df
                        st.session_state.file_name = uploaded_file.name
                    else:
                        # (MODIFIKASI) Pesan error diperbaiki
                        st.error("Validasi Gagal! Data Anda salah dan gagal diproses karena tidak sesuai format template. Alasan:")
                        for msg in error_messages:
                            st.markdown(msg)
                        # Hapus data dari state jika tidak valid
                        # (Pastikan atribut ada sebelum dihapus)
                        if "data_to_process" in st.session_state:
                            del st.session_state['data_to_process']
                        if "file_name" in st.session_state:
                            del st.session_state['file_name']
                        # Set ke None agar bagian bawah tidak jalan
                        st.session_state.data_to_process = None
                        st.session_state.file_name = None


                except Exception as e: 
                    st.error(f"Terjadi kesalahan saat membaca atau memvalidasi file Excel Anda: {e}")
                     # Hapus data dari state jika error
                    if "data_to_process" in st.session_state:
                        del st.session_state['data_to_process']
                    if "file_name" in st.session_state:
                        del st.session_state['file_name']
                    # Set ke None
                    st.session_state.data_to_process = None
                    st.session_state.file_name = None


    st.divider()

    # --- Langkah 2 & 3: Konfigurasi & Pemilihan Fitur ---
    # (MODIFIKASI) Pengecekan dipindahkan ke sini setelah inisialisasi di awal
    if st.session_state.data_to_process is not None:
        
        st.subheader("Langkah 2: Konfigurasi Metode Analisis")
        
        # (DIPERBARUI) Nama Metode
        method = st.radio("Pilih metode analisis:", ["BIRCH", "Isolation Forest", "Isolation Forest + BIRCH"], horizontal=True, key="metode_radio")
        
        if "Isolation Forest" in method:
            st.info("ℹ️ **Isolation Forest** adalah metode untuk mendeteksi anomali (outlier). "
                    "Metode ini akan mencari data yang 'berbeda' dari yang lain, contoh: sekolah dengan **jumlah siswa yang sangat tinggi** atau **jumlah ruang kelas yang sangat sedikit**.")

        st.markdown("---")
        
        params = {}
        with st.container(border=True):
            if method == "BIRCH":
                st.subheader("Parameter Algoritma BIRCH")
                
                # (DIPERBARUI) Defaultnya False
                auto_cluster = st.checkbox("Tentukan jumlah cluster secara otomatis (Maks 11)", key="auto_cluster", value=False, help="Jika dicentang, sistem akan mencari jumlah cluster terbaik (2-11) secara otomatis.")
                
                col1, col2, col3 = st.columns(3)
                with col1: 
                    # (DIPERBARUI) Default 5, disabled by default
                    params['n_clusters'] = st.number_input("Target Jumlah Cluster (n_clusters)", min_value=2, max_value=11, value=5, help="Jumlah cluster akhir yang ingin dibentuk.", disabled=st.session_state.auto_cluster)
                with col2: 
                    # (MODIFIKASI) Threshold min 0.001, step 0.001, format %.3f
                    params['threshold'] = st.number_input(
                        "Nilai Threshold (threshold)", 
                        min_value=0.001, # Batas bawah diubah
                        max_value=1.0, 
                        value=0.3, 
                        step=0.001, 
                        format="%.3f", # Format disesuaikan
                        help="Radius sub-cluster. Turunkan jika cluster terlalu sedikit/besar, naikkan jika terlalu banyak."
                    )
                with col3: 
                    params['branching_factor'] = st.number_input("Branching Factor (branching_factor)", min_value=20, max_value=100, value=50, help="Jumlah maksimum sub-cluster di setiap node CF tree.")
                
                # (BARU) Penjelasan Parameter BIRCH
                st.caption("""
                    **Penjelasan Parameter BIRCH:**
                    - **Target Jumlah Cluster (n_clusters):** Jumlah kelompok akhir yang diinginkan. Abaikan jika opsi otomatis dicentang.
                    - **Nilai Threshold (threshold):** Radius maksimum sub-cluster awal. **Semakin kecil nilainya, cenderung semakin banyak cluster detail yang terbentuk.** Coba turunkan (misal 0.1 atau 0.05) jika hasil cluster terlalu besar/tidak seimbang. Untuk data > 500 baris, nilai antara 0.1 - 0.001 mungkin lebih baik. Untuk data < 500, coba 0.3 - 0.1.
                    - **Branching Factor (branching_factor):** Jumlah maksimum cabang/anak di setiap node pohon CF internal. Nilai default (50) biasanya cukup baik.
                """)

            elif method == "Isolation Forest":
                st.subheader("Parameter Algoritma Isolation Forest")
                col1, col2 = st.columns(2)
                with col1: params['contamination'] = st.number_input("Perkiraan Kontaminasi (contamination)", min_value=0.01, max_value=0.3, value=0.05, step=0.01, format="%.2f", help="Perkiraan persentase data anomali (outlier) dalam dataset.")
                with col2: params['n_estimators'] = st.number_input("Jumlah Estimator (n_estimators)", min_value=10, max_value=300, value=100, help="Jumlah pohon acak (base estimator) yang akan dibangun.")
                
                # (BARU) Penjelasan Parameter Isolation Forest
                st.caption("""
                    **Penjelasan Parameter Isolation Forest:**
                    - **Perkiraan Kontaminasi (contamination):** Perkiraan proporsi outlier dalam data (misal, 0.05 = 5%). Algoritma akan menggunakan nilai ini untuk menentukan batas antara inlier dan outlier.
                    - **Jumlah Estimator (n_estimators):** Jumlah pohon yang dibangun. Semakin banyak biasanya lebih stabil, tapi lebih lama. Nilai default (100) seringkali cukup.
                """)

            elif method == "Isolation Forest + BIRCH":
                st.subheader("Parameter Gabungan")
                st.markdown("##### 1. Parameter Isolation Forest (Preprocessing Anomali)")
                col1_if, col2_if = st.columns(2)
                with col1_if: params['contamination'] = st.number_input("Perkiraan Kontaminasi (contamination)", min_value=0.01, max_value=0.3, value=0.05, step=0.01, format="%.2f", key="if_contam_gabung", help="Perkiraan persentase data anomali (outlier).")
                with col2_if: params['n_estimators'] = st.number_input("Jumlah Estimator (n_estimators)", min_value=10, max_value=300, value=100, key="if_est_gabung", help="Jumlah pohon acak (base estimator).")
                st.caption("""
                    **Penjelasan Isolation Forest:** Tahap ini memisahkan data normal (Inlier) dari data anomali (Outlier) terlebih dahulu.
                """)
                
                st.markdown("---")
                st.markdown("##### 2. Parameter BIRCH (Clustering untuk Inlier)")
                
                # (DIPERBARUI) Defaultnya False
                auto_cluster_gabungan = st.checkbox("Tentukan jumlah cluster secara otomatis (Maks 11)", key="auto_cluster_gabungan", value=False, help="Jika dicentang, sistem akan mencari jumlah cluster terbaik (2-11) secara otomatis untuk data Inlier.")
                
                col1_birch, col2_birch, col3_birch = st.columns(3)
                with col1_birch: 
                    params['n_clusters'] = st.number_input("Target Jumlah Cluster (n_clusters)", min_value=2, max_value=11, value=5, key="birch_n_gabung", help="Jumlah cluster akhir untuk data Inlier.", disabled=st.session_state.auto_cluster_gabungan)
                    if st.session_state.auto_cluster_gabungan:
                        params['n_clusters'] = None 
                with col2_birch: 
                    # (MODIFIKASI) Threshold min 0.001, step 0.001, format %.3f
                    params['threshold'] = st.number_input(
                        "Nilai Threshold (threshold)", 
                        min_value=0.001, 
                        max_value=1.0, 
                        value=0.3, 
                        step=0.001, 
                        format="%.3f", 
                        key="birch_thresh_gabung", 
                        help="Radius sub-cluster untuk data Inlier."
                    )
                with col3_birch: params['branching_factor'] = st.number_input("Branching Factor (branching_factor)", min_value=20, max_value=100, value=50, key="birch_branch_gabung", help="Jumlah maksimum sub-cluster.")
                st.caption("""
                    **Penjelasan BIRCH:** Tahap ini mengelompokkan data Inlier (yang dianggap normal) menjadi beberapa cluster. Data Outlier akan dimasukkan ke 'Cluster Outlier' terpisah. Lihat penjelasan parameter BIRCH di atas.
                """)


        st.subheader("Langkah 3: Pilih Fitur untuk Analisis")
        st.write("Pilih kolom numerik yang akan digunakan untuk proses analisis.")
        df_loaded = st.session_state.data_to_process
        numeric_columns = df_loaded.select_dtypes(include=['number']).columns.tolist()
        pretty_map = {col: col.replace('_', ' ').title() for col in numeric_columns}
        reverse_pretty_map = {v: k for k, v in pretty_map.items()}
        pretty_options = list(pretty_map.values())

        # (BARU) Tombol Pilih/Hapus Semua Fitur
        if 'selected_pretty_features' not in st.session_state:
            st.session_state.selected_pretty_features = pretty_options # Default semua
        
        col_f1, col_f2, col_f3_spacer = st.columns([1,1,2])
        with col_f1:
            if st.button("Pilih Semua Fitur"):
                st.session_state.selected_pretty_features = pretty_options
                st.rerun() 
        with col_f2:
            if st.button("Hapus Semua Fitur"):
                st.session_state.selected_pretty_features = []
                st.rerun() 
        
        selected_pretty_features = st.multiselect(
            "Fitur yang akan dianalisis:", 
            options=pretty_options, 
            default=st.session_state.selected_pretty_features
        )
        st.session_state.selected_pretty_features = selected_pretty_features # Simpan pilihan
        
        st.markdown("") # Spasi
        
        # --- Tombol Jalankan Proses ---
        if st.button("Jalankan Proses Analisis", type="primary", use_container_width=True):
            # (MODIFIKASI) Izinkan proses berjalan meski tidak ada fitur dipilih
            # Fitur rasio akan tetap berjalan
            # if not selected_pretty_features:
            #     st.warning("Harap pilih minimal satu fitur untuk dianalisis.")
            # else:
            
            if "analysis_results" in st.session_state:
                del st.session_state.analysis_results
            
            # (MODIFIKASI) Handle jika tidak ada fitur dipilih
            if selected_pretty_features:
                selected_original_features = [reverse_pretty_map[p_name] for p_name in selected_pretty_features]
            else:
                st.warning("Tidak ada fitur yang dipilih untuk analisis perbandingan. Hanya analisis rasio & fasilitas yang akan berjalan.")
                selected_original_features = [] # List kosong
            
            st.session_state.analysis_params = params
            st.session_state.selected_features = selected_original_features
            st.session_state.selected_method = method
            
            # (MODIFIKASI) Pastikan pretty_names_map berisi SEMUA kolom numerik
            # untuk fungsi analisis rasio, meskipun tidak dipilih
            st.session_state.pretty_names_map = {col: name for col, name in pretty_map.items()}

            # Catat waktu mulai
            start_time = time.time()
            
            with st.spinner("Melakukan prapemrosesan dan analisis model... Ini mungkin perlu beberapa saat."):
                df_full = st.session_state.data_to_process.copy()
                
                # (MODIFIKASI) Pra-pemrosesan hanya pada fitur yang dipilih
                # Handle jika selected_original_features kosong
                if selected_original_features:
                    df_processed, df_scaled = preprocess_data(df_full, selected_original_features)
                else:
                    # Buat DataFrame kosong jika tidak ada fitur
                    df_processed = pd.DataFrame(index=df_full.index)
                    df_scaled = pd.DataFrame(index=df_full.index)

                
                # (MODIFIKASI) df_results_final_download sekarang berisi SEMUA kolom asli
                # Ini penting untuk fungsi analisis rasio yang baru
                df_results_final_download = df_full.copy()

                analysis_results = {'type': method}
                
                # --- Logika Clustering ---
                
                # (MODIFIKASI) Cek jika ada data untuk di-cluster
                if df_scaled.empty and method != 'Isolation Forest': # Isolation forest bisa jalan tanpa fitur (?)
                    st.error("Proses clustering tidak dapat dijalankan karena tidak ada fitur numerik yang dipilih.")
                    # Buat kolom 'Cluster' default
                    df_results_final_download['Cluster'] = "Cluster 0"
                    analysis_results['labels'] = np.zeros(len(df_full))
                    analysis_results['data_scaled'] = df_scaled
                    analysis_results['cluster_names_map'] = {0: "Cluster 0"} # Tambah map default
                
                elif method == "BIRCH":
                    birch_params = {'threshold': params['threshold'], 'branching_factor': params['branching_factor']}
                    final_n_clusters = params['n_clusters']
                    
                    if final_n_clusters is None: 
                        with st.spinner("Mencari jumlah cluster optimal (2-11)..."):
                            # (MODIFIKASI) Tangkap 3 nilai
                            best_n, best_sil, best_dbi = find_best_cluster(df_scaled, birch_params, max_clusters=11)
                            final_n_clusters = best_n
                            # Simpan hasil terbaik untuk ditampilkan
                            analysis_results['auto_cluster_result'] = {
                                'n': best_n,
                                'silhouette': best_sil,
                                'dbi': best_dbi
                            }
                    
                    model = Birch(n_clusters=final_n_clusters, **birch_params)
                    labels = model.fit_predict(df_scaled)
                    
                    # (BARU) Mapping label numerik ke nama string
                    analysis_results['cluster_names_map'] = {i: f"Cluster {i}" for i in np.unique(labels)}
                    
                    df_results_final_download['Cluster'] = [analysis_results['cluster_names_map'][l] for l in labels]
                    analysis_results['labels'] = labels # Simpan label numerik
                    analysis_results['data_scaled'] = df_scaled

                elif method == "Isolation Forest":
                    # Perlu handle jika df_scaled kosong
                    if df_scaled.empty:
                        st.error("Isolation Forest memerlukan setidaknya satu fitur numerik.")
                        df_results_final_download['Cluster'] = "N/A"
                        analysis_results['labels'] = np.array([])
                        analysis_results['data_scaled'] = df_scaled
                        analysis_results['cluster_names_map'] = {} # Map kosong
                    else:
                        model = IsolationForest(n_estimators=params['n_estimators'], contamination=params['contamination'], random_state=42)
                        labels = model.fit_predict(df_scaled) # Hasilnya -1 (Outlier) dan 1 (Inlier)
                        
                        # (BARU) Mapping label numerik ke nama string
                        analysis_results['cluster_names_map'] = {1: "Inlier", -1: "Outlier"}

                        df_results_final_download['Cluster'] = ["Inlier" if l == 1 else "Outlier" for l in labels]
                        analysis_results['labels'] = labels # Simpan label numerik (-1, 1)
                        analysis_results['data_scaled'] = df_scaled
                
                elif method == "Isolation Forest + BIRCH":
                     if df_scaled.empty:
                        st.error("Metode ini memerlukan setidaknya satu fitur numerik.")
                        df_results_final_download['Cluster'] = "N/A"
                        analysis_results['labels'] = np.array([])
                        analysis_results['data_scaled'] = df_scaled
                        analysis_results['cluster_names_map'] = {} # Map kosong
                     else:
                        if_model = IsolationForest(n_estimators=params['n_estimators'], contamination=params['contamination'], random_state=42)
                        if_labels = if_model.fit_predict(df_scaled) 
                        inlier_mask = (if_labels == 1)
                        outlier_mask = (if_labels == -1)
                        df_scaled_inliers = df_scaled.loc[inlier_mask] # Gunakan .loc dengan boolean mask
                        
                        birch_params = {'threshold': params['threshold'], 'branching_factor': params['branching_factor']}
                        final_n_clusters_birch = params['n_clusters']

                        if final_n_clusters_birch is None: 
                             with st.spinner("Mencari jumlah cluster optimal untuk Inlier (2-11)..."):
                                # (MODIFIKASI) Tangkap 3 nilai
                                best_n, best_sil, best_dbi = find_best_cluster(df_scaled_inliers, birch_params, max_clusters=11)
                                final_n_clusters_birch = best_n
                                # Simpan hasil terbaik untuk ditampilkan
                                analysis_results['auto_cluster_result'] = {
                                    'n': best_n,
                                    'silhouette': best_sil,
                                    'dbi': best_dbi
                                }
                        
                        labels_final_numeric = np.zeros(len(df_scaled), dtype=int) # Array untuk label numerik akhir
                        cluster_names_map = {} # Mapping untuk plot

                        if df_scaled_inliers.shape[0] > 0:
                            birch_model = Birch(n_clusters=final_n_clusters_birch, **birch_params)
                            # Pastikan input ke fit_predict adalah numpy array jika pakai find_best_cluster
                            birch_labels = birch_model.fit_predict(df_scaled_inliers.values if isinstance(df_scaled_inliers, pd.DataFrame) else df_scaled_inliers) 
                            
                            # Set label numerik untuk inlier (0, 1, 2, ...)
                            labels_final_numeric[inlier_mask] = birch_labels 
                            
                            # Buat mapping nama untuk inlier
                            for i in np.unique(birch_labels):
                                cluster_names_map[i] = f"Cluster {i}"

                            n_inlier_clusters = len(np.unique(birch_labels))
                            outlier_label_numeric = n_inlier_clusters # Label numerik untuk outlier
                        else:
                            birch_labels = np.array([]) 
                            n_inlier_clusters = 0
                            outlier_label_numeric = 0 # Outlier jadi label 0 jika tidak ada inlier
                            st.warning("Tidak ditemukan data Inlier setelah proses Isolation Forest.")
                        
                        # Set label numerik untuk outlier
                        labels_final_numeric[outlier_mask] = outlier_label_numeric
                        cluster_names_map[outlier_label_numeric] = "Cluster Outlier" # Mapping nama outlier
                        
                        # Buat kolom 'Cluster' string berdasarkan mapping
                        final_labels_string = pd.Series([cluster_names_map[l] for l in labels_final_numeric], index=df_processed.index)
                        df_results_final_download['Cluster'] = final_labels_string
                        
                        analysis_results['labels'] = labels_final_numeric # Simpan label numerik gabungan
                        analysis_results['data_scaled'] = df_scaled # Untuk evaluasi pakai semua data
                        analysis_results['cluster_names_map'] = cluster_names_map # Simpan mapping

                # --- Akhir Logika Clustering ---

                # (MODIFIKASI) df_results_display sekarang berisi SEMUA data
                # kolom non-fitur + kolom fitur yang di-scale
                df_results_display = pd.concat([
                    df_full.drop(columns=selected_original_features, errors='ignore'), 
                    df_scaled # Fitur terpilih yang sudah di-scale (sebagai DataFrame)
                ], axis=1)
                # Tambah pengecekan jika kolom 'Cluster' sudah ada
                if 'Cluster' in df_results_final_download.columns:
                    df_results_display['Cluster'] = df_results_final_download['Cluster'] 
                else: # Jika clustering gagal total
                    df_results_display['Cluster'] = "N/A"
                
                end_time = time.time()
                analysis_results['duration'] = end_time - start_time
                
                analysis_results['df_results_display'] = df_results_display 
                analysis_results['df_results_download'] = df_results_final_download 
                
                st.session_state.analysis_results = analysis_results
                st.rerun()

        # --- (DIPERBARUI) LANGKAH 4 & 5: TAMPILKAN HASIL ANALISIS ---
        if "analysis_results" in st.session_state:
            results = st.session_state.analysis_results
            df_results_display = results['df_results_display'] # Untuk grafik (fitur scaled)
            df_results_download = results['df_results_download'] # Untuk download (fitur original)
            features = st.session_state.selected_features # Fitur yg dipilih (nama asli)
            pretty_names_map = st.session_state.pretty_names_map # Peta semua fitur
            
            # (MODIFIKASI) Filter pretty_names_map HANYA untuk fitur yg dipilih,
            # khusus untuk plot box-plot 
            pretty_names_map_selected = {k: v for k, v in pretty_names_map.items() if k in features}
            
            
            st.divider()
            st.header("Hasil Analisis")
            
            # (BARU) Tampilkan waktu proses & info MinMax
            if features: # Hanya tampilkan jika ada fitur
                st.info("Prapemrosesan (**MinMax Scaler**) telah diterapkan pada fitur yang dipilih.")
            st.success(f"Analisis selesai dalam **{results['duration']:.2f} detik**.")
            
            # (MODIFIKASI) Pesan auto cluster dipindah ke Evaluasi

            # --- LANGKAH 4: HASIL ANALISIS ---
            st.subheader("Langkah 4: Hasil Analisis")
            
            # 1. Ringkasan Hasil
            st.markdown("#### 1. Ringkasan Hasil")
            cluster_counts = df_results_display['Cluster'].value_counts().sort_index()
            st.dataframe(cluster_counts.rename("Jumlah Sekolah"))
            
            # 2. Perbandingan Fitur (Box Plot)
            # (MODIFIKASI) Panggil plot_individual_box_plots di sini
            if features:
                # Panggil dengan df_results_download (nilai asli)
                plot_individual_box_plots(df_results_download, features, pretty_names_map_selected, cluster_col='Cluster')
            else:
                 st.markdown("#### 2. Perbandingan Fitur Antar Cluster (Nilai Asli)")
                 st.info("Tidak ada fitur yang dipilih untuk ditampilkan di box plot.")

            # (DIHAPUS) Bagian Peran Fitur F-Value dihapus
            
            # 3. (MODIFIKASI) Karakteristik Cluster (Naratif Expander)
            # Memanggil fungsi naratif
            analysis_details_dict = get_cluster_analysis_narrative( # Nama fungsi diubah
                df_results_display,   # Data dengan fitur scaled
                df_results_download,  # Data dengan fitur original (untuk rasio)
                features,             # Fitur yg dipilih
                pretty_names_map,     # Peta SEMUA fitur (untuk rasio & nama)
                cluster_col='Cluster'
            )
            
            # (DIHAPUS) Tabel perbandingan fitur global dihapus
            # display_feature_importance_table(analysis_details_dict)

            # (MODIFIKASI) Download Karakteristik (Sekarang setelah expander)
            st.markdown("##### Download Detail Karakteristik")
            try:
                # Kirim dictionary hasil analisis ke fungsi konversi Excel
                excel_bytes_karakteristik = convert_analysis_to_excel(analysis_details_dict)
                st.download_button(
                     label="📥 Download Tabel Karakteristik Cluster & Fitur Pembeda (Excel)",
                     data=excel_bytes_karakteristik,
                     file_name=f"karakteristik_cluster_{st.session_state.file_name.split('/')[-1]}_{results['type']}.xlsx",
                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     key="download_karakteristik"
                )
            except Exception as e:
                st.error(f"Gagal mempersiapkan file Excel Karakteristik: {e}")

            st.markdown("---") # Pemisah sebelum anggota cluster

            # 4. (MODIFIKASI) Anggota Cluster (sebelumnya no 5)
            st.markdown("#### 4. Anggota Cluster")
            st.write("Daftar sekolah di setiap cluster.")
            
            # (MODIFIKASI) Tombol Download sekarang memanggil fungsi yang dimodifikasi
            # Pindahkan ke dalam blok try-except
            try:
                excel_bytes_anggota = convert_clusters_to_excel(
                        df_results_download, # Data asli (untuk tabel)
                        df_results_display,  # Data scaled (untuk plot)
                        features,            # Fitur yg dipilih (untuk plot)
                        pretty_names_map_selected, # Peta fitur yg dipilih (untuk plot)
                        cluster_col='Cluster'
                    )
                st.download_button(
                    label="📥 Download Daftar Anggota per Cluster (Excel, per Sheet + Plot)",
                    data=excel_bytes_anggota, 
                    file_name=f"anggota_cluster_{st.session_state.file_name.split('/')[-1]}_{results['type']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_anggota" # Tambah key unik
                )
            except Exception as e:
                st.error(f"Gagal mempersiapkan file Excel Anggota: {e}")

            cluster_names = cluster_counts.index.tolist()
            num_clusters = len(cluster_names)
            
            # (DIPERBARUI) Tentukan jumlah kolom
            if results['type'] == 'Isolation Forest':
                num_cols = 2
            else:
                num_cols = 3
                
            if num_clusters > 0:
                cols = st.columns(num_cols) 
                
                for i, cluster_name in enumerate(cluster_names):
                    with cols[i % num_cols]: 
                        st.markdown(f"**{cluster_name}** ({cluster_counts[cluster_name]} sekolah)")
                        
                        # Ambil nama sekolah, kecamatan, kelurahan dari df_results_download
                        cluster_members = df_results_download[df_results_download['Cluster'] == cluster_name][['nama_sekolah', 'kecamatan', 'kelurahan']]
                        
                        cluster_df = pd.DataFrame({'Nama Sekolah': cluster_members['nama_sekolah']})
                        cluster_df.reset_index(drop=True, inplace=True)
                        cluster_df.index = cluster_df.index + 1 # Buat nomor 1-based
                        cluster_df.index.name = "No"
                        
                        st.dataframe(cluster_df, use_container_width=True, height=300)
            
            # --- LANGKAH 5: EVALUASI & PERSEBARAN ---
            st.divider()
            st.subheader("Langkah 5: Evaluasi Model & Persebaran")

            # 1. Evaluasi Kualitas Cluster
            st.markdown("#### 1. Evaluasi Kualitas Cluster")
            
            # (BARU) Tampilkan hasil pencarian otomatis jika ada
            if 'auto_cluster_result' in results:
                auto_res = results['auto_cluster_result']
                st.info(f"⚙️ **Hasil Pencarian Otomatis:** Ditemukan **{auto_res['n']} cluster** sebagai yang terbaik dengan: \n"
                        f"- Skor Silhouette: **{auto_res['silhouette']:.3f}** \n"
                        f"- Skor DBI: **{auto_res['dbi']:.3f}**")
                st.markdown("---") # Pemisah tambahan

            # (DIPERBARUI) Hitung untuk SEMUA metode
            data_scaled_for_eval = results['data_scaled']
            labels_for_eval = results['labels'] # Ini label NUMERIK
            
            if results['type'] == 'Isolation Forest' and features:
                st.warning("**Catatan:** Metrik ini (Silhouette, DBI) umumnya tidak digunakan untuk evaluasi Isolation Forest. "
                         "Sesuai permintaan, skor ini tetap ditampilkan untuk menunjukkan seberapa 'terpisah' secara matematis grup Inlier (data normal) dari grup Outlier (anomali).")
            
            # Cek jika ada cukup data dan cluster untuk evaluasi
            unique_labels_eval = np.unique(labels_for_eval)
            if len(unique_labels_eval) > 1 and not data_scaled_for_eval.empty :
                try:
                    # Pastikan input adalah numpy array
                    if isinstance(data_scaled_for_eval, pd.DataFrame):
                        data_scaled_np_eval = data_scaled_for_eval.values
                    else:
                         data_scaled_np_eval = data_scaled_for_eval

                    silhouette_avg = silhouette_score(data_scaled_np_eval, labels_for_eval)
                    dbi_score = davies_bouldin_score(data_scaled_np_eval, labels_for_eval)
                    
                    sil_label, sil_color = evaluate_clusters(silhouette_avg, 'silhouette')
                    dbi_label, dbi_color = evaluate_clusters(dbi_score, 'dbi')
                    
                    col_metrik1, col_metrik2 = st.columns(2)
                    with col_metrik1:
                        st.metric(
                            label="Silhouette Score (Semakin tinggi semakin baik)",
                            value=f"{silhouette_avg:.3f}",
                            delta=sil_label,
                            delta_color=sil_color
                        )
                    with col_metrik2:
                        st.metric(
                            label="Davies-Bouldin Index (DBI) (Semakin rendah semakin baik)",
                            value=f"{dbi_score:.3f}",
                            delta=dbi_label,
                            delta_color=dbi_color
                        )
                    
                    # (MODIFIKASI) Tampilkan Plot Silhouette & Scatter BERDAMPINGAN
                    # if results['type'] != 'Isolation Forest' and len(np.unique(labels_for_eval)) > 1: # Cek > 1 cluster
                    # Perbaikan: Cek jumlah unique label > 1 sudah dilakukan di atas
                    if len(unique_labels_eval) > 1:
                        
                        st.markdown("---") # Pemisah
                        
                        col_plot1, col_plot2 = st.columns(2) # Buat kolom

                        with col_plot1:
                            # Plot Silhouette
                            st.markdown("##### Grafik Plot Silhouette")
                            st.caption("Menunjukkan kualitas pengelompokan per cluster. Idealnya semua bilah > garis merah.")
                            try: # Tambah try-except
                                fig_sil = plot_silhouette(data_scaled_np_eval, labels_for_eval)
                                if fig_sil: # Cek jika figure berhasil dibuat
                                     st.pyplot(fig_sil, use_container_width=True)
                                else:
                                     st.warning("Plot Silhouette tidak dapat dibuat (kemungkinan hanya 1 cluster).")
                            except Exception as e_sil:
                                st.warning(f"Gagal membuat plot Silhouette: {e_sil}")

                        with col_plot2:
                            # Plot Scatter PCA
                            st.markdown("##### Grafik Sebaran Cluster (PCA)")
                            st.caption("Visualisasi 2D sebaran cluster (pakai PCA). Titik=sekolah, Warna=cluster.")
                            try: # Tambah try-except
                                # (BARU) Ambil mapping nama cluster dari results
                                cluster_map = results.get('cluster_names_map', {}) 
                                fig_scatter = plot_cluster_scatter(data_scaled_np_eval, labels_for_eval, cluster_map)
                                if fig_scatter: # Cek jika figure berhasil dibuat
                                     st.pyplot(fig_scatter, use_container_width=True)
                                else:
                                     st.warning("Plot Scatter tidak dapat dibuat (kemungkinan hanya 1 cluster).")
                            except Exception as e_scatter:
                                st.warning(f"Gagal membuat plot Scatter PCA: {e_scatter}")

                except ValueError as e:
                     st.warning(f"Tidak dapat menghitung metrik evaluasi: {e}")
                except Exception as e: # Tangkap error lain
                     st.error(f"Terjadi error saat evaluasi: {e}")
            else:
                st.warning("Tidak dapat menghitung metrik evaluasi (kemungkinan hanya 1 cluster atau tidak ada fitur dipilih).")

            # 2. Persebaran per Kecamatan (MODIFIKASI)
            # Judul diubah jadi '2.' di dalam fungsi
            plot_region_distribution_filtered(df_results_display, cluster_col='Cluster')
            
            # 3. (BARU) Persebaran per Kelurahan
            plot_region_distribution_filtered_kelurahan(df_results_display, cluster_col='Cluster')

