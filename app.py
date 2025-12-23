import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP - V7", layout="wide")

# --- YARDIMCI FONKSİYONLAR ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        # Virgül varsa noktaya çevir, TL simgesi varsa sil
        temiz = str(deger).replace(',', '.').replace('TL', '').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

# --- SAYFA BAŞLIĞI ---
st.title("🏭 3D Atölye Üretim & Maliyet (V7)")

# --- HAFIZA (SESSION STATE) ---
if 'secilen_urun_kodu' not in st.session_state:
    st.session_state.secilen_urun_kodu = None
if 'bom_listesi' not in st.session_state:
    st.session_state.bom_listesi = []

# --- YAN MENÜ: DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📂 Dosyalar")
    st.info("Lütfen iki dosyayı da yükle.")
    dosya_sarf = st.file_uploader("1. SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("2. ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

    #
