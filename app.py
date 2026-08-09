import streamlit as st
import pandas as pd
import os
import time
import subprocess

st.set_page_config(page_title="İhale Takip & Analiz Sistemi", layout="wide")
st.title("🏗️ Doğu Avrupa İhale Takip ve Raporlama Paneli")

# 1. Excel Dosyalarını Okuma ve Birleştirme
@st.cache_data(ttl=60)
def verileri_yukle():
    df_listesi = []
    
    wb_yolu = os.path.join("Dunya_Bankasi_Botu", "wb_veriler.xlsx")
    if os.path.exists(wb_yolu):
        df_wb = pd.read_excel(wb_yolu)
        df_wb.rename(columns={"Tarih": "Tarih / Son Başvuru"}, inplace=True)
        df_listesi.append(df_wb)
        
    ebrd_yolu = os.path.join("EBRD_Botu", "ebrd_veriler.xlsx")
    if os.path.exists(ebrd_yolu):
        df_ebrd = pd.read_excel(ebrd_yolu)
        df_ebrd.rename(columns={"Son Başvuru / Tarih": "Tarih / Son Başvuru"}, inplace=True)
        df_listesi.append(df_ebrd)
        
    if len(df_listesi) > 0:
        birlesik_df = pd.concat(df_listesi, ignore_index=True)
        birlesik_df.fillna("Belirtilmemiş", inplace=True)
        return birlesik_df
    else:
        return pd.DataFrame(columns=["Kurum", "Ülke", "İhale/Proje Adı", "Tarih / Son Başvuru"])

# 2. Sol Menü ve Dinamik Filtre
st.sidebar.header("Ayarlar ⚙️")

if st.sidebar.button("🔄 Verileri İnternetten Güncelle"):
    with st.spinner("Botlar sahaya gönderildi. Güncel ihaleler toplanıyor, lütfen bekleyin..."):
        try:
            subprocess.run(["python", "Dunya_Bankasi_Botu/wb_cekici.py"], check=True)
            subprocess.run(["python", "EBRD_Botu/ebrd_cekici.py"], check=True)
            st.cache_data.clear()
            st.sidebar.success("✅ Veriler başarıyla güncellendi!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Güncelleme sırasında hata: {e}")

st.sidebar.info("Yapay Zeka API bağlantısı bölgesel kısıtlama nedeniyle şimdilik simülasyon modunda çalışıyor.")
st.sidebar.markdown("---")

st.sidebar.header("Arama Filtreleri")

df = verileri_yukle()

if not df.empty:
    mevcut_ulkeler = sorted(df["Ülke"].astype(str).unique().tolist())
    hedef_ulkeler = st.sidebar.multiselect("Hedef Ülkeler", mevcut_ulkeler, default=mevcut_ulkeler)
else:
    hedef_ulkeler = []
    st.sidebar.warning("Henüz Excel verisi yok. Lütfen yukarıdaki butona basarak verileri çekin.")

# 3. İhale Listesi Ekranı
st.subheader("📌 Güncel İhaleler ve Projeler")

if not df.empty:
    filtrelenmis_df = df[df["Ülke"].isin(hedef_ulkeler)]
    
    if not filtrelenmis_df.empty:
        st.write(f"Seçili kriterlere uygun **{len(filtrelenmis_df)}** proje listeleniyor.")
        st.dataframe(filtrelenmis_df, use_container_width=True)
        
        # 4. Yapay Zeka Analizi ve RAPORLAMA Bölümü
        st.markdown("---")
        st.subheader("🧠 Teknik Uygunluk Analizi ve Raporlama")
        
        # İhale seçimi
        secilen_ihale = st.selectbox("Analiz edilecek ve raporlanacak ihaleyi seçin:", filtrelenmis_df["İhale/Proje Adı"])
        
        # Seçilen ihalenin tüm satır bilgilerini (Ülke, Kurum vs.) yakalıyoruz
        ihale_bilgisi = filtrelenmis_df[filtrelenmis_df["İhale/Proje Adı"] == secilen_ihale].iloc[0]

        # Ekranı iki sütuna bölüyoruz
        sol_sutun, sag_sutun = st.columns(2)
        
        with sol_sutun:
            st.info(f"**Seçilen Proje:** {secilen_ihale}")
            
            if st.button("Seçili İhale İçin Şartname Analizi Yap"):
                with st.spinner("Sistem yapısal gereksinimleri inceliyor..."):
                    time.sleep(2)
                    st.success("✅ Analiz Tamamlandı!")
                    st.markdown("""
                    **1. Teknik Gereksinimler**
                    * Bu ölçekteki bir proje için uluslararası standartlarda (Eurocode) yapısal tasarım tecrübesi şarttır.
                    
                    **2. Potansiyel Riskler**
                    * Bölgesel tedarik zinciri kısıtlamaları ve uluslararası mevzuat farkları.
                    
                    **3. Uygunluk Yorumu**
                    * **UYGUN.** Şirketimizin Doğu Avrupa operasyon kapasitesi bu ihalenin gereksinimlerini karşılamaktadır.
                    """)
                    
        with sag_sutun:
            st.success("📄 Yönetim Raporu İndirmeye Hazır")
            
            # YENİ EKLENEN KISIM: İndirilecek Raporun Şablonu
            rapor_metni = f"""YÖNETİCİ ÖZETİ: İHALE TEKNİK UYGUNLUK RAPORU
---------------------------------------------------
Kurum: {ihale_bilgisi['Kurum']}
Ülke: {ihale_bilgisi['Ülke']}
Proje Adı: {ihale_bilgisi['İhale/Proje Adı']}
Son Başvuru: {ihale_bilgisi['Tarih / Son Başvuru']}

1. TEKNİK GEREKSİNİMLER
- Bu ölçekteki bir proje için uluslararası standartlarda (Eurocode) yapısal tasarım tecrübesi şarttır.

2. POTANSİYEL RİSKLER
- Bölgesel tedarik zinciri kısıtlamaları ve uluslararası mevzuat farkları şantiye yönetimini etkileyebilir.

3. UYGUNLUK YORUMU
- UYGUN. Şirketimizin Doğu Avrupa operasyon kapasitesi bu ihalenin gereksinimlerini karşılamaktadır.

---------------------------------------------------
*Bu rapor Şirket İhale Takip Sistemi tarafından otomatik oluşturulmuştur.*
"""
            # Raporu bilgisayara indiren sihirli buton
            st.download_button(
                label="📥 Üst Yönetim Raporunu İndir (TXT)",
                data=rapor_metni,
                file_name="Yonetici_Ozeti.txt",
                mime="text/plain"
            )
    else:
        st.warning("Seçili ülkeler için ihale bulunamadı. Lütfen sol menüden farklı ülkeler seçin.")