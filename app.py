import streamlit as st
import pandas as pd
import os
import time
import subprocess

st.set_page_config(page_title="İhale Takip & Analiz Sistemi", layout="wide")

# ==========================================
# 🔒 GÜVENLİK DUVARI (LOGIN) BÖLÜMÜ
# ==========================================
def giris_kontrolu():
    # Eğer daha önce doğru şifre girildiyse sistemi aç
    if st.session_state.get("giris_basarili", False):
        return True
        
    # Girilmediyse kilit ekranını göster
    st.title("🔒 Yalnızca Yetkili Personel")
    st.info("Bu panele erişim şirket yönetimi ile sınırlandırılmıştır.")
    
    girilen_sifre = st.text_input("Lütfen yönetici şifresini girin:", type="password")
    
    if st.button("Giriş Yap"):
        # Şifreyi Streamlit Secrets'tan alıyoruz. Kasada yoksa geçici olarak 'ihale2026' kabul eder.
        dogru_sifre = st.secrets.get("PANEL_SIFRESI", "ihale2026")
        
        if girilen_sifre == dogru_sifre:
            st.session_state["giris_basarili"] = True
            st.rerun() # Sayfayı yenile ve paneli aç
        else:
            st.error("❌ Hatalı şifre! Lütfen tekrar deneyin.")
            
    return False

# Eğer giriş yapılmadıysa, kodun alt kısmını ÇALIŞTIRMA ve burada dur!
if not giris_kontrolu():
    st.stop()
# ==========================================


# --- BURADAN SONRASI İHALE PANELİ KODLARIDIR ---
st.title("🏗️ Doğu Avrupa İhale Takip ve Raporlama Paneli")

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

st.subheader("📌 Güncel İhaleler ve Projeler")

if not df.empty:
    filtrelenmis_df = df[df["Ülke"].isin(hedef_ulkeler)]
    
    if not filtrelenmis_df.empty:
        st.write(f"Seçili kriterlere uygun **{len(filtrelenmis_df)}** proje listeleniyor.")
        st.dataframe(filtrelenmis_df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🧠 Teknik Uygunluk Analizi ve Raporlama")
        
        secilen_ihale = st.selectbox("Analiz edilecek ve raporlanacak ihaleyi seçin:", filtrelenmis_df["İhale/Proje Adı"])
        ihale_bilgisi = filtrelenmis_df[filtrelenmis_df["İhale/Proje Adı"] == secilen_ihale].iloc[0]

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
            st.download_button(
                label="📥 Üst Yönetim Raporunu İndir (TXT)",
                data=rapor_metni,
                file_name="Yonetici_Ozeti.txt",
                mime="text/plain"
            )
    else:
        st.warning("Seçili ülkeler için ihale bulunamadı. Lütfen sol menüden farklı ülkeler seçin.")
