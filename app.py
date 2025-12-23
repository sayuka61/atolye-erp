import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D ERP V12 - Serbest Mod", layout="wide")

# --- FONKSİYONLAR ---
def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        t = str(deger).replace(',', '.').replace('TL', '').strip()
        return float(t)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (V12 - Serbest Mod)")

# --- HAFIZA ---
if 'bom' not in st.session_state:
    st.session_state.bom = []

# --- SOL MENÜ: DOSYALAR ---
with st.sidebar:
    st.header("1. Dosyaları Yükle")
    dosya_sarf = st.file_uploader("SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")
    
    st.divider()
    
    # DEPO VERİSİNİ OKU
    df_depo = None
    if dosya_sarf:
        try:
            xl = pd.ExcelFile(dosya_sarf)
            sayfa = st.selectbox("Depo Sayfası", xl.sheet_names, index=1)
            raw = pd.read_excel(dosya_sarf, sheet_name=sayfa, header=1)
            
            if len(raw.columns) >= 6:
                raw = raw.iloc[:, :8]
                raw.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET', 'TEDARIKCI', 'TARIH']
                raw = raw.dropna(subset=['PAKET'])
                raw['PAKET'] = raw['PAKET'].apply(temizle_para)
                raw['ALINAN'] = raw['ALINAN'].apply(temizle_para)
                raw = raw[raw['ALINAN'] > 0]
                raw['BIRIM'] = raw['PAKET'] / raw['ALINAN']
                raw['ISIM'] = raw['URUN'].astype(str) + " - " + raw['ACIKLAMA'].astype(str)
                df_depo = raw
                st.success(f"✅ Depo Hazır ({len(df_depo)} Parça)")
            else:
                st.error("Sütun sayısı eksik.")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ANA EKRAN ---
if dosya_sarf and dosya_urun and df_depo is not None:
    
    st.subheader("2. Reçete Hazırlama")
    
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
            
            # --- SOL TARAF: PARÇA EKLEME ---
            with c1:
                st.info("👇 Malzeme Ekle")
                
                # SEKMELİ YAPI (Depodan Seç / Elle Yaz / Renk)
                tab_depo, tab_manuel, tab_renk = st.tabs(["📦 Depodan Seç", "✏️ Elle Yaz", "🎨 Renk Ekle"])
                
                # 1. DEPO SEÇİMİ (Otomatik)
                with tab_depo:
                    parca_secimi = st.selectbox("Parça Ara (Switch, Vida vb.)", df_depo['ISIM'].unique())
                    adet_depo = st.number_input("Adet", min_value=1, value=1, key="adet_depo")
                    
                    if st.button("Depodan Ekle ➕"):
                        veri = df_depo[df_depo['ISIM'] == parca_secimi].iloc[0]
                        st.session_state.bom.append({
                            "Tür": "Parça",
                            "İsim": parca_secimi,
                            "Miktar": f"{adet_depo} Adet",
                            "Birim Maliyet": veri['BIRIM'],
                            "Tutar": adet_depo * veri['BIRIM']
                        })
                        st.success("Eklendi")

                # 2. MANUEL GİRİŞ (Excel'de olmayanlar için)
                with tab_manuel:
                    st.write("Listede bulamadıysan buradan ekle:")
                    manuel_isim = st.text_input("Parça Adı (Örn: Duy Seti)", "")
                    manuel_adet = st.number_input("Adet", min_value=1, value=1, key="adet_man")
                    manuel_fiyat = st.number_input("Birim Maliyeti (TL)", value=0.0)
                    
                    if st.button("Manuel Ekle ➕"):
                        if manuel_isim:
                            st.session_state.bom.append({
                                "Tür": "Ekstra",
                                "İsim": manuel_isim,
                                "Miktar": f"{manuel_adet} Adet",
                                "Birim Maliyet": manuel_fiyat,
                                "Tutar": manuel_adet * manuel_fiyat
                            })
                            st.success("Manuel Eklendi")
                        else:
                            st.warning("Lütfen isim yaz.")

                # 3. RENK SEÇİMİ
                with tab_renk:
                    renkler = ["SİYAH", "BEYAZ", "GRİ", "KIRMIZI", "MAVİ", "SARI", "YEŞİL", "TURUNCU", "MOR", "KAHVERENGİ", "TEN RENGİ", "PEMBE", "ŞEFFAF"]
                    secilen_renk = st.selectbox("Filament Rengi", renkler)
                    ozel_renk = st.text_input("Veya Özel Renk Yaz", "")
                    renk_final = ozel_renk if ozel_renk else secilen_renk
                    
                    if st.button("Rengi Ekle 🖌️"):
                        st.session_state.bom.append({
                            "Tür": "Renk",
                            "İsim": f"{renk_final} Filament",
                            "Miktar": "-",
                            "Birim Maliyet": 0,
                            "Tutar": 0.0
                        })
                        st.success("Renk Eklendi")

                st.divider()
                if st.button("LİSTEYİ SIFIRLA 🗑️", type="primary"):
                    st.session_state.bom = []
                    st.rerun()

            # --- SAĞ TARAF: LİSTE ---
            with c2:
                st.success("🧾 Üretim Reçetesi (BOM)")
                
                if st.session_state.bom:
                    df_bom = pd.DataFrame(st.session_state.bom)
                    
                    st.dataframe(
                        df_bom, 
                        column_config={
                            "Birim Maliyet": st.column_config.NumberColumn(format="%.2f TL"),
                            "Tutar": st.column_config.NumberColumn(format="%.2f TL")
                        },
                        use_container_width=True
                    )
                    
                    toplam = df_bom['Tutar'].sum()
                    st.metric("TOPLAM MALİYET", f"{toplam:.2f} TL")
                    
                    with st.expander("Kıyaslama (Eski Veri)"):
                        kod = secilen.split(' | ')[0]
                        eski = df_ur[df_ur[col_kod].astype(str) == kod]
                        st.dataframe(eski)
                else:
                    st.info("Reçete boş.")
                    
        else:
            st.error("Ürün listesi sütunları eksik.")
            
    except Exception as e:
        st.error(f"Hata: {e}")

else:
    st.info("👈 Dosyaları yükleyerek başla.")
