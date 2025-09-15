import json
import random
from typing import List, Dict, Any

class TrainingDataGenerator:
    def __init__(self):
        self.ranking_ranges = [
            (50000, 150000),   # Yüksek performans hedefleyenler
            (150000, 300000),  # Orta-üst performans
            (300000, 500000),  # Orta performans
            (500000, 700000),  # Orta-alt performans
            (700000, 1000000), # Düşük performans
        ]
        
        # İlgi alanı çeşitlendirmesi için alternatif ifadeler
        self.interest_variations = {
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım', 'dijital teknoloji', 'IT'],
            'sağlık': ['sağlık', 'tıp', 'hasta bakımı', 'sağlık hizmetleri', 'medikal'],
            'sanat': ['sanat', 'tasarım', 'yaratıcılık', 'estetik', 'görsel sanatlar'],
            'matematik': ['matematik', 'hesaplama', 'sayısal analiz', 'matematiksel düşünce'],
            'iletişim': ['iletişim', 'sosyal beceiler', 'insan ilişkileri', 'medya'],
            'spor': ['spor', 'fiziksel aktivite', 'atletizm', 'fitness'],
            'doğa': ['doğa', 'çevre', 'tarım', 'ekoloji', 'yeşil teknoloji'],
            'güvenlik': ['güvenlik', 'koruma', 'emniyet', 'kurtarma operasyonları'],
            'işletme': ['işletme', 'yönetim', 'ekonomi', 'ticaret', 'girişimcilik'],
            'mühendislik': ['mühendislik', 'teknik bilim', 'proje yönetimi', 'sistem tasarımı']
        }

    def load_extracted_data(self, file_path: str) -> List[Dict]:
        """Keyword extractor'dan çıkan veriyi yükle"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_interest_variations(self, interests: List[str]) -> List[str]:
        """İlgi alanlarını farklı şekillerde ifade et"""
        varied_interests = []
        for interest in interests:
            if interest in self.interest_variations:
                variations = self.interest_variations[interest]
                varied_interests.append(random.choice(variations))
            else:
                varied_interests.append(interest)
        return varied_interests

    def is_ranking_match(self, dept_ranking: str, target_min: int, target_max: int) -> bool:
        """Bölüm sıralaması hedef aralıkta mı kontrol et"""
        try:
            ranking = float(str(dept_ranking).replace(',', '.'))
            return target_min <= ranking <= target_max
        except (ValueError, TypeError):
            return False

    def create_training_sample(self, department: Dict, target_range: tuple) -> Dict:
        """Tek bir training sample oluştur"""
        target_min, target_max = target_range
        
        # İlgi alanlarını çeşitlendir
        varied_interests = self.generate_interest_variations(department['interests'])
        
        # Hedef sıralamanın ortasını al
        target_ranking = (target_min + target_max) // 2
        
        # Input oluştur
        interests_str = ', '.join(varied_interests)
        input_text = f"İlgi alanlarım: {interests_str}. YKS sıralaması: {target_ranking}"
        
        # Output oluştur
        ranking = department['ranking_2025']
        output_text = f"{department['bolum_adi']} - {department['universite']} (Sıralama: {ranking})"
        
        return {
            "input": input_text,
            "output": output_text,
            "metadata": {
                "department": department['bolum_adi'],
                "university": department['universite'],
                "city": department['sehir'],
                "actual_ranking": ranking,
                "target_range": f"{target_min}-{target_max}",
                "interests": department['interests']
            }
        }

    def generate_training_data(self, extracted_data: List[Dict]) -> List[Dict]:
        """Ana training data generation fonksiyonu"""
        training_samples = []
        
        for target_range in self.ranking_ranges:
            target_min, target_max = target_range
            
            # Bu sıralama aralığına uyan bölümleri bul
            matching_departments = [
                dept for dept in extracted_data 
                if self.is_ranking_match(dept['ranking_2025'], target_min, target_max)
                and dept['interests']  # İlgi alanı boş olmayanlar
            ]
            
            print(f"Sıralama aralığı {target_min}-{target_max}: {len(matching_departments)} bölüm")
            
            # Her uygun bölüm için training sample oluştur
            for dept in matching_departments:
                # Her bölüm için 2-3 farklı varyasyon oluştur
                for _ in range(random.randint(2, 3)):
                    sample = self.create_training_sample(dept, target_range)
                    training_samples.append(sample)
        
        # Training data'yı karıştır
        random.shuffle(training_samples)
        return training_samples

    def create_validation_data(self, training_data: List[Dict], split_ratio: float = 0.2) -> tuple:
        """Training ve validation setlerini ayır"""
    
        # Stratified split yaparak her label'dan hem train hem val'de bulunmasını sağla
        from collections import defaultdict
    
        # Label'lara göre grupla
        label_groups = defaultdict(list)
        for item in training_data:
            label_groups[item['output']].append(item)
    
        train_data = []
        val_data = []
    
        # Her label'dan en az 1 tane train'de kalsın
        for label, items in label_groups.items():
            if len(items) == 1:
                train_data.extend(items)  # Tek örnek varsa train'e koy
            else:
                split_idx = max(1, int(len(items) * (1 - split_ratio)))
                train_data.extend(items[:split_idx])
                val_data.extend(items[split_idx:])
    
        return train_data, val_data

    def save_training_data(self, training_data: List[Dict], output_path: str):
        """Training data'yı kaydet"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Training data saved: {output_path}")
        print(f"📊 Total samples: {len(training_data)}")

    def generate_statistics(self, training_data: List[Dict]):
        """Training data istatistiklerini göster"""
        print("\n📈 TRAINING DATA İSTATİSTİKLERİ:")
        print(f"Toplam sample sayısı: {len(training_data)}")
        
        # Sıralama aralıklarına göre dağılım
        range_distribution = {}
        for sample in training_data:
            target_range = sample['metadata']['target_range']
            range_distribution[target_range] = range_distribution.get(target_range, 0) + 1
        
        print("\n🎯 Sıralama Aralığı Dağılımı:")
        for range_key, count in sorted(range_distribution.items()):
            print(f"  {range_key}: {count} samples")
        
        # İlgi alanı dağılımı
        interest_count = {}
        for sample in training_data:
            for interest in sample['metadata']['interests']:
                interest_count[interest] = interest_count.get(interest, 0) + 1
        
        print("\n🎨 İlgi Alanı Dağılımı:")
        for interest, count in sorted(interest_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {interest}: {count} samples")

    def show_sample_examples(self, training_data: List[Dict], num_examples: int = 5):
        """Örnek training sample'larını göster"""
        print(f"\n📋 ÖRNEK TRAINING SAMPLES ({num_examples} adet):")
        
        for i, sample in enumerate(training_data[:num_examples]):
            print(f"\n{i+1}. SAMPLE:")
            print(f"   INPUT:  {sample['input']}")
            print(f"   OUTPUT: {sample['output']}")

def main():
    generator = TrainingDataGenerator()
    
    # Keyword extractor'dan veriyi yükle
    print("📂 Extracted keywords loading...")
    extracted_data = generator.load_extracted_data('/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/Dataset_creation/Datasets/extracted_keywords.json')
    print(f"✅ {len(extracted_data)} bölüm yüklendi")
    
    # Training data oluştur
    print("\n🤖 Training data generation başlıyor...")
    training_data = generator.generate_training_data(extracted_data)
    
    # Train/validation split
    train_data, val_data = generator.create_validation_data(training_data)
    
    # Dosyaları kaydet
    generator.save_training_data(train_data, '/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/model_training/model_datasets/train_data.json')
    generator.save_training_data(val_data, '/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/model_training/model_datasets/val_data.json')
    generator.save_training_data(training_data, '/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/model_training/model_datasets/ful_training_data.json')
    
    # İstatistikler ve örnekler
    generator.generate_statistics(training_data)
    generator.show_sample_examples(training_data)
    
    print(f"\n🎉 Training data generation tamamlandı!")
    print(f"📊 Train samples: {len(train_data)}")
    print(f"📊 Validation samples: {len(val_data)}")

if __name__ == "__main__":
    main()