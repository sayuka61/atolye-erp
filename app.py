import streamlit as st
import pandas as pd

# --- SAYFA AYARI ---
st.set_page_config(page_title="3D ERP V17 Final", layout="wide")

# --- YARDIMCI: PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        # Virgülü noktaya çevir, TL ve boşlukları at
        t = str(deger).replace(',', '.').replace('TL', '').replace(' ', '').strip()
        return float(t)
    except:
        return 0.0

# --- BAŞLIK ---
st.title("🏭 3D Atölye ERP (V17 - Sorunsuz Mod)")

# --- HAFIZA (SEPET) ---
if 'bom_listesi' not in st.session_state:
    st.session_state.bom_listesi = []

# ==========================================
# 1. BÖLÜM: DOSYA YÜKLEME VE OKUMA
# ==========================================
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    # DEPOYU OKU (Varsa)
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            # Genelde 2. sayfa (index=1) Hırdavat olur
            sayfa_adi = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            # 2. satır başlıktır (header=1)
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa_adi, header=1)
            
            # Sütun kontrolü (En az 6 sütun lazım)
            if len(raw.columns) >= 6:
                # İlk 8 sütunu al ve isimlendir
                raw = raw.iloc[:, :8]
                cols = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TED', 'TARIH']
                raw.columns = cols
                
                # Temizlik
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                # 0'a bölme hatasını önle
                raw = raw[raw['ALINAN'] > 0]
                
                # Birim Maliyet (Hesapla ama gösterme)
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                # Arama için İsim oluştur
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                
                df_depo = raw
                st.success(f"✅ Depo Okundu: {len(df_depo)} Parça")
            else:
                st.error("Seçilen sayfada sütunlar eksik/hatalı.")
        except Exception as e:
            st.error(f"Depo okuma hatası: {e}")

# ==========================================
# 2. BÖLÜM: ANA EKRAN (REÇETE HAZIRLAMA)
# ==========================================

