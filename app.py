import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V14 - Final", layout="wide")

# --- PARA TEMİZLEME ---
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

# --- SOL MENÜ ---
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            # Genelde 2. sayfa Hırdavat olur (index=1)
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            # 2. satır başlık (header=1)
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            if len(raw.columns) >= 6:
                raw = raw.iloc[:, :8]
                raw.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TEDARIKCI', 'TARIH']
                
                # Temizlik
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                raw = raw[raw['ALINAN'] > 0]
                
                # Birim Maliyeti hesapla (Ama kullanıcıya gösterme)
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                
                df_depo = raw
                st.success(f"✅ Depo Hazır ({len(df_depo)} Parça)")
            else:
                st.error("Sütun sayısı eksik.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# --- ANA EKRAN ---
if dosya_sarf and dosya_urun and df_depo is not None:
    
    st.subheader("2. Reçete Hazırla (Fiyatlar Gizli)")
    
    try:
        xl_ur = pd.ExcelFile(dosya_urun)
        sayfa_ur = st.selectbox("Kategori", xl_ur.sheet_names)
        df_ur = pd.read_excel(dosya_urun, sheet_name=sayfa_ur)
        
        if len(df_ur.columns) >= 2:
            col_kod = df_ur.columns[0]
            col_ad = df_ur.columns[1]
            liste = df_ur[col_kod].astype(str) + " | " + df_ur[col_ad].astype(str)
            secilen = st.selectbox("Ürün Seçiniz", liste)
            
            st.markdown("---")
            
            c1, c2 = st.columns([1, 1])
            
            # SOL: MALZEME EKLEME
            with c1:
                st.info("👇 Buradan Malzeme Ekle")
                t1, t2, t3 = st.tabs(["📦 Depodan", "✏️ Elle Yaz", "🎨 Renk"])
                
                # 1. DEPO (FİYATSIZ)
                with t1:
                    parca = st.selectbox("Parça Seç", df_depo['ISIM'].unique())
                    adet = st.number_input("Adet", min_value=1, value=1)
                    if st.button("Ekle ➕
