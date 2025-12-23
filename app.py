import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V14", layout="wide")

# --- YARDIMCI: PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V14 - Dinamik Mod)")

# --- HAFIZA ---
if 'bom_v14' not in st.session_state:
    st.session_state.bom_v14 = []

# --- SOL MENÜ: DOSYALAR ---
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    # DEPO VERİSİNİ OKU (Hata korumalı)
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            # Genelde 2. sayfa Hırdavat olur, index=1
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            # Başlık genelde 2. satırdadır (header=1)
