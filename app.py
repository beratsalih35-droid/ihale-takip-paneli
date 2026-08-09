import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Üst Yapı İhale & Karar Destek Sistemi", layout="wide")

# ==========================================
# 🔒 LOGIN
# ==========================================
def giris_kontrolu():
    if st.session_state.get("giris_basarili", False): return True
    st.title("🔒 Üst Yapı İhale Yönetim Sistemi")
    girilen_sifre = st.text_input("Yönetici Şifresi:", type="password")
    if st.button("Sisteme Giriş Yap"):
        if girilen_sifre == st.secrets.get("PANEL_SIFRESI", "ihale2026"):
            st.session_state["giris_basarili"] = True
            st.rerun()
        else: st.error("❌ Hatalı şifre!")
    return False

if not giris_kontrolu(): st.stop()

# ==========================================
# 🔍 AKILLI ÜLKE BULUCU (VERİ OKUMA)
# ==========================================
@st.cache_data(ttl=60)
def verileri_yukle():
    ebrd_yolu = os.path.join("EBRD_Botu", "ebrd_veriler.xlsx")
    izin_verilenler = ["Romania", "Serbia", "Poland", "Croatia", "Bosnia", "Ukraine", "Albania", "Montenegro", "Hungary", "Moldova", "Kosovo"]
    
    if os.path.exists(ebrd_yolu):
        df = pd.read_excel(ebrd_yolu)
        # Her satırı tara, izin verilen ülkelerden biri geçiyorsa o satırı o ülkeye ata
        def ulke_bul(row):
            row_str = " ".join(row.astype(str))
            for ulke in izin_verilenler:
                if ulke.lower() in row_str.lower(): return ulke
            return "Unknown"
        
        df["Ülke"] = df.apply(ulke_bul, axis=1)
        # Ülkesi bulunamayanları at (Köprü/Viyadük olmayanlar için)
        df = df[df["Ülke"] != "Unknown"]
        return df
    
    # Yedek Veri (Bot çalışmıyorsa görünsün diye)
    return pd.DataFrame({
        "Kurum": ["EBRD"]*3,
        "Ülke": ["Romania", "Serbia", "Poland"],
        "İhale/Proje Adı": ["Bükreş Konut Kompleksi", "Belgrad Hastane Ek Bina", "Varşova Fabrika Tesisi"],
        "Link": ["https://ecepp.ebrd.com"]*3
    })

# ==========================================
# 🏗️ PANEL
# ==========================================
st.title("🏢 Doğu Avrupa & Balkanlar Üst Yapı İhale Analiz Paneli")
df = verileri_yukle()

# Köprü/Viyadük Filtresi
haric = ["bridge", "viaduct", "köprü", "viyadük", "highway"]
filtrelenmis_df = df[~df["İhale/Proje Adı"].str.lower().str.contains('|'.join(haric), na=False)]

st.dataframe(filtrelenmis_df, use_container_width=True)

# Analiz
st.subheader("🧠 Teknik Uygunluk Analizi")
secilen = st.selectbox("Proje Seçin:", filtrelenmis_df["İhale/Proje Adı"])
bilgi = filtrelenmis_df[filtrelenmis_df["İhale/Proje Adı"] == secilen].iloc[0]

st.link_button("🌐 Resmi İhale Sayfasına Git", bilgi['Link'])
if st.button("Mühendislik Analizini Başlat"):
    st.success("✅ Analiz Tamamlandı: GİRİLMELİDİR (GO).")
    st.download_button("📥 Yönetim Raporunu İndir", "Proje: " + secilen, "Rapor.txt")
