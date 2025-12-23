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
            raw_hir['FULL_ISIM'] = raw_hir['URUN'].astype(str) + " (" + raw_hir['ACIKLAMA'].astype(str) + ")"
            df_hir = raw_hir
            st.success("Depo Bağlandı ✅")
        except:
            st.error("Sarf Malzeme dosyası okunamadı.")

# --- ANA EKRAN ---

if dosya_sarf and dosya_urun and df_hir is not None:
    
    # Adım 1: Hangi Listeden Ürün Seçeceğiz?
    xl_urun = pd.ExcelFile(dosya_urun)
    sayfa = st.selectbox("1. Adım: Kategori Seç", xl_urun.sheet_names)
    
    # O sayfayı oku
    df_urun_sayfa = pd.read_excel(dosya_urun, sheet_name=sayfa)
    
    # Ürün Seçimi İçin Listeyi Hazırla (Kod + İsim)
    # Genelde 1. sütun Kod, 2. sütun İsim oluyor
    col_kod = df_urun_sayfa.columns[0]
    col_isim = df_urun_sayfa.columns[1]
    
    # Ürün Listesi Dropdown
    urun_listesi = df_urun_sayfa[col_kod].astype(str) + " - " + df_urun_sayfa[col_isim].astype(str)
    secilen_urun_full = st.selectbox("2. Adım: Ürün Seç", urun_listesi)
    
    st.divider()

    # --- ÇALIŞMA ALANI ---
    col_sol, col_sag = st.columns([1, 2])

    with col_sol:
        st.subheader("🛠️ BOM Hazırla")
        st.info(f"Şu an işlem yapılan: **{secilen_urun_full}**")
        
        # BOM EKLEME FORMU
        st.write("Depodan Parça Ekle:")
        secilen_parca = st.selectbox("Parça Ara", df_hir['FULL_ISIM'].unique())
        adet = st.number_input("Adet", min_value=1, value=1)
        
        if st.button("Listeye Ekle ➕"):
            # Seçilen parçanın maliyetini bul
            parca_data = df_hir[df_hir['FULL_ISIM'] == secilen_parca].iloc[0]
            birim_fiyat = parca_data['BIRIM_MALIYET']
            
            st.session_state.bom_listesi.append({
                "Tip": "Hırdavat",
                "Malzeme": secilen_parca,
                "Adet": adet,
                "Birim Maliyet": birim_fiyat,
                "Toplam": adet * birim_fiyat
            })
            st.success("Eklendi")

        st.markdown("---")
        st.write("Filament Ekle:")
        fil_gram = st.number_input("Gramaj", value=0)
        fil_fiyat = st.number_input("Gram Maliyeti", value=0.5)
        
        if st.button("Filament Ekle 🧵"):
             st.session_state.bom_listesi.append({
                "Tip": "Filament",
                "Malzeme": "Filament Tüketimi",
                "Adet": fil_gram,
                "Birim Maliyet": fil_fiyat,
                "Toplam": fil_gram * fil_fiyat
            })

        st.markdown("---")
        if st.button("Temizle / Sıfırla 🗑️"):
            st.session_state.bom_listesi = []
            st.rerun()

    with col_sag:
        st.subheader("🧾 Maliyet Hesap Tablosu")
        
        if st.session_state.bom_listesi:
            df_bom = pd.DataFrame(st.session_state.bom_listesi)
            
            # Tabloyu Göster
            st.dataframe(df_bom, use_container_width=True)
            
            # TOPLAM HESAP
            toplam_tutar = df_bom['Toplam'].sum()
            
            st.markdown(f"""
            ### 💰 TOPLAM MALİYET: :green[{top
