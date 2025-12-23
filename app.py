import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V15", layout="wide")

# --- PARA TEMİZLEME FONKSİYONU ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V15 - Final)")

# --- HAFIZA (Sepet) ---
if 'bom_list' not in st.session_state:
    st.session_state.bom_list = []

# --- SOL MENÜ: DOSYALAR ---
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            # Genelde 2. sayfa Hırdavat olur
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            # 2. satır başlık
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            if len(raw.columns) >= 6:
                # Sütunları al ve isimlendir
                raw = raw.iloc[:, :8]
                cols = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TEDARIKCI', 'TARIH']
                raw.columns = cols
                
                # Temizlik ve Hesaplama
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                raw = raw[raw['ALINAN'] > 0]
                
                # Birim Fiyatı Hesapla (Ama gösterme)
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                # Arama için İsim oluştur
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                
                df_depo = raw
                st.success(f"✅ Depo Hazır! ({len(df_depo)} Parça)")
            else:
                st.error("Sütun sayısı eksik.")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ANA EKRAN ---
if dosya_sarf and dosya_urun and df_depo is not None:
    
    st.subheader("2. Reçete Hazırla (Fiyatlar Gizli)")
    
    try:
        xl_ur = pd.ExcelFile(dosya_urun)
        sayfa_ur = st.selectbox("Kategori", xl_ur.sheet_names)
        df_ur = pd.read_excel(dosya_urun, sheet_name=sayfa_ur)
        
        if len(df_ur.columns) >= 2:
            c_kod = df_ur.columns[0]
            c_ad = df_ur.columns[1]
            liste = df_ur[c_kod].astype(str) + " | " + df_ur[c_ad].astype(str)
            secilen = st.selectbox("Ürün Seçiniz", liste)
            
            st.markdown("---")
            
            col1, col2 = st.columns([1, 1])
            
            # --- SOL: MALZEME SEÇİMİ ---
            with col1:
                st.info("👇 Malzeme Ekle")
                t1, t2, t3 = st.tabs(["📦 Depodan", "✏️ Elle Yaz", "🎨 Renk"])
                
                # 1. DEPO (FİYAT YOK)
                with t1:
                    parca = st.selectbox("Parça Seç", df_depo['ISIM'].unique())
                    adet = st.number_input("Adet", min_value=1, value=1)
                    
                    if st.button("Depodan Ekle ➕"):
                        st.session_state.bom_list.append({
                            "Kaynak": "Depo",
                            "İsim": parca,
                            "Miktar": adet
                        })
                        st.success("Eklendi")

                # 2. MANUEL
                with t2:
                    m_isim = st.text_input("Parça Adı")
                    m_adet = st.number_input("Adet", min_value=1, value=1, key="man")
                    m_fiyat = st.number_input("Birim Fiyat", value=0.0)
                    
                    if st.button("Manuel Ekle ➕"):
                        st.session_state.bom_list.append({
                            "Kaynak": "Manuel",
                            "İsim": m_isim,
                            "Miktar": m_adet,
                            "SabitFiyat": m_fiyat
                        })
                        st.success("Eklendi")

                # 3. RENK
                with t3:
                    renkler = ["SİYAH", "BEYAZ", "GRİ", "KIRMIZI", "MAVİ", "SARI"]
                    r_sec = st.selectbox("Renk", renkler)
                    r_ozel = st.text_input("
