import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V13 - Dinamik", layout="wide")

# --- PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').replace(' ', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V13 - Dinamik Mod)")

# --- HAFIZA ---
if 'bom_v13' not in st.session_state:
    st.session_state.bom_v13 = []

# --- SOL MENÜ ---
with st.sidebar:
    st.header("1. Güncel Dosyalar")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    # DEPOYU OKU
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            # KOPYALAMA HATASINI ENGELLEMEK İÇİN KISA TUTTUM:
