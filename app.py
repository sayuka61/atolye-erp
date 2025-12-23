import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V10", layout="wide")

# --- YARDIMCI: PARA TEMİZLEME ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V10 Final)")

# --- HAFIZA ---
if 'bom' not in st.session_state:
    st.session_state.bom = []

# --- SOL MENÜ: AYARLAR ---
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    # DEPO VERİSİNİ OKU
    df_depo = None
    if dosya_sarf:
        try:
            # Kullanıcıya sor: Hangi sayfa?
            xl = pd.ExcelFile(dosya_sarf)
            sayfa = st.selectbox("Depo Sayfası (Genelde 2. Sayfa)", xl.sheet_names, index=1)
            
            # Veriyi oku
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            # Sütunları düzenle (İlk 8 sütun)
            if len(raw.columns) >= 6:
                raw = raw.iloc[:, :8]
                raw.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TEDARIKCI', 'TARIH']
                
                # Temizlik
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                raw = raw[raw['ALINAN'] > 0]
                
                # Birim Maliyet
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                
                df_depo = raw
                st.success(f"✅ Depo Hazır: {len(df_depo)} Parça")
            else:
                st.error("Seçilen sayfada sütun eksik.")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ANA EKRAN ---
if dosya_sarf and dosya_urun and df_depo is not None:
    
    st.subheader("2. Ürün ve Reçete İşlemleri")
    
    try:
        xl_ur = pd.ExcelFile(dosya_urun)
        sayfa_ur = st.selectbox("Ürün Kategorisi", xl_ur.sheet_names)
        df_ur = pd.read_excel(dosya_urun, sheet_name=sayfa_ur)
        
        # Ürün Listesi (Kod - İsim)
        if len(df_ur.columns) >= 2:
            col_kod = df_ur.columns[0]
            col_ad = df_ur.columns[1]
            liste = df_ur[col_kod].astype(str) + " | " + df_ur[col_ad].astype(str)
            secilen = st.selectbox("Ürün Seçiniz", liste)
            
            st.markdown("---")
            
            # --- HESAPLAMA ALANI ---
            c1, c2 = st.columns([1, 1])
            
            # SOL: EKLEME
            with c1:
                st.info("👇 Malzeme Ekle")
                
                # 1. Hırdavat
                parca = st.selectbox("Depodan Parça", df_depo['ISIM'].unique())
                adet = st.number_input("Adet", min_value=1, value=1)
                
                if st.button("Parça Ekle ➕"):
                    veri = df_depo[df_depo['ISIM'] == parca].iloc[0]
                    st.session_state.bom.append({
                        "Tür": "Parça",
                        "İsim": parca,
                        "Miktar": adet,
                        "Birim": veri['BIRIM'],
                        "Toplam": adet * veri['BIRIM']
                    })
                
                st.write("") # Boşluk
                
                # 2. Filament
                gram = st.number_input("Filament (Gram)", value=0)
                gram_tl = st.number_input("Gram Fiyatı (TL)", value=0.60)
                
                if st.button("Filament Ekle 🧶"):
                    st.session_state.bom.append({
                        "Tür": "Filament",
                        "İsim": "Filament Tüketimi",
                        "Miktar": gram,
                        "Birim": gram_tl,
                        "Toplam": gram * gram_tl
                    })
                    
                st.write("")
                if st.button("TEMİZLE 🗑️", type="primary"):
                    st.session_state.bom = []
                    st.rerun()

            # SAĞ: LİSTE VE SONUÇ
            with c2:
                st.success("🧾 Reçete Özeti")
                
                if st.session_state.bom:
                    df_bom = pd.DataFrame(st.session_state.bom)
                    st.dataframe(df_bom, use_container_width=True)
                    
                    toplam = df_bom['Toplam'].sum()
                    st.metric("TOPLAM MALİYET", f"{toplam:.2f} TL")
                    
                    # Eski Veriyi Göster
                    with st.expander("Eski Excel Verisi (Kıyasla)"):
                        kod = secilen.split(' | ')[0]
                        eski = df_ur[df_ur[col_kod].astype(str) == kod]
                        st.dataframe(eski)
                else:
                    st.warning("Henüz malzeme eklenmedi.")
                    
        else:
            st.error("Ürün listesinde sütunlar eksik.")
            
    except Exception as e:
        st.error(f"Ürün listesi hatası: {e}")

else:
    st.info("👈 Lütfen soldan dosyaları yükle.")
