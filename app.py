import streamlit as st
import pandas as pd

st.set_page_config(page_title="3D Atölye ERP", layout="wide")

def temizle_para(deger):
    if pd.isna(deger): return 0.0
    if isinstance(deger, (int, float)): return float(deger)
    try:
        temiz = str(deger).replace(',', '.').replace(' ', '').strip()
        return float(temiz)
    except:
        return 0.0

st.title("🏭 3D Atölye ERP (Final)")
st.markdown("---")

with st.sidebar:
    st.header("Dosyalar")
    dosya_sarf = st.file_uploader("1. SARF MALZEME.xlsx", type=['xlsx'], key="sarf")
    dosya_urun = st.file_uploader("2. ÜRÜN LİSTESİ.xlsx", type=['xlsx'], key="urun")

tab1, tab2 = st.tabs(["📋 Maliyet Analizi", "📦 Depo Stokları"])

with tab1:
    if dosya_urun:
        try:
            xl = pd.ExcelFile(dosya_urun)
            secilen_sayfa = st.selectbox("Kategori Seç", xl.sheet_names)
            df_urun = pd.read_excel(dosya_urun, sheet_name=secilen_sayfa)

            # EĞER DETAYLI BİR LİSTEYSE (Lamba, Switch vb.)
            if len(df_urun.columns) >= 8:
                col_fil_maliyet = df_urun.columns[2]
                col_sarf1_fiyat = df_urun.columns[5]
                col_sarf2_fiyat = df_urun.columns[7]

                df_urun[col_fil_maliyet] = df_urun[col_fil_maliyet].apply(temizle_para)
                df_urun[col_sarf1_fiyat] = df_urun[col_sarf1_fiyat].apply(temizle_para)
                df_urun[col_sarf2_fiyat] = df_urun[col_sarf2_fiyat].apply(temizle_para)

                df_urun['TOPLAM_MALIYET'] = (
                    df_urun[col_fil_maliyet] + 
                    df_urun[col_sarf1_fiyat] + 
                    df_urun[col_sarf2_fiyat]
                )

                st.write(f"### {secilen_sayfa} - Maliyet Tablosu")
                
                # Sadece önemli sütunları gösterelim
                gosterilecek = [df_urun.columns[0], df_urun.columns[1], 'TOPLAM_MALIYET']
                
                # Eğer satış fiyatı (9. sütun) varsa kar hesabı da yap
                if len(df_urun.columns) > 8:
                    col_satis = df_urun.columns[8]
                    df_urun[col_satis] = df_urun[col_satis].apply(temizle_para)
                    df_urun['KAR'] = df_urun[col_satis] - df_urun['TOPLAM_MALIYET']
                    gosterilecek.append('KAR')
                    gosterilecek.append(col_satis)

                st.dataframe(df_urun[gosterilecek], use_container_width=True)
                
                with st.expander("Tüm Detayları Gör"):
                    st.dataframe(df_urun)

            else:
                # OYUNCAK GİBİ BASİT LİSTELER
                st.write(f"### {secilen_sayfa}")
                st.dataframe(df_urun, use_container_width=True)

        except Exception as e:
            st.error(f"Hata: {e}")
    else:
        st.info("Lütfen Ürün Listesi Excel dosyanı yükle.")

with tab2:
    if dosya_sarf:
        try:
            st.subheader("🧵 Filamentler")
            df_fil = pd.read_excel(dosya_sarf, sheet_name=0)
            st.dataframe(df_fil, use_container_width=True)

            st.subheader("🔩 Hırdavat & Parçalar")
            df_hir = pd.read_excel(dosya_sarf, sheet_name=1, header=1)
            df_hir = df_hir.iloc[:, :8]
            df_hir.columns = ['DIN', 'URUN', 'ACIKLAMA', 'STOK', 'ALINAN', 'PAKET_FIYATI', 'TEDARIKCI', 'TARIH']
            
            df_hir = df_hir.dropna(subset=['PAKET_FIYATI'])
            df_hir['PAKET_FIYATI'] = df_hir['PAKET_FIYATI'].apply(temizle_para)
            df_hir['ALINAN'] = df_hir['ALINAN'].apply(temizle_para)
            df_hir['BIRIM_MALIYET'] = df_hir['PAKET_FIYATI'] / df_hir['ALINAN']
            
            st.dataframe(df_hir, use_container_width=True)
        except Exception as e:
            st.error("Sarf malzeme dosyasında format sorunu var.")
    else:
        st.info("Lütfen Sarf Malzeme Excel dosyanı yükle.")
