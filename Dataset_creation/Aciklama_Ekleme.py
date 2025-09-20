import os
import time
import pandas as pd
import google.generativeai as genai

# 🔑 API Key
genai.configure(api_key="apı key gelecek")

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_description(bolum):
    prompt = f"""
    '{bolum}' isimli 4 yıllık eşit ağırlık puanı ile girilen üniversite bölümü için kısa ve net bir açıklama yaz.
    İçermeli:
    - Öğrencinin ne öğrenebileceği
    - Mezuniyet sonrası iş alanları
    - Hangi hobilerle örtüşebileceği
    Açıklama 3-4 cümle olsun.
    """
    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else ""

# -----------------------------
csv_path = "/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/Dataset_creation/Datasets/Esit_Agirlik_Aciklamali.csv"

# 1. CSV oku (virgüllü formatta)
df = pd.read_csv(csv_path)

# Eğer Aciklama sütunu yoksa ekle
if "Aciklama" not in df.columns:
    df["Aciklama"] = ""

# 2. Benzersiz bölümler
unique_bolumler = df["bolum_adi"].unique()

try:
    # 3. Açıklaması olmayanları doldur
    for bolum in unique_bolumler:
        mevcut = df.loc[df["bolum_adi"] == bolum, "Aciklama"]
        if mevcut.notna().any() and mevcut.astype(str).str.strip().any():
            continue  # zaten açıklaması var

        try:
            aciklama = generate_description(bolum)
            df.loc[df["bolum_adi"] == bolum, "Aciklama"] = aciklama
            print(f"{bolum} -> {aciklama}")
        except Exception as e:
            print(f"Hata: {bolum} -> {e}")
            df.loc[df["bolum_adi"] == bolum, "Aciklama"] = ""

        time.sleep(5)  # free tier güvenlik için bekleme

finally:
    # 4. Aynı dosyanın üzerine yaz
    df.to_csv(csv_path, index=False)
    print(f"💾 Güncel CSV kaydedildi: {csv_path}")