# Sadece dosyalar yüklüyse ekranı göster
if dosya_sarf and dosya_urun and df_depo is not None:
    
    st.subheader("2. Reçete Hazırla (Fiyatlar Gizli)")
    
    try:
        # Ürün Listesini Oku
        xl_ur = pd.ExcelFile(dosya_urun)
        sayfa_ur = st.selectbox("Kategori Seç", xl_ur.sheet_names)
        df_ur = pd.read_excel(dosya_urun, sheet_name=sayfa_ur)
        
        # Sütunları kontrol et
        if len(df_ur.columns) >= 2:
            k_col = df_ur.columns[0]
            a_col = df_ur.columns[1]
            
            # Seçim Listesi Hazırla
            # (Burada hata vermemesi için string birleştiriyoruz)
            liste = df_ur[k_col].astype(str) + " | " + df_ur[a_col].astype(str)
            secilen_urun = st.selectbox("Ürün Seç", liste)
            
            st.markdown("---")
            
            # İki Kolonlu Yapı
            col1, col2 = st.columns([1, 1])
            
            # --- SOL KOLON: MALZEME EKLEME ---
            with col1:
                st.info("👇 Malzemeleri Buradan Ekle")
                
                tab1, tab2, tab3 = st.tabs(["📦 Depodan Seç", "✏️ Elle Yaz", "🎨 Renk Ekle"])
                
                # 1. DEPO (Fiyat Göstermez)
                with tab1:
                    parca = st.selectbox("Parça Ara", df_depo['ISIM'].unique())
                    adet = st.number_input("Adet", min_value=1, value=1)
                    
                    if st.button("Depodan Ekle ➕"):
                        st.session_state.bom_listesi.append({
                            "Kaynak": "Depo",
                            "Ad": parca,
                            "Miktar": adet
                        })
                        st.success("Eklendi")

                # 2. MANUEL (Fiyat Girmek Zorunlu)
                with tab2:
                    m_isim = st.text_input("Parça Adı (Örn: Özel Vida)")
                    m_adet = st.number_input("Adet", min_value=1, value=1, key="man_adet")
                    m_fiyat = st.number_input("Birim Fiyat (TL)", value=0.0)
                    
                    if st.button("Manuel Ekle ➕"):
                        st.session_state.bom_listesi.append({
                            "Kaynak": "Manuel",
                            "Ad": m_isim,
                            "Miktar": m_adet,
                            "SabitFiyat": m_fiyat
                        })
                        st.success("Eklendi")

                # 3. RENK
                with tab3:
                    renkler = ["SİYAH", "BEYAZ", "GRİ", "KIRMIZI", "MAVİ", "SARI", "YEŞİL", "TURUNCU"]
                    r_sec = st.selectbox("Renk Seç", renkler)
                    r_ozel = st.text_input("Veya Özel Renk Yaz")
                    # Hangisi doluysa onu al
                    final_renk = r_ozel if r_ozel else r_sec
                    
                    if st.button("Renk Ekle 🖌️"):
                        st.session_state.bom_listesi.append({
                            "Kaynak": "Renk",
                            "Ad": f"{final_renk} Filament",
                            "Miktar": 1
                        })
                        st.success("Renk Eklendi")
                
                st.divider()
                if st.button("🗑️ LİSTEYİ TEMİZLE", type="primary"):
                    st.session_state.bom_listesi = []
                    st.rerun()

            # --- SAĞ KOLON: LİSTE VE HESAP ---
            with col2:
                t_liste, t_hesap = st.tabs(["📋 Liste (Mühendis)", "💰 MALİYET (Muhasebe)"])
                
                # SEKME 1: SADECE LİSTE
                with t_liste:
                    if st.session_state.bom_listesi:
                        # DataFrame oluştur ama sadece Ad ve Miktar göster
                        df_goster = pd.DataFrame(st.session_state.bom_listesi)
                        st.dataframe(df_goster[['Ad', 'Miktar']], use_container_width=True)
                    else:
                        st.info("Liste şu an boş.")

                # SEKME 2: HESAPLAMA (Excel'den Çeker)
                with t_hesap:
                    st.caption("Butona basınca Excel'deki **ANLIK** fiyatlar çekilir.")
                    
                    if st.button("GÜNCEL MALİYETİ HESAPLA 💸"):
                        if st.session_state.bom_listesi:
                            hesapli_liste = []
                            toplam_tutar = 0
                            
                            for item in st.session_state.bom_listesi:
                                isim = item['Ad']
                                miktar = item['Miktar']
                                kaynak = item['Kaynak']
                                birim_fiyat = 0
                                
                                # Kaynağa göre fiyat bul
                                if kaynak == "Depo":
                                    # Excel tablosunda bu ismi ara
                                    bulunan = df_depo[df_depo['ISIM'] == isim]
                                    if not bulunan.empty:
                                        birim_fiyat = bulunan.iloc[0]['BIRIM']
                                    else:
                                        birim_fiyat = 0 # Bulunamazsa 0
                                
                                elif kaynak == "Manuel":
                                    birim_fiyat = item['SabitFiyat']
                                
                                # Renklerin maliyeti 0 kabul edilir
                                
                                tutar = miktar * birim_fiyat
                                toplam_tutar += tutar
                                
                                hesapli_liste.append({
                                    "Malzeme": isim,
                                    "Adet": miktar,
                                    "Birim": f"{birim_fiyat:.2f}",
                                    "Tutar": f"{tutar:.2f}"
                                })
                            
                            # Sonuç Tablosu
                            st.dataframe(pd.DataFrame(hesapli_liste), use_container_width=True)
                            st.metric("TOPLAM MALİYET", f"{toplam_tutar:.2f} TL")
                        else:
                            st.warning("Liste boş, hesaplanacak bir şey yok.")

        else:
            st.error("Ürün listesinde en az 2 sütun (Kod, İsim) olmalı.")

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

else:
    st.info("👈 Lütfen sol menüden 'SARF MALZEME' ve 'ÜRÜN LİSTESİ' dosyalarını yükleyin.")
