import os
import time
import pandas as pd
import google.generativeai as genai

# Datasetlerin ham halinde bölümler ile ilgili açıklama olmadığından gemini a sorgu atılarak 4 dataset için de açıklama eklenmiştir
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

df = pd.read_csv(csv_path)

if "Aciklama" not in df.columns:
    df["Aciklama"] = ""

unique_bolumler = df["bolum_adi"].unique()

try:
    for bolum in unique_bolumler:
        mevcut = df.loc[df["bolum_adi"] == bolum, "Aciklama"]
        if mevcut.notna().any() and mevcut.astype(str).str.strip().any():
            continue  
        try:
            aciklama = generate_description(bolum)
            df.loc[df["bolum_adi"] == bolum, "Aciklama"] = aciklama
            print(f"{bolum} -> {aciklama}")
        except Exception as e:
            print(f"Hata: {bolum} -> {e}")
            df.loc[df["bolum_adi"] == bolum, "Aciklama"] = ""

        time.sleep(5)  

finally:
    # 4. Aynı dosyanın üzerine yazılmıştır
    df.to_csv(csv_path, index=False)
    print(f" Güncel CSV kaydedildi: {csv_path}")
