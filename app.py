import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP - V8 (Garanti Mod)", layout="wide")

# --- TEMİZLİK FONKSİYONU ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        temiz = str(deger).replace(',', '.').replace('TL', '').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V8 - Kontrol Sende)")

# --- HAFIZA ---
if 'bom_listesi' not in st.session_state:
    st.session_state.bom_listesi = []

# --- 1. SOL MENÜ: DOSYALAR ---
with st.sidebar:
    st.header("1️⃣ Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

    st.markdown("---")
    st.header("2️⃣ Sayfa Ayarları")
    
    # SARF MALZEME SAYFA SEÇİMİ
    df_hir = None
    if dosya_sarf:
        try:
            xl_sarf = pd.ExcelFile(dosya_sarf)
            st.write("📂 **Sarf Malzeme Dosyası Okundu!**")
            
            # Kullanıcıya Soralım
            sayfa_hir = st.selectbox("Hırdavat (Civata/Somun) Hangi Sayfada?", xl_sarf.sheet_names, index=1)
            baslik_satiri = st.number_input("Başlık Kaçıncı Satırda? (Genelde 2)", min_value=1, value=2) - 1
            
            # Seçilen sayfayı oku
            raw_hir = pd.read_excel(dosya_sarf, sheet_name=sayfa_hir, header=baslik_satiri)
            
            # Sütunları Kontrol Et
            st.caption(f"Bulunan Sütunlar: {list(raw_hir.columns[:3])}...")
            
            # Veriyi Hazırla (İlk 8 sütun varsayımıyla)
            if len(raw_hir.columns) >= 8:
                raw_hir = raw_hir.iloc[:, :8]
                raw_hir.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET_FIYATI', 'TEDARIKCI', 'TARIH']
                
                # Temizlik
                raw_hir = raw_hir.dropna(subset=['PAKET_FIYATI'])
                raw_hir['PAKET_FIYATI'] = raw_hir['PAKET_FIYATI'].apply(temizle_para)
                raw_hir['ALINAN'] = raw_hir['ALINAN'].apply(temizle_para)
                raw_hir = raw_hir[raw_hir['ALINAN'] > 0]
                raw_hir['BIRIM_MALIYET'] = raw_hir['PAKET_FIYATI'] / raw_hir['ALINAN']
                raw_hir['FULL_ISIM'] = raw_hir['URUN'].astype(str) + " (" + raw_hir['ACIKLAMA'].astype(str) + ")"
                
                df_hir = raw_hir
                st.success(f"✅ Hırdavatlar Hazır! ({len(df_hir)} Parça)")
            else:
                st.error("⚠️ Seçilen sayfada yeterli sütun yok. Yanlış sayfa seçmiş olabilir misin?")
                
        except Exception as e:
            st.error(f"Hata: {e}")
    else:
        st.info("Sarf Malzeme dosyası bekleniyor...")

# --- ANA EKRAN ---

if dosya_sarf and dosya_urun and df_hir is not None:
    
    st.subheader("3️⃣ Ürün Seç ve Hesapla")
    
    try:
        xl_urun = pd.ExcelFile(dosya_urun)
        sayfa_urun = st.selectbox("Ürün Kategorisi Seç (Sayfa)", xl_urun.sheet_names)
        
        # Sayfayı Oku
        df_urun_sayfa = pd.read_excel(dosya_urun, sheet_name=sayfa_urun)
        
        if len(df_urun_sayfa.columns) >=
