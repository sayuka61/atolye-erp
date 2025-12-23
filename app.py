import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP - V9", layout="wide")

# --- PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        temiz = str(deger).replace(',', '.').replace('TL', '').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V9 - Final)")

# --- HAFIZA ---
if 'bom_listesi' not in st.session_state:
    st.session_state.bom_listesi = []

# --- SOL MENÜ ---
with st.sidebar:
    st.header("1️⃣ Dosya Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

    st.markdown("---")
    st.header("2️⃣ Ayarlar")
    
    # SARF MALZEME OKUMA
    df_hir = None
    if dosya_sarf:
        try:
            xl_sarf = pd.ExcelFile(dosya
