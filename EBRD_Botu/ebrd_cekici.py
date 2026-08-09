# EBRD_Botu/ebrd_cekici.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

print("🌐 EBRD ECEPP (Avrupa Kalkınma Bankası) sistemine bağlanılıyor...")
url = "https://ecepp.ebrd.com/delta/noticeSearchResults.html"

# ÇÖZÜM BURADA: Botumuza normal bir insan/tarayıcı kimliği veriyoruz
kimlik_karti = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    # Siteye giderken bu kimlik kartını (headers) gösteriyoruz
    cevap = requests.get(url, headers=kimlik_karti)
    
    if cevap.status_code == 200:
        soup = BeautifulSoup(cevap.content, "lxml")
        ihale_listesi = []
        
        satirlar = soup.find_all("tr")
        
        for satir in satirlar:
            hucreler = satir.find_all("td")
            if len(hucreler) >= 4:
                ihale_no = hucreler[0].text.strip()
                ulke = hucreler[1].text.strip()
                proje_adi = hucreler[2].text.strip()
                tarih = hucreler[3].text.strip()
                
                if proje_adi and ulke:
                    ihale_listesi.append({
                        "Kurum": "EBRD",
                        "Ülke": ulke,
                        "İhale/Proje Adı": proje_adi,
                        "Son Başvuru / Tarih": tarih
                    })
        
        if len(ihale_listesi) > 0:
            df = pd.DataFrame(ihale_listesi)
            
            kayit_yolu = os.path.join(os.path.dirname(__file__), "ebrd_veriler.xlsx")
            df.to_excel(kayit_yolu, index=False)
            
            print(f"✅ Başarılı! ECEPP sayfasından {len(ihale_listesi)} EBRD ihale verisi çekildi.")
            print(f"📂 Veriler şuraya kaydedildi: {kayit_yolu}")
        else:
            print("⚠️ Siteye başarıyla girildi ancak ihale tablosu bulunamadı. HTML tasarımı farklı olabilir.")
            
    else:
        print(f"❌ Siteye ulaşılamadı. Hata Kodu: {cevap.status_code}")

except Exception as e:
    print("Sistemsel bir hata oluştu:", e)