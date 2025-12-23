import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP Pro", layout="wide")

# --- YARDIMCI: PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        temiz = str(deger).replace(',', '.').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

# --- YARDIMCI: DEPO VERİSİNİ OKU ---
def depo_oku(dosya):
    try:
        # Filament (Sayfa 1)
        df_fil = pd.read_excel(dosya, sheet_name=0)
        
        # Hırdavat (Sayfa 2) - 2. satır başlık
        df_hir = pd.read_excel(dosya, sheet_name=1, header=1)
        df_hir = df_hir.iloc[:, :8] # İlk 8 sütun
        df_hir.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET_FIYATI', 'TEDARIKCI', 'TARIH']
        
        # Hesaplamalar
        df_hir = df_hir.dropna(subset=['PAKET_FIYATI'])
        df_hir['PAKET_FIYATI'] = df_hir['PAKET_FIYATI'].apply(temizle_para)
        df_hir['ALINAN'] = df_hir['ALINAN'].apply(temizle_para)
        df_hir['BIRIM_MALIYET'] = df_hir['PAKET_FIYATI'] / df_hir['ALINAN']
        
        # Seçim Listesi İçin Yeni Sütun (Ad + Açıklama)
        df_hir['SECIM_ISMI'] = df_hir['URUN'].astype(str) + " - " + df_hir['ACIKLAMA'].astype(str)
        
        return df_fil, df_hir
    except Exception as e:
        return None, None

# --- ARAYÜZ ---
st.title("🏭 3D Atölye ERP (BOM Modülü)")

# Session State (Sepet Hafızası)
if 'sepet' not in st.session_state:
    st.session_state.sepet = []

with st.sidebar:
    st.header("📂 Dosyalar")
    dosya_sarf = st.file_uploader("1. SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("2. ÜRÜN LİSTESİ.xlsx (Opsiyonel)", type=['xlsx'], key="urun")

    # Depo verisini bir kere oku ve hafızaya al
    if dosya_sarf:
        df_fil, df_hir = depo_oku(dosya_sarf)
    else:
        df_fil, df_hir = None, None

# SEKMELER
tab1, tab2, tab3 = st.tabs(["📝 YENİ REÇETE (BOM) OLUŞTUR", "📋 Mevcut Ürün Listeleri", "📦 Depo Stokları"])

# --- TAB 1: REÇETE OLUŞTURUCU (SENİN İSTEDİĞİN) ---
with tab1:
    if df_hir is not None:
        st.subheader("Yeni Ürün Maliyet Hesaplayıcı")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info("👇 Malzemeleri Buradan Ekle")
            
            # 1. Depodan Malzeme Seç
            malzeme_listesi = df_hir['SECIM_ISMI'].unique()
            secilen_malzeme = st.selectbox("Parça Seç", malzeme_listesi)
            adet = st.number_input("Adet", min_value=1, value=1)
            
            if st.button("Sepete Ekle ➕"):
                # Seçilenin fiyatını bul
                veri = df_hir[df_hir['SECIM_ISMI'] == secilen_malzeme].iloc[0]
                birim_fiyat = veri['BIRIM_MALIYET']
                
                st.session_state.sepet.append({
                    "Malzeme": secilen_malzeme,
                    "Adet": adet,
                    "Birim Maliyet": birim_fiyat,
                    "Tutar": adet * birim_fiyat
                })
                st.success(f"{secilen_malzeme} eklendi.")

            st.markdown("---")
            
            # 2. Filament Ekle
            st.write("🧵 **Filament Hesabı**")
            gramaj = st.number_input("Harcanan Gram", value=0)
            gram_maliyet = st.number_input("Gram Maliyeti (TL)", value=0.55) # Ortalama
            
            if st.button("Listeyi Temizle 🗑️"):
                st.session_state.sepet = []
                st.rerun()

        with col2:
            st.write("### 🧾 Ürün Reçetesi")
            
            if st.session_state.sepet or gramaj > 0:
                # Sepeti Tablo Yap
                df_sepet = pd.DataFrame(st.session_state.sepet)
                
                if not df_sepet.empty:
                    st.dataframe(df_sepet, use_container_width=True)
                    toplam_parca = df_sepet['Tutar'].sum()
                else:
                    toplam_parca = 0
                
                # Filament Tutarı
                fil_tutar = gramaj * gram_maliyet
                
                st.divider()
                st.write(f"🔩 **Parça Toplamı:** {toplam_parca:.2f} TL")
                st.write(f"🧵 **Filament Toplamı:** {fil_tutar:.2f} TL")
                
                genel_toplam = toplam_parca + fil_tutar
                st.markdown(f"## 💰 TOPLAM MALİYET: :green[{genel_toplam:.2f} TL]")
                
                st.warning("Not: Bu reçeteyi beğendiysen Excel dosyanın 'ÜRÜN LİSTESİ' kısmına yeni satır olarak ekleyebilirsin.")
            else:
                st.info("Henüz malzeme seçmedin.")

    else:
        st.warning("👈 Önce soldan 'SARF MALZEME' dosyasını yükle ki stokları görebileyim.")

# --- TAB 2: MEVCUT LİSTELER (ESKİ V4 ÖZELLİĞİ) ---
with tab2:
    if dosya_urun:
        try:
            xl = pd.ExcelFile(dosya_urun)
            secilen_sayfa = st.selectbox("Kategori", xl.sheet_names)
            df_urun = pd.read_excel(dosya_urun, sheet_name=secilen_sayfa)

            if len(df_urun.columns) >= 8: # Detaylı Liste
                # V4'teki hesaplama mantığı aynı kalıyor
                col_fil = df_urun.columns[2]
                col_sarf1 = df_urun.columns[5]
                col_sarf2 = df_urun.columns[7]
                
                # Temizle ve Topla
                for c in [col_fil, col_sarf1, col_sarf2]:
                    df_urun[c] = df_urun[c].apply(temizle_para)
                
                df_urun['TOPLAM_MALIYET'] = df_urun[col_fil] + df_urun[col_sarf1] + df_urun[col_sarf2]
                
                # Göster
                cols = [df_urun.columns[0], df_urun.columns[1], 'TOPLAM_MALIYET']
                st.dataframe(df_urun[cols], use_container_width=True)
            else:
                st.dataframe(df_urun, use_container_width=True)
        except:
            st.error("Ürün listesi okunurken hata.")
    else:
        st.info("Yüklü ürün listesi yok.")

# --- TAB 3: DEPO ---
with tab3:
    if df_hir is not None:
        st.dataframe(df_hir[['URUN', 'ACIKLAMA', 'STOK', 'BIRIM_MALIYET']], use_container_width=True)
    else:
        st.info("Veri yok.")
