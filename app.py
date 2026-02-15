import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import date
import re

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Perangkat KBC Presisi - MIN 1 CIAMIS", layout="wide", page_icon="🏫")

# --- ENGINE AI (DIPERBAIKI AGAR TIDAK EROR 404) ---
@st.cache_resource
def get_model():
    if "GOOGLE_API_KEY" not in st.secrets: return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Menggunakan versi stabil terbaru
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model_ai = get_model()

# --- DATABASE SEMENTARA ---
if 'db_rpp' not in st.session_state: st.session_state.db_rpp = []
if 'config' not in st.session_state:
    st.session_state.config = {
        "madrasah": "MIN 1 CIAMIS", "guru": "", "nip_guru": "",
        "kepala": "Iim Siti Halimah, S.Ag., M.Pd.",
        "nip_kepala": "197206051997032003", "thn_ajar": "2025/2026"
    }

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>E-Perangkat KBC</h2>", unsafe_allow_html=True)
    menu = st.radio("Menu Utama", ["➕ Buat RPP Baru", "📜 Riwayat RPP", "⚙️ Pengaturan"])

# --- MENU 2: BUAT RPP BARU ---
if menu == "➕ Buat RPP Baru":
    st.subheader("➕ Rancang RPP KBC Presisi")
    
    with st.form("form_rpp_utama"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: mapel = st.text_input("Mata Pelajaran")
        with c2: kls_sel = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"], index=3)
        with c3: sem_sel = st.selectbox("Semester", ["1 (Ganjil)", "2 (Genap)"])
        with c4: materi = st.text_input("Materi Pokok")
        
        target_belajar = st.text_area("Tujuan Pembelajaran (TP)", height=100)
        instruksi_khusus = st.text_input("💡 Instruksi Tambahan AI (Misal: Tambahkan Ice Breaking)")
        
        # Checkbox Topik KBC
        st.write("<b>Pilih Topik KBC (Panca Cinta):</b>", unsafe_allow_html=True)
        list_kbc = ["Cinta kepada Allah/Rasul-Nya", "Cinta Ilmu", "Cinta Diri dan Sesama", "Cinta Lingkungan", "Cinta Tanah Air"]
        cols_k = st.columns(2)
        topik_sel = [k for i, k in enumerate(list_kbc) if cols_k[i % 2].checkbox(k, key=f"k_{k}")]
        
        submit_button = st.form_submit_button("🚀 GENERATE RPP SESUAI REFERENSI")

    if submit_button:
        if not mapel or not materi:
            st.warning("Mohon lengkapi Mata Pelajaran dan Materi.")
        else:
            with st.spinner("⏳ AI sedang menyusun RPP lengkap..."):
                try:
                    # PROMPT UTUH (DATA TETAP LENGKAP)
                    prompt = f"""
                    Berperanlah sebagai Guru MI Profesional. 
                    TUGAS: Buat RPP Kurikulum Merdeka KBC Presisi untuk MAPEL {mapel}.
                    Materi: {materi}, Kelas: {kls_sel}, Semester: {sem_sel}.
                    
                    DATA INPUT:
                    - Madrasah: {st.session_state.config['madrasah']}
                    - Tujuan: {target_belajar}
                    - Nilai KBC: {', '.join(topik_sel)}
                    - Instruksi Khusus: {instruksi_khusus}

                    WAJIB: Tampilkan Identitas, KBC, Desain Pembelajaran, Deep Learning (LOK-R), Asesmen, dan Lampiran LKPD/Soal.
                    HANYA BERIKAN KODE HTML.
                    """

                    # PENGATURAN AGAR HASIL TIDAK TERPOTONG (max_output_tokens)
                    raw_response = model_ai.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=8192,
                            temperature=0.7
                        )
                    ).text
                    
                    html_final = re.sub(r'```html|```', '', raw_response).strip()
                    st.session_state.db_rpp.append({"tgl": date.today(), "materi": materi, "file": html_final})
                    st.success("Selesai!")
                    components.html(f"<div style='background:white; color:black; padding:20px;'>{html_final}</div>", height=800, scrolling=True)
                    st.download_button("📥 Download Document", html_final, file_name=f"RPP_{mapel}.doc")
                except Exception as e:
                    st.error(f"Gagal generate: {e}")

elif menu == "⚙️ Pengaturan":
    st.subheader("⚙️ Data Master")
    st.session_state.config['madrasah'] = st.text_input("Madrasah", st.session_state.config['madrasah'])
    st.session_state.config['guru'] = st.text_input("Nama Guru", st.session_state.config['guru'])
