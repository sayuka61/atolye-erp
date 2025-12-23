import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP - V6", layout="wide")

# --- FONKSİYONLAR ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        temiz = str(deger).replace(',', '.').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

# --- ARAYÜZ ---
st.title("🏭 3D Atölye Üretim & Maliyet (V6)")

# Session State (Hafıza)
if 'secilen_urun_kodu' not in st.session_state:
    st.session_state.secilen_urun_kodu = None
if 'bom_listesi' not in st.session_state:
    st.session_state.bom_listesi = []

# --- YAN MENÜ: DOSYALAR ---
with st.sidebar:
    st.header("📂 Veri Deposu")
    dosya_sarf = st.file_uploader("1. SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("2. ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

    # Depo Verisini Oku
    df_hir = None
    if dosya_sarf:
        try:
            # Hırdavat Sayfası (2. Sayfa)
            raw_hir = pd.read_excel(dosya_sarf, sheet_name=1, header=1)
            raw_hir = raw_hir.iloc[:, :8]
            raw_hir.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET_FIYATI', 'TEDARIKCI', 'TARIH']
            
            # Hesaplamalar
            raw_hir = raw_hir.dropna(subset=['PAKET_FIYATI'])
            raw_hir['PAKET_FIYATI'] = raw_hir['PAKET_FIYATI'].apply(temizle_para)
            raw_hir['ALINAN'] = raw_hir['ALINAN'].apply(temizle_para)
            raw_hir['BIRIM_MALIYET'] = raw_hir['PAKET_FIYATI'] / raw_hir['ALINAN']
            
            # Seçim Listesi (İsim + Açıklama)
            raw_hir
