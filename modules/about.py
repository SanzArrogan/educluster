import streamlit as st

def app():
    # --- CSS Tampilan Elegan ---
    st.markdown("""
        <style>
        section[data-testid="stAppViewContainer"] > div:first-child {
            max-width: 900px;
            margin: auto;
            padding: 2rem 1rem;
        }
        .about-title {
            text-align: center;
            font-size: 34px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .about-subtitle {
            text-align: center;
            color: #333;
            font-size: 17px;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .section-title {
            color: #1E3A8A;
            font-size: 22px;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .content-text {
            color: #333;
            font-size: 15px;
            line-height: 1.7;
            text-align: justify;
        }
        
        /* --- CSS BARU UNTUK ALUR PROSES --- */
        .flow-container {
            display: flex;
            flex-wrap: wrap; /* Agar responsif di layar kecil */
            justify-content: center;
            align-items: center;
            margin-top: 1.5rem;
            gap: 10px;
        }
        .flow-step {
            background: #F0F9FF; /* Biru muda */
            border: 1px solid #BEE3F8;
            border-radius: 10px;
            padding: 0.75rem 1.25rem;
            text-align: center;
            font-weight: 600;
            color: #1E3A8A;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .flow-step.choices {
            background: #FFFBEB; /* Kuning muda */
            border-color: #FDE68A;
        }
        .flow-step.choices ul {
            list-style-type: none;
            padding-left: 0;
            margin-top: 0.5rem;
            margin-bottom: 0;
            font-size: 13px;
            font-weight: 500;
            color: #333;
            line-height: 1.5;
        }
        .flow-arrow {
            font-size: 24px;
            color: #1E3A8A;
            font-weight: 700;
            margin: 0 0.25rem;
        }
        /* ----------------------------------- */

        .tech-card {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            text-align: center;
        }
        .tech-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }
        .tech-icon {
            font-size: 35px;
            color: #16A34A;
            margin-bottom: 0.5rem;
        }
        .tech-label {
            font-weight: 600;
            color: #1E3A8A;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Judul & Deskripsi ---
    st.markdown('<div class="about-title">Tentang Proyek Ini ℹ️</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="about-subtitle">
            <b>EduCluster</b> adalah aplikasi analisis berbasis web yang dikembangkan untuk mengelompokkan sekolah-sekolah di DKI Jakarta berdasarkan kondisi pendidikan menggunakan algoritma <b>BIRCH</b> dan <b>Isolation Forest</b>.
            Sistem ini dirancang untuk menganalisis pola pendidikan dan mendeteksi ketimpangan fasilitas, 
            <b>dengan tujuan utama mendukung terciptanya pemerataan kualitas sekolah</b> di wilayah DKI Jakarta.
        </div>
    """, unsafe_allow_html=True)

    # --- Latar Belakang ---
    st.markdown('<div class="section-title">🎯 Latar Belakang</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="content-text">
            Pendidikan merupakan faktor penting dalam pembangunan manusia. Namun, setiap sekolah di DKI Jakarta memiliki kondisi yang berbeda-beda, baik dari segi jumlah siswa, guru, tenaga kependidikan, maupun sarana prasarana seperti laboratorium dan ruang belajar.
            Perbedaan ini menimbulkan kebutuhan akan analisis data yang mampu mengelompokkan sekolah berdasarkan kesamaan karakteristiknya agar kebijakan pendidikan dapat diarahkan secara lebih tepat sasaran.
        </div>
    """, unsafe_allow_html=True)

    # --- Tujuan Penelitian ---
    st.markdown('<div class="section-title">🎓 Tujuan Proyek</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="content-text">
            Proyek ini bertujuan untuk:
            <ul>
                <li>Mengelompokkan sekolah berdasarkan kondisi sumber daya manusia dan fasilitas pendidikan menggunakan algoritma <b>BIRCH</b>.</li>
                <li>Mendeteksi data anomali atau sekolah dengan kondisi tidak wajar menggunakan <b>Isolation Forest</b>.</li>
                <li>Menyediakan tampilan visual interaktif untuk memudahkan interpretasi hasil analisis.</li>
                <li>Mendukung proses pengambilan keputusan dalam peningkatan kualitas pendidikan di DKI Jakarta.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # --- [BARU] Alur Proses Analisis ---
    st.markdown('<div class="section-title">⚙️ Alur Proses Analisis</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="flow-container">
            <div class="flow-step">1. Masukkan Data</div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">2. Preprocessing</div>
            <div class="flow-arrow">→</div>
            <div class="flow-step choices">
                <b>3. Pilih Metode</b>
                <ul>
                    <li>BIRCH</li>
                    <li>Isolation Forest</li>
                    <li>BIRCH + IF</li>
                </ul>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">4. Proses Model</div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">5. Visualisasi Hasil</div>
        </div>
    """, unsafe_allow_html=True)


    # --- Teknologi yang Digunakan ---
    st.markdown('<div class="section-title">🧠 Teknologi yang Digunakan</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="tech-card">
                <div class="tech-icon">🐍</div>
                <div class="tech-label">Python</div>
                <p style='font-size:14px; color:#333;'>Digunakan untuk pengolahan data dan penerapan algoritma BIRCH & Isolation Forest.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="tech-card">
                <div class="tech-icon">📊</div>
                <div class="tech-label">Streamlit</div>
                <p style='font-size:14px; color:#333;'>Membangun antarmuka web interaktif untuk analisis dan visualisasi hasil clustering.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="tech-card">
                <div class="tech-icon">🗂️</div>
                <div class="tech-label">Pandas & Scikit-Learn</div>
                <p style='font-size:14px; color:#333;'>Mengelola data, melakukan preprocessing, dan menjalankan model machine learning.</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Penutup ---
    st.markdown("""
        <div style='text-align:center;'>
            <p style='font-size:15px; color:#444;'>
                EduCluster dikembangkan sebagai bagian dari penelitian akademik untuk mendukung pemerataan pendidikan di Indonesia.
            </p>
            <p style='font-weight:600; color:#1E3A8A;'>
                "Data bukan hanya angka, tapi arah menuju kebijakan yang lebih baik." 📘
            </p>
        </div>
    """, unsafe_allow_html=True)