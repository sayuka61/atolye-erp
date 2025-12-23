import streamlit as st
import pandas as pd

# Sayfa Genişliği
st.set_page_config(page_title="3D Atölye ERP Pro", layout="wide")

# --- YARDIMCI FONKSİYONLAR ---
def temizle_para(deger):
    """Excel'den gelen '1,15' gibi metinleri sayıya (1.15) çevirir"""
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        # Virgülü noktaya çevir, boşlukları sil
        temiz = str(deger).replace(',', '.').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

# --- ARAYÜZ BAŞLIYOR ---
st.title("🏭 3D Atölye ERP Sistemi (V4)")
st.markdown("---")

# YAN MENÜ (DOSYA YÜKLEME)
with st.sidebar:
    st.header("📂 Dosya Yükleme Alanı")
    st.info("Sistemin çalışması için iki Excel dosyanı da yükle.")
    
    dosya_sarf = st.file_uploader("1. SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("2. ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

# ANA EKRAN SEKME YAPISI
tab1, tab2, tab3 = st.tabs(["📋 Ürün Kataloğu & Maliyetler", "📦 Depo Stokları", "📊 Özet Durum"])

# --- TAB 1: ÜRÜN LİSTESİ VE MALİYETLER ---
with tab1:
    if dosya_urun:
        try:
            xl = pd.ExcelFile(dosya_urun)
            secilen_sayfa = st.selectbox("Kategoriler (Sayfalar)", xl.sheet_names)
            
            # Sayfayı oku
            df_urun = pd.read_excel(dosya_urun, sheet_name=secilen_sayfa)
            
            # Eğer 'SWİTCHLİ' veya 'LAMBA' gibi detaylı sayfaysa hesaplama yap
            # Senin dediğin sütun yapısı genelde 8+ sütunlu dosyalarda var
            if len(df_urun.columns) >= 8:
                # Sütun isimlerini standartlaştıralım (İndeks ile alıyoruz ki isim değişse de çalışsın)
                # 0:Kod, 1:Ad, 2:FilamentMaliyet, 3:Süre, 4:Sarf1, 5:Fiyat1, 6:Sarf2, 7:Fiyat2
                
                # Pandas'ta indeks 0'dan
