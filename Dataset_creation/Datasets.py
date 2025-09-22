## Bu Kod pdf şeklinde bulduğumuz datamızı pdften okuyarak csv ye aktarmak için kullanılmıştır 
# csv oluşturulduktan sonra data temizleme dataiku uygulamasında yapılmıştır


import pdfplumber
import pandas as pd
import unicodedata
import os

pdf_path = "/Users/ardaerdegirmenci/Desktop/Pupilica/2025_YKS_Genel_Kontenjan_EA_Taban_Puanlari_ve_Siralari.pdf"

def fix_turkish_chars(text):
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFC", text)  
    replacements = {
        "ç": "ç", "ğ": "ğ", "ö": "ö", "ü": "ü", "ş": "ş", "ı": "ı",
        "Ç": "Ç", "Ğ": "Ğ", "Ö": "Ö", "Ü": "Ü", "Ş": "Ş", "İ": "İ"
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text

rows = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            for row in table:
                rows.append([fix_turkish_chars(cell) if cell else "" for cell in row])

rows = [row for row in rows if any(cell.strip() for cell in row)]

df = pd.DataFrame(rows)

output_path = os.path.expanduser("/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/Dataset_creation/Esit_Agirlik_Bolumler_Ham.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ Temiz tablo kaydedildi: {output_path}")
print(df.head())




