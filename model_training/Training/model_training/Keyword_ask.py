import google.generativeai as genai
import pandas as pd
import json

def ask_gemini_for_keywords():
    """Gemini'ye keyword sistemi oluşturmasını sor"""
    
    # API key'ini buraya koy
    GEMINI_API_KEY = "# Buraya kendi API key"  
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Önce mevcut modelleri listele
    try:
        print("📋 Mevcut modeller:")
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                print(f"  - {model_info.name}")
    except Exception as e:
        print(f"Model listesi alınamadı: {e}")
    
    # Yeni model isimleri dene
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ gemini-1.5-flash kullanılıyor")
    except:
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ gemini-1.5-pro kullanılıyor")
        except:
            try:
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                print("✅ gemini-1.5-flash-latest kullanılıyor")
            except Exception as e:
                print(f"❌ Hiçbir model bulunamadı: {e}")
                return None
    
    # Veri setlerinden örnek bölümler çıkar
    try:
        # 2 yıllık bölümler dataseti
        df = pd.read_csv('2yillik_Bolumler_aciklamali_yeni.csv')
        
        # En sık geçen bölüm türlerini bul
        dept_counts = df['bolum_adi'].str.upper().value_counts().head(20)
        
        sample_depts = "\n".join([f"- {dept} ({count} bölüm)" for dept, count in dept_counts.items()])
        
    except:
        # Eğer dosya yoksa manuel örnek ver
        sample_depts = """
- BILGISAYAR PROGRAMCILIĞI (450 bölüm)
- GRAFİK TASARIMI (340 bölüm)
- HEMŞIRELIK (280 bölüm)
- SPOR YÖNETICILIĞİ (89 bölüm)
- PAZARLAMA (445 bölüm)
- MUHASEBE VE VERGİ UYGULAMALARI (380 bölüm)
- WEB TASARIMI VE KODLAMA (120 bölüm)
- FOTOĞRAFÇILIK VE KAMERAMANLIK (95 bölüm)
- ANESTEZİ (67 bölüm)
- REKREASYON YÖNETİMİ (45 bölüm)
- E-TİCARET VE PAZARLAMA (78 bölüm)
- OYUN GELİŞTİRME VE PROGRAMLAMA (23 bölüm)
- GASTRONOMI VE MUTFAK SANATLARI (156 bölüm)
- ANTRENÖRLÜK EĞİTİMİ (34 bölüm)
- TIBBİ TANITIM VE PAZARLAMA (67 bölüm)
"""
    
    prompt = f"""
Bu Türkiye üniversite bölümleri için keyword sistemi oluştur:

BÖLÜM ÖRNEKLERİ:
{sample_depts}

Python dictionary formatında ver:

# POZİTİF - kullanıcının ilgisini artıran kelimeler
positive_mappings = {{
    'teknoloji': ['bilgisayar', 'yazılım', 'programlama', 'web', 'oyun', 'dijital', 'sistem', 'kodlama'],
    'sağlık': ['sağlık', 'tıp', 'hemşire', 'hasta', 'tedavi', 'anestezi', 'veteriner', 'diş'],
    'sanat': ['sanat', 'tasarım', 'grafik', 'müzik', 'sinema', 'fotoğraf', 'görsel', 'yaratıcı'],
    'spor': ['spor', 'antrenör', 'fitness', 'egzersiz', 'rekreasyon', 'beden', 'atletik', 'hareket'],
    'işletme': ['işletme', 'pazarlama', 'muhasebe', 'ticaret', 'yönetim', 'ekonomi', 'finans', 'satış'],
    'eğitim': ['öğretmen', 'eğitim', 'öğretim', 'ders', 'okul', 'çocuk', 'akademik', 'öğrenci']
}}

# NEGATİF - kullanıcının kaçındığı kelimeler (basit kelimeler)
negative_keywords = {{
    'teknoloji': ['teknoloji', 'bilgisayar', 'matematik', 'sayısal', 'programlama', 'kodlama'],
    'sağlık': ['sağlık', 'hasta', 'kan', 'tıp', 'ameliyat', 'hastalık'],
    'matematik': ['matematik', 'hesap', 'sayı', 'formül', 'problem', 'çözüm'],
    'sosyal': ['tarih', 'edebiyat', 'ezber', 'okuma', 'yazma', 'analiz']
    'spor' : ['tembel']
    'işletme' : ['']
    'eğitim' : ['']
}}

Sadece bu iki dictionary'yi ver, başka hiçbir şey yazma."""
    
    try:
        print("🤖 Gemini'ye soruyor...")
        response = model.generate_content(prompt)
        
        print("✅ Gemini'den cevap alındı!")
        print("="*80)
        print(response.text)
        print("="*80)
        
        # Sonucu dosyaya kaydet
        with open('gemini_keywords.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("💾 Sonuç 'gemini_keywords.txt' dosyasına kaydedildi")
        print("📋 Bu kodları kopyalayıp:")
        print("  1. positive_mappings'i expanded_mappings yerine koy") 
        print("  2. negative_keywords'i filter_keywords kısmında kullan")
        
        return response.text
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        print("🔑 API key'ini kontrol et veya Gemini API'yi aktif et")
        return None

if __name__ == "__main__":
    ask_gemini_for_keywords()