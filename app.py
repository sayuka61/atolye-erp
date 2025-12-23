import streamlit as st
import pandas as pd

# Sayfa Genişliği
st.set_page_config(page_title="3D Atölye Üretim & BOM", layout="wide")

# --- FONKSİYONLAR ---
def veri_yukle(file):
    try:
        # Filament (Sayfa 1)
        df_fil = pd.read_excel(file, sheet_name=0)
        
        # Hırdavat (Sayfa 2) - Başlık satırını bulmaya çalışır
        df_hir = pd.read_excel(file, sheet_name=1, header=1) 
        
        # Sütun isimlerini sabitleyelim (Excel'deki karmaşayı önlemek için)
        # Senin Excel sırasına göre: Kod, Ad, Açıklama, Stok, Alınan, Fiyat...
        df_hir = df_hir.iloc[:, 0:8] # İlk 8 sütunu al
        df_hir.columns = ['KOD', 'URUN_ADI', 'ACIKLAMA', 'STOK', 'ALINAN_ADET', 'PAKET_FIYATI', 'TEDARIKCI', 'TARIH']
        
        # Temizlik ve Hesaplama
        df_hir = df_hir.dropna(subset=['PAKET_FIYATI']) # Fiyatı olmayanları at
        df_hir['PAKET_FIYATI'] = pd.to_numeric(df_hir['PAKET_FIYATI'], errors='coerce')
        df_hir['ALINAN_ADET'] = pd.to_numeric(df_hir['ALINAN_ADET'], errors='coerce')
        
        # Birim Maliyet Hesabı
        df_hir['BIRIM_MALIYET'] = df_hir['PAKET_FIYATI'] / df_hir['ALINAN_ADET']
        
        return df_fil, df_hir
    except Exception as e:
        return None, None

# --- ARAYÜZ ---
st.title("🏭 3D Atölye Üretim Yönetimi")

# Oturum Durumu (Sepet Mantığı İçin)
if 'rechete_listesi' not in st.session_state:
    st.session_state.rechete_listesi = []

# 1. ADIM: EXCEL YÜKLEME
with st.sidebar:
    st.header("Depo Verisi")
    dosya = st.file_uploader("SARF MALZEME.xlsx Yükle", type=['xlsx'])

if dosya:
    df_fil, df_hir = veri_yukle(dosya)
    
    if df_hir is not None:
        st.sidebar.success("✅ Depo Bağlandı")
        
        # SEKME YAPISI
        tab1, tab2, tab3 = st.tabs(["📝 BOM (Reçete) Oluştur", "📦 Ürün Listem", "🔍 Depo Stokları"])
        
        # --- TAB 1: BOM OLUŞTURMA (SENİN İSTEDİĞİN YER) ---
        with tab1:
            st.header("Yeni Ürün Reçetesi Hazırla")
            
            # Ürün Bilgileri
            col_u1, col_u2 = st.columns(2)
            urun_adi = col_u1.text_input("Üretilecek Ürün Adı", placeholder="Örn: Basketbol Sahası")
            urun_kodu = col_u2.text_input("Ürün Kodu (SKU)", placeholder="Örn: PRD-001")
            
            st.markdown("---")
            
            # Malzeme Ekleme Alanı
            c1, c2, c3 = st.columns([3, 1, 1])
            
            # Tüm malzemeleri tek listede birleştir (İsim + Açıklama)
            malzeme_secenekleri = df_hir['URUN_ADI'].astype(str) + " (" + df_hir['ACIKLAMA'].astype(str) + ")"
            
            secilen_malzeme = c1.selectbox("Depodan Malzeme Seç", malzeme_secenekleri)
            adet = c2.number_input("Adet", min_value=1, value=1)
            
            # Seçilen malzemenin maliyetini bul
            secilen_data = df_hir[malzeme_secenekleri == secilen_malzeme].iloc[0]
            birim_maliyet = secilen_data['BIRIM_MALIYET']
            
            if c3.button("➕ Reçeteye Ekle"):
                st.session_state.rechete_listesi.append({
                    "Malzeme": secilen_malzeme,
                    "Adet": adet,
                    "Birim Maliyet": birim_maliyet,
                    "Toplam": adet * birim_maliyet
                })
                st.success(f"{adet} adet {secilen_malzeme} eklendi!")

            # Reçete Tablosu
            if st.session_state.rechete_listesi:
                st.write("### 📋 Şu Anki Reçete Listesi")
                rechete_df = pd.DataFrame(st.session_state.rechete_listesi)
                st.dataframe(rechete_df, use_container_width=True)
                
                # Toplam Hesap
                toplam_maliyet = rechete_df['Toplam'].sum()
                
                # Filament Ekleme (Manuel)
                st.info("Filament maliyetini aşağıdan manuel ekleyebilirsin:")
                f_col1, f_col2 = st.columns(2)
                fil_gram = f_col1.number_input("Harcanan Filament (Gram)", value=0)
                fil_fiyat = f_col2.number_input("Filament Gram Maliyeti (TL)", value=0.5)
                fil_toplam = fil_gram * fil_fiyat
                
                GENEL_TOPLAM = toplam_maliyet + fil_toplam
                
                st.markdown(f"""
                ### 💰 TOPLAM MALİYET: :green[{GENEL_TOPLAM:.2f} TL]
                """)
                
                if st.button("💾 BU ÜRÜNÜ KAYDET (Simülasyon)"):
                    st.toast(f"{urun_adi} başarıyla sisteme kaydedildi!")
                    st.balloons()
            
        # --- TAB 2: ÜRÜN LİSTEM (DEMO) ---
        with tab2:
            st.write("Burada daha önce kaydettiğin BOM listeleri listelenecek.")
            st.info("Şu an veritabanı bağlı olmadığı için kaydettiklerin sayfa yenilenince gider. Kalıcı olması için Google Sheets bağlamamız gerekecek.")

        # --- TAB 3: DEPO STOKLARI ---
        with tab3:
            st.dataframe(df_hir, use_container_width=True)
            
    else:
        st.error("Excel formatı okunamadı. Lütfen 'SARF MALZEME' dosyasını yüklediğinden emin ol.")
else:
    st.info("Başlamak için soldaki menüden Excel dosyanı yükle.")
