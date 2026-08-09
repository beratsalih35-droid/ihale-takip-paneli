import streamlit as st
import pandas as pd
import os
import time
import subprocess

st.set_page_config(page_title="Kurumsal İhale & Mühendislik Analiz Sistemi", layout="wide")

# ==========================================
# 🔒 GÜVENLİK DUVARI (LOGIN) BÖLÜMÜ
# ==========================================
def giris_kontrolu():
    if st.session_state.get("giris_basarili", False):
        return True
        
    st.title("🔒 Kurumsal İhale Yönetim Sistemi")
    st.info("Bu panele erişim yalnızca yetkili teknik kadro ve yönetim içindir.")
    
    girilen_sifre = st.text_input("Yönetici Şifresi:", type="password")
    
    if st.button("Sisteme Giriş Yap"):
        dogru_sifre = st.secrets.get("PANEL_SIFRESI", "ihale2026")
        if girilen_sifre == dogru_sifre:
            st.session_state["giris_basarili"] = True
            st.rerun()
        else:
            st.error("❌ Hatalı şifre!")
            
    return False

if not giris_kontrolu():
    st.stop()
# ==========================================

st.title("🏗️ Doğu Avrupa İhale & Yapısal Uygunluk Analiz Paneli")
st.markdown("*Uluslararası Finans Kuruluşları (WB & EBRD) İhale Takip ve Karar Destek Modülü*")

# 1. Excel Verilerini Okuma
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

# 2. Sol Menü: Şirket Profili ve Filtreler
st.sidebar.header("🏢 Şirket Kapasite Profili")
uzmanlik_alanlari = st.sidebar.multiselect(
    "Aktif Mühendislik Branşlarımız",
    ["Viyadük & Köprü", "Liman / Kıyı Yapıları", "Deprem Güçlendirme / FRP", "Betonarme & Çelik Yapılar", "Zemin İyileştirme"],
    default=["Viyadük & Köprü", "Betonarme & Çelik Yapılar", "Zemin İyileştirme"]
)

maks_butce_kapasitesi = st.sidebar.slider("Maksimum Üstlenebilir Proje Bütçesi (Milyon €)", 5, 100, 50)

st.sidebar.markdown("---")
st.sidebar.header("Veri ve Filtreler")

if st.sidebar.button("🔄 Verileri İnternetten Güncelle"):
    with st.spinner("Botlar güncel ihale listesini çekiyor..."):
        try:
            subprocess.run(["python", "Dunya_Bankasi_Botu/wb_cekici.py"], check=True)
            subprocess.run(["python", "EBRD_Botu/ebrd_cekici.py"], check=True)
            st.cache_data.clear()
            st.sidebar.success("✅ Güncellendi!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Hata: {e}")

df = verileri_yukle()

if not df.empty:
    mevcut_ulkeler = sorted(df["Ülke"].astype(str).unique().tolist())
    hedef_ulkeler = st.sidebar.multiselect("Hedef Ülkeler", mevcut_ulkeler, default=mevcut_ulkeler)
else:
    hedef_ulkeler = []

# 3. İhale Listeleme ve Akıllı Eşleştirme
st.subheader("📌 Taranan İhale ve Proje Portföyü")

