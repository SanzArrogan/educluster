import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from streamlit.components.v1 import html

# --- Fungsi Membuat / Membaca Buku Manual ---
@st.cache_data
def get_manual_pdf_bytes():
    # (DIUBAH) Nama file sekarang 'Buku Manual.pdf'
    file_name = "Buku Manual.pdf" 
    try:
        with open(file_name, "rb") as pdf_file:
            pdf_bytes_real = pdf_file.read()
        print(f"Menggunakan file {file_name} asli.")
        return pdf_bytes_real, file_name
    except FileNotFoundError:
        print(f"File {file_name} tidak ditemukan, membuat dummy PDF.")
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Buku Manual EduCluster (Dummy)")
        p.drawString(100, 730, "File buku manual asli tidak ditemukan.")
        # (DIUBAH) Pesan error di dummy PDF juga diperbarui
        p.drawString(100, 710, "Letakkan file 'Buku Manual.pdf' di folder utama.") 
        p.save()
        buffer.seek(0)
        return buffer.getvalue(), "Buku_Manual_Dummy.pdf"


# --- Aplikasi Utama ---
def app():
    # --- CSS Umum (INI BAGIAN PENTING YANG HILANG) ---
    st.markdown("""
        <style>
        /* Mengatur lebar halaman utama */
        section[data-testid="stAppViewContainer"] > div:first-child {
            max-width: 950px;
            margin: auto;
            padding: 1rem 1rem;
        }
        .home-title {
            text-align: center;
            font-size: 38px;
            font-weight: 700;
            color: #2E3A59;
            line-height: 1.3;
            margin-bottom: 0.5rem;
        }
        .home-icon {
            font-size: 50px;
            text-align: center;
            display: block;
            margin-bottom: 5px;
        }

        /* INI UNTUK MEMBUAT SUBTITLE KE TENGAH */
        .home-subtitle {
            text-align: center;
            font-size: 17px;
            color: #333;
            max-width: 900px;
            margin: 0 auto 15px auto; 
            line-height: 1.6;
            display: block;
            position: relative;
            left: 100px;
        }
        
        /* INI UNTUK MEMBUAT TOMBOL DOWNLOAD KE TENGAH */
        .manual-download-home {
            text-align: center !important;
            display: flex;
            justify-content: center;
            margin-top: 10px;
            position: relative;
            left: 150px;
        }
        /* Ini untuk styling tombolnya jadi hijau */
        .manual-download-home div[data-testid="stDownloadButton"] button {
            background-color: #16A34A !important; color: white !important;
            border: none !important; padding: 0.6rem 1.2rem !important;
            font-size: 15px !important; font-weight: 500 !important;
            border-radius: 5px !important;
            transition: background-color 0.3s ease !important;
        }
        .manual-download-home div[data-testid="stDownloadButton"] button:hover {
            background-color: #15803D !important;
        }
        
        /* INI UNTUK KARTU FITUR AGAR SAMA TINGGI */
        .feature-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            text-align: center;
            height: 100%; /* Kunci agar tingginya sama */
            display: flex;
            flex-direction: column;
            justify-content: flex-start; /* Konten rata atas */
            margin-bottom: 1rem; 
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }
        .feature-icon-big {
            font-size: 45px;
            margin-bottom: 0.5rem;
        }
        .feature-title {
            font-size: 20px;
            font-weight: 600;
            color: #1E3A8A;
            margin-bottom: 0.5rem;
        }
        .feature-desc {
            font-size: 15px;
            color: #333;
            line-height: 1.5;
        }
        .fitur-sistem-title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Judul Utama ---
    st.markdown("""
        <span class="home-icon">🏫</span>
        <h1 class="home-title">
            Pengelompokan Sekolah di DKI Jakarta <br>
            Berdasarkan Kondisi Pendidikan <br>
            Menggunakan Metode BIRCH
        </h1>
    """, unsafe_allow_html=True)

    # --- Download Buku Manual ---
    st.warning("Silahkan download buku manual untuk mempermudah mengakses web", icon="💡")
    pdf_content, pdf_filename = get_manual_pdf_bytes()

    # Ini adalah div wrapper untuk tombol download
    st.markdown('<div class="manual-download-home">', unsafe_allow_html=True)
    st.download_button(
        label="📖 Download Buku Manual (.pdf)",
        data=pdf_content,
        file_name=pdf_filename,
        mime="application/pdf"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Deskripsi Utama ---
    # Ini adalah paragraf subtitle
    st.markdown("""
        <p class="home-subtitle">
            "Sistem analisis pengelompokan sekolah menggunakan algoritma <b>BIRCH</b> (Balanced Iterative Reducing and Clustering using Hierarchies) 
            untuk mengidentifikasi pola dan karakteristik kondisi pendidikan di Jakarta. 
            Penelitian ini bertujuan membantu pengambilan keputusan dalam peningkatan kualitas pendidikan secara optimal."
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # --- Bagian Metode Analisis ---
    st.subheader("Metode Analisis yang Digunakan")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">👥</div>
                <div class="feature-title">Analisis Sekolah</div>
                <div class="feature-desc">
                    Clustering berbasis data pendidikan untuk memahami pola sekolah-sekolah di DKI Jakarta.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">🌳</div>
                <div class="feature-title">Metode BIRCH</div>
                <div class="feature-desc">
                    Algoritma clustering hierarkis efisien untuk data besar dan kompleks.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">🌲</div>
                <div class="feature-title">Isolation Forest</div>
                <div class="feature-desc">
                    Algoritma deteksi anomali untuk mengidentifikasi data outlier secara otomatis.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Fitur Sistem EduCluster ---
    st.markdown('<h2 class="fitur-sistem-title">Fitur Sistem EduCluster</h2>', unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📂</div>
                <div class="feature-title">Upload Dataset</div>
                <div class="feature-desc">
                    Unggah file <b>CSV</b> atau <b>Excel</b> berisi templet data sekolah untuk dianalisis secara otomatis oleh sistem.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">🌳</div>
                <div class="feature-title">BIRCH Clustering</div>
                <div class="feature-desc">
                    Analisis pengelompokan sekolah menggunakan algoritma <b>BIRCH</b> dengan pengaturan parameter yang fleksibel.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📈</div>
                <div class="feature-title">Visualisasi Hasil</div>
                <div class="feature-desc">
                    Tampilkan hasil analisis dalam bentuk <b>grafik</b>, <b>tabel</b>, dan <b>peta interaktif</b> untuk interpretasi yang mudah.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- Jenis Sekolah (Pengganti Carousel) ---
    st.divider()
    st.markdown('<h2 class="fitur-sistem-title">Jenis dan Tingkatan Sekolah di DKI Jakarta</h2>', unsafe_allow_html=True)
    
    # Baris 1: PAUD, SD, SMP
    colS1, colS2, colS3 = st.columns(3)
    with colS1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">🏫</div>
                <div class="feature-title">PAUD</div>
                <div class="feature-desc">
                    Pendidikan Anak Usia Dini (PAUD) menekankan pembentukan karakter, kemandirian, dan keterampilan dasar anak.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with colS2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📘</div>
                <div class="feature-title">SD</div>
                <div class="feature-desc">
                    Sekolah Dasar (SD) fokus pada literasi, numerasi, dan pembentukan nilai-nilai dasar untuk anak usia 7–12 tahun.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with colS3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📗</div>
                <div class="feature-title">SMP</div>
                <div class="feature-desc">
                    Sekolah Menengah Pertama (SMP) merupakan lanjutan SD dengan fokus pada pendalaman ilmu pengetahuan.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Baris 2: SMA, SMK, PKBM
    colS4, colS5, colS6 = st.columns(3)
    with colS4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📙</div>
                <div class="feature-title">SMA</div>
                <div class="feature-desc">
                    Sekolah Menengah Atas (SMA) berorientasi pada akademik, mempersiapkan siswa menuju pendidikan tinggi.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with colS5:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">⚙️</div>
                <div class="feature-title">SMK</div>
                <div class="feature-desc">
                    Sekolah Menengah Kejuruan (SMK) berfokus pada keahlian praktis untuk menyiapkan siswa masuk dunia industri.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with colS6:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">📖</div>
                <div class="feature-title">PKBM</div>
                <div class="feature-desc">
                    Pusat Kegiatan Belajar Masyarakat (PKBM) adalah lembaga nonformal yang menyediakan program kesetaraan.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Baris 3: SLB (Dibuat di kolom tengah agar rapi)
    colS7, colS8, colS9 = st.columns(3)
    with colS8: # Menempatkan di kolom tengah
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-big">💙</div>
                <div class="feature-title">SLB</div>
                <div class="feature-desc">
                    Sekolah Luar Biasa (SLB) melayani anak-anak berkebutuhan khusus dengan pembelajaran inklusif dan adaptif.
                </div>
            </div>
        """, unsafe_allow_html=True)
