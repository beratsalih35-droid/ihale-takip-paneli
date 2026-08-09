# Dunya_Bankasi_Botu/wb_cekici.py
import requests
import pandas as pd
import os

print("🌐 Dünya Bankası sistemine bağlanılıyor...")
url = "https://search.worldbank.org/api/v2/projects?format=json&rows=15"

try:
    cevap = requests.get(url)
    
    if cevap.status_code == 200:
        ham_veri = cevap.json()
        proje_listesi = []
        
        if "projects" in ham_veri:
            for anahtar, proje in ham_veri["projects"].items():
                if type(proje) == dict and "project_name" in proje:
                    baslik = proje.get("project_name", "Başlık Yok")
                    ulke = proje.get("countryshortname", "Belirtilmemiş")
                    tarih = proje.get("boardapprovaldate", "Belirtilmemiş")
                    
                    proje_listesi.append({
                        "Kurum": "World Bank",
                        "Ülke": ulke,
                        "İhale/Proje Adı": baslik,
                        "Tarih": tarih
                    })
        
        df = pd.DataFrame(proje_listesi)
        
        # Dosyanın doğru klasöre kaydedilmesi için yol belirliyoruz
        kayit_yolu = os.path.join(os.path.dirname(__file__), "wb_veriler.xlsx")
        df.to_excel(kayit_yolu, index=False)
        
        print(f"✅ Başarılı! Toplam {len(proje_listesi)} Dünya Bankası projesi çekildi.")
        print(f"📂 Veriler şuraya kaydedildi: {kayit_yolu}")
        
    else:
        print("❌ Siteye ulaşılamadı. Hata Kodu:", cevap.status_code)

except Exception as e:
    print("Sistemsel bir hata oluştu:", e)