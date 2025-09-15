import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class KeywordExtractor:
    def __init__(self):
        # Turkish stopwords
        self.stopwords = set([
            've', 'bir', 'bu', 'da', 'de', 'için', 'ile', 'olan', 'olarak', 
            'sonra', 'sonrası', 'mezuniyet', 'program', 'programı', 'bölüm',
            'alan', 'alanında', 'konusunda', 'hakkında', 'gibi', 'kadar',
            'çalışma', 'çalışır', 'öğrenci', 'öğrenciler', 'ders', 'dersler'
        ])
        
        # Interest area mappings
        self.interest_keywords = {
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım', 'dijital', 'elektronik', 'otomasyon', 'robot'],
            'sanat': ['sanat', 'tasarım', 'yaratıcı', 'estetik', 'görsel', 'grafik', 'müzik'],
            'sağlık': ['sağlık', 'hasta', 'tedavi', 'tıp', 'ameliyat', 'bakım', 'hemşire', 'doktor'],
            'matematik': ['matematik', 'hesap', 'analiz', 'istatistik', 'sayısal', 'formül'],
            'iletişim': ['iletişim', 'sosyal', 'insan', 'toplum', 'dil', 'konuşma', 'medya'],
            'spor': ['spor', 'fitness', 'antrenör', 'egzersiz', 'hareket', 'atletik'],
            'doğa': ['tarım', 'çevre', 'doğa', 'bitki', 'hayvan', 'ekoloji', 'orman'],
            'güvenlik': ['güvenlik', 'polis', 'askeriye', 'koruma', 'emniyet', 'kurtarma'],
            'işletme': ['işletme', 'yönetim', 'ekonomi', 'ticaret', 'pazarlama', 'satış'],
            'mühendislik': ['mühendislik', 'teknik', 'proje', 'inşaat', 'yapı', 'sistem']
        }
    
    def clean_text(self, text):
        """Metni temizle ve normalize et"""
        if not text or text == '-':
            return ""
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Özel karakterleri temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Çoklu boşlukları tek boşluğa çevir
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords_from_description(self, description):
        """Açıklamadan keywords çıkar"""
        cleaned = self.clean_text(description)
        if not cleaned:
            return []
        

        words = cleaned.split()
        
        # Stopwords'leri filtrele ve 2+ karakter olanları al
        keywords = [word for word in words 
                   if word not in self.stopwords and len(word) > 2]
        
        return keywords
    
    def map_to_interests(self, keywords):
        """Keywords'leri ilgi alanlarına map et"""
        interests = []
        keyword_str = ' '.join(keywords)
        
        for interest, interest_keywords in self.interest_keywords.items():
            for keyword in interest_keywords:
                if keyword in keyword_str:
                    interests.append(interest)
                    break
        
        return list(set(interests))  # Unique interests
    
    def categorize_by_ranking(self, ranking):
        """Sıralamaya göre zorluk kategorisi"""
        if not ranking or ranking == '-':
            return 'unknown'
        
        try:
            rank = float(str(ranking).replace(',', '.'))
            if rank < 100000:
                return 'zor'
            elif rank < 400000:
                return 'orta'
            else:
                return 'kolay'
        except:
            return 'unknown'
    
    def process_dataset(self, csv_path):
        """Dataset'i işle ve training data hazırla"""
        df = pd.read_csv(csv_path)
        
        training_data = []
        
        # Unique bölümleri al
        unique_departments = df.drop_duplicates(subset=['bolum_adi'])
        
        for _, row in unique_departments.iterrows():
            # Keywords çıkar
            keywords = self.extract_keywords_from_description(row['Aciklama'])
            interests = self.map_to_interests(keywords)
            
            if not interests:  # İlgi alanı bulunamazsa skip
                continue
            
           # YENİ KOD:
            ranking_2025 = row.get('2025_Taban_Sıralama', 0)

# Training data oluştur
            training_sample = {
                'bolum_adi': row['bolum_adi'],
                'interests': interests,
                'keywords': keywords[:10],
                'ranking_2025': ranking_2025,
                'universite': row.get('Universite', ''),
                'sehir': row.get('Sehir', ''),
                'description': row['Aciklama'][:200] + '...' if len(str(row['Aciklama'])) > 200 else row['Aciklama']
            }
            
            training_data.append(training_sample)
        
        return training_data
    
    def save_training_data(self, training_data, output_path):
        """Training data'yı JSON olarak kaydet"""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Training data saved: {output_path}")
        print(f"📊 Total samples: {len(training_data)}")

# Kullanım örneği
if __name__ == "__main__":
    extractor = KeywordExtractor()
    
    # Dataset'i işle
    training_data = extractor.process_dataset('/Users/ardaerdegirmenci/Desktop/Pupilica/kuzular/Dataset_creation/Datasets/2yillik_Bolumler_aciklamali_yeni.csv')
    
    # Sonuçları kaydet
    extractor.save_training_data(training_data, '/Users/ardaerdegirmenci/Desktop/Pupilica/kuzular/Dataset_creation/Datasets/extracted_keywords.json')
    
    # Örnek sonuçları göster
    print("\n📋 Sample Results:")
    for i, sample in enumerate(training_data[:5]):
        print(f"\n{i+1}. {sample['bolum_adi']}")
        print(f"   İlgi Alanları: {sample['interests']}")
        print(f"   Keywords: {sample['keywords'][:5]}")
