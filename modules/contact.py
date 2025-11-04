import streamlit as st
import base64
from pathlib import Path

# --- FUNGSI BANTUAN ---
def img_to_base64(image_path):
    """Mengubah file gambar menjadi string base64 untuk ditanamkan di HTML."""
    try:
        img_bytes = Path(image_path).read_bytes()
        img_b64 = base64.b64encode(img_bytes).decode()
        # Menggunakan format 'jpeg' karena file aslinya adalah .jpg
        return f"data:image/jpeg;base64,{img_b64}"
    except FileNotFoundError:
        st.error(f"File gambar tidak ditemukan di: {image_path}. Pastikan 'profile_pic.jpg' ada di folder yang sama.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat gambar: {e}")
        return None

def app():
    # --- CSS Kustom ---
    st.markdown("""
        <style>
        section[data-testid="stAppViewContainer"] > div:first-child {
            max-width: 800px;
            margin: auto;
            padding: 2rem 1rem;
        }
        .contact-title {
            text-align: center;
            font-size: 34px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.8rem;
        }
        .contact-subtitle {
            text-align: center;
            color: #333;
            font-size: 16px;
            margin-bottom: 2rem;
        }
        
        /* --- [PERBAIKAN] CSS UNTUK KARTU PROFIL --- */
        .profile-container {
            display: flex;
            flex-direction: column;
            align-items: center; /* Memusatkan semua konten */
            margin-bottom: 2.5rem;
            padding: 2.5rem; /* Padding lebih besar agar rapi */
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        .profile-container:hover {
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        }
        .profile-pic {
            width: 150px;       /* Ukuran gambar tetap */
            height: 150px;      /* Ukuran gambar tetap */
            border-radius: 50%; /* Membuat gambar lingkaran */
            object-fit: cover;  /* Memastikan gambar mengisi lingkaran */
            border: 5px solid #16A34A; /* Border hijau */
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .profile-name {
            font-size: 28px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        .profile-detail {
            font-size: 16px;
            color: #333;
            margin-bottom: 0.3rem;
            text-align: center;
        }
        .profile-detail strong {
            color: #1E3A8A;
        }
        /* ------------------------------------------- */

        .contact-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            text-align: center;
            height: 100%; /* Memastikan tinggi kartu sama */
        }
        .contact-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        }
        .contact-icon {
            font-size: 50px;
            color: #16A34A;
            margin-bottom: 0.5rem;
        }
        .contact-label {
            font-weight: 600;
            font-size: 17px;
            color: #1E3A8A;
            margin-bottom: 5px;
        }
        .contact-info {
            font-size: 15px;
            color: #333;
            margin-bottom: 15px;
            word-wrap: break-word; /* Agar email tidak overflow */
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Judul Halaman ---
    st.markdown('<div class="contact-title">Kontak Kami 📞</div>', unsafe_allow_html=True)
    st.markdown('<div class="contact-subtitle">Anda dapat menghubungi pengembang proyek EduCluster melalui informasi di bawah ini.</div>', unsafe_allow_html=True)

    # --- [PERBAIKAN] Bagian Profil (Foto dan Informasi Pribadi) ---
    
    # Ganti "profile_pic.jpg" dengan path/nama file foto Anda
    # Pastikan file foto ada di folder yang sama dengan script .py Anda
    image_path = "profile_pic.jpg" 
    img_b64_string = img_to_base64(image_path)

    # Hanya tampilkan jika gambar berhasil dimuat
    if img_b64_string:
        st.markdown(f"""
            <div class="profile-container">
                <img src="{img_b64_string}" class="profile-pic" alt="Foto Profil Devanska">
            </div>
        """, unsafe_allow_html=True)

    # --- Kartu Kontak (Nomor Telepon & Email) ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="contact-card">
            <div class="profile-name">Devanska Uzieltama Mardanus</div>
                <div class="profile-detail"><strong>NIM:</strong> 535220089</div>
                <div class="profile-detail"><strong>Universitas:</strong> Universitas Tarumanegara</div>
                <div class="profile-detail"><strong>Fakultas:</strong> Teknik Informatika</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="contact-card">
                <div class="contact-label">Nomor Telephone</div>
                <div class="contact-info">0812-2450-6237</div>
                <div class="contact-label">Email</div>
                <div class="contact-info">devanska.535220089@stu.untar.ac.id</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Tambahan Info / Pesan ---
    st.markdown("""
        <div style='text-align:center;'>
            <p style='color:#444; font-size:15px;'>
                Kami siap membantu Anda dalam memahami hasil analisis, pengelompokan sekolah, 
                serta pemanfaatan sistem EduCluster untuk penelitian dan pengambilan keputusan.
            </p>
            <p style='color:#1E3A8A; font-weight:600;'>Terima kasih telah menggunakan EduCluster! 🌱</p>
        </div>
    """, unsafe_allow_html=True)