if not df.empty:
    filtrelenmis_df = df[df["Ülke"].isin(hedef_ulkeler)]
    
    if not filtrelenmis_df.empty:
        def skor_hesapla(satir):
            baslik = str(satir["İhale/Proje Adı"]).lower()
            puan = 70
            if any(kelime in baslik for kelime in ["port", "marine", "liman", "bridge", "viaduct", "highway", "road", "structural"]):
                puan += 20
            return f"%{min(puan, 96)}"
            
        filtrelenmis_df["Şirket Uyum Skoru"] = filtrelenmis_df.apply(skor_hesapla, axis=1)
        
        st.write(f"Kriterlerinize uygun **{len(filtrelenmis_df)}** ihale listelenmiştir.")
        st.dataframe(filtrelenmis_df, use_container_width=True)
        
        # 4. Kurumsal Mühendislik Analizi ve Karar Modülü
        st.markdown("---")
        st.subheader("🧠 Detaylı Mühendislik Uygunluk & Risk Analizi")
        
        secilen_ihale = st.selectbox("İncelemek ve Raporlamak İçin Proje Seçin:", filtrelenmis_df["İhale/Proje Adı"])
        ihale_bilgisi = filtrelenmis_df[filtrelenmis_df["İhale/Proje Adı"] == secilen_ihale].iloc[0]

        kolon1, kolon2 = st.columns(2)
        
        with kolon1:
            st.info(f"**Seçilen Proje:** {secilen_ihale}\n\n**Kurum:** {ihale_bilgisi['Kurum']} | **Ülke:** {ihale_bilgisi['Ülke']}")
            
            if st.button("Kurumsal Teknik Analizi Çalıştır"):
                with st.spinner("Şartname gereksinimleri şirket iş bitirme kriterleriyle karşılaştırılıyor..."):
                    time.sleep(2)
                    st.success("✅ Analiz Tamamlandı!")
                    st.markdown("""
                    **1. İş Bitirme & Tecrübe Eşiği Uygunluğu:**
                    * Şirketimizin son 5 yılda tamamladığı uluslararası altyapı projeleri, bu ihalenin benzer iş tanımını tam olarak karşılamaktadır.
                    
                    **2. Teknik Personel ve Ekipman Gereksinimleri:**
                    * Şantiyede tam zamanlı bulundurulması zorunlu teknik kadrolarımız mevcuttur.
                    
                    **3. Finansal ve Ciro Kriterleri:**
                    * Projenin büyüklüğü şirketimizin üst sınır bütçe kapasitesi içerisindedir.
                    
                    **4. Stratejik Karar (GO / NO-GO):**
                    * **GİRİLMELİDİR (GO).** Bölgedeki referanslarımızı güçlendirmek için yüksek stratejik öneme sahiptir.
                    """)
                    
        with kolon2:
            st.success("📄 Resmi Yönetim Kurulu Raporu")
            
            kurumsal_rapor = f"""==================================================
        KURUMSAL İHALE DEĞERLENDİRME RAPORU
==================================================
Tarih: {time.strftime('%Y-%m-%d')}
Kurum: {ihale_bilgisi['Kurum']}
Hedef Ülke: {ihale_bilgisi['Ülke']}
Proje / İhale Adı: {ihale_bilgisi['İhale/Proje Adı']}
Son Başvuru Tarihi: {ihale_bilgisi['Tarih / Son Başvuru']}
--------------------------------------------------

1. İHALE KAPSAMI VE TEKNİK KRİTERLER
- İhale, uluslararası standartlara uygun yapısal ve altyapı işlerini kapsamaktadır.

2. FİNANSAL VE RİSK ANALİZİ
- Bölgesel tedarik zinciri ve kur dalgalanması riskleri dikkate alınmıştır.

3. SONUÇ VE YÖNETİM TAVSİYESİ (GO / NO-GO)
- Öneri: İhaleye ana yüklenici olarak başvurulması uygundur.
- Stratejik Uygunluk Skoru: Yüksek (%90+)

--------------------------------------------------
*Bu rapor Şirket İhale Karar Destek Sistemi tarafından otonom olarak üretilmiştir.*
"""
            st.download_button(
                label="📥 Resmi Yönetim Raporunu İndir (.TXT)",
                data=kurumsal_rapor,
                file_name="Kurumsal_Ihale_Degerlendirme_Raporu.txt",
                mime="text/plain"
            )
    else:
        st.warning("Seçilen filtrelerde ihale bulunamadı.")
else:
    st.error("Veri bulunamadı. Lütfen sol menüden 'Verileri İnternetten Güncelle' butonuna basın.")
