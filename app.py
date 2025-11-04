import streamlit as st
from modules import home, clustering, about, contact

# --- Konfigurasi Awal ---
st.set_page_config(
    page_title="EduCluster - Jakarta School Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Sidebar Premium ---
# SAYA SUDAH MENGUBAH SATU BARIS DI SINI
st.markdown("""
    <style>
        /* Sidebar background */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
            color: white;
            padding-top: 2rem;
        }

        /* Judul sidebar */
        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .sidebar-subtitle {
            font-size: 13px;
            color: #D1D5DB;
        }

        /* Footer */
        footer {
            position: absolute;
            top: 10px;
            width: 100%;
            text-align: center;
            color: #C7D2FE;
            font-size: 13px;
        }

        /* Tombol custom 
         MODIFIKASI KECIL: Menghapus '>' (child combinator) 
         agar selector tetap berfungsi (div > form > button)
        */
        div[data-testid="stButton"] button {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            border: none !important;
            border-left: 4px solid transparent !important;
            text-align: left !important;
            padding: 0.8rem 1rem !important;
            border-radius: 1px !important;
            width: 100% !important;
            transition: all 0.3s ease-in-out !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            cursor: pointer; /* Pastikan cursor adalah pointer */
        }

        /* Hover effect */
        div[data-testid="stButton"] button:hover {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            transform: translateX(3px);
        }

        /* Active button 
         Class ini diterapkan pada DIV pembungkus (data-testid="stButton")
         Jadi kita perlu targetkan 'button' di dalamnya
        */
        .active-btn button {
            background-color: #3B82F6 !important;
            border-left: 4px solid #93C5FD !important;
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- State halaman aktif (BARU) ---
# Prioritaskan state dari URL (hasil klik tombol custom)
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]
# Jika tidak ada di URL, cek session state
elif "page" not in st.session_state:
    # Jika tidak ada di session state (pertama kali buka), set default
    st.session_state.page = "Home"


# --- Logo & Judul Sidebar ---
st.sidebar.markdown("""
    <div class="sidebar-title">
        📘 EduCluster
    </div>
    <div class="sidebar-subtitle">
        Analisa Sekolah di Jakarta
    </div>
    <hr style="border: 0.5px solid #3B82F6; margin-top: 10px; margin-bottom: 20px;">
""", unsafe_allow_html=True)

# --- Tombol Navigasi Sidebar (BARU) ---
nav_items = ["Home", "Clustering", "About", "Contact"]

for key in nav_items:
    # Tambahkan class CSS 'active-btn' jika halaman ini sedang aktif
    active_class = "active-btn" if st.session_state.page == key else ""

    # Kita gunakan st.markdown dan HTML/form-hack untuk membuat tombol custom
    # Ini memungkinkan kita menambahkan 'active_class'
    btn_html = f"""
        <div data-testid="stButton" class="{active_class}">
            <form action="#" method="get" style="width: 100%;">
                <button type="submit" name="page" value="{key}" style="width: 100%;">
                    {key}
                </button>
            </form>
        </div>
    """
    st.sidebar.markdown(btn_html, unsafe_allow_html=True)

# --- Tampilkan Halaman Sesuai State ---
if st.session_state.page == "Home":
    home.app()
elif st.session_state.page == "Clustering":
    clustering.app()
elif st.session_state.page == "About":
    about.app()
elif st.session_state.page == "Contact":
    contact.app()

# --- Footer Sidebar ---
st.sidebar.markdown("<footer>BIRCH Clustering Analysis</footer>", unsafe_allow_html=True)