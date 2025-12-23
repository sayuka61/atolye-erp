import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V16", layout="wide")

def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V16 - Final)")

if 'bom' not in st.session_state:
    st.session_state.bom = []

with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            if len(raw.columns) >= 6:
                raw = raw.iloc[:, :8]
                raw.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TED', 'TARIH']
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                raw = raw[raw['ALINAN'] > 0]
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                df_depo = raw
                st.success(f"✅ Depo Hazır! ({len(df_depo)} Parça)")
            else:
                st.error("Sütun eksik.")
        except Exception as e:
            st.error(f"Hata: {e}")

if dosya_sarf and dosya_urun and df_depo is not None:
    st.subheader("2. Reçete Hazırla (Fiyatlar Gizli)")
    try:
        xl_ur = pd.ExcelFile(dosya_urun)
        sayfa_ur = st.selectbox("Kategori", xl_ur.sheet_names)
        df_ur = pd.read_excel(dosya_urun, sheet_name=sayfa_ur)
        
        if len(df_ur.columns) >= 2:
            kod_col = df_ur.columns[0]
            ad_col = df_ur.columns[1]
            liste = df_ur[kod_col].astype(str) + " | "
