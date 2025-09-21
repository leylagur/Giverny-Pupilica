import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridRecommendationEngine:
    """
    Hybrid model using semantic similarity + rule-based filtering
    """
    
    def __init__(self, dataset_path: str):
        """Initialize the recommendation engine"""
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual model
        self.departments_df = None
        self.department_embeddings = None

        self.load_dataset(dataset_path)
        self.prepare_embeddings()
        
    def load_dataset(self, dataset_path: str):
        """Load department dataset - simple approach with error catching"""
        logger.info(f"Loading dataset from {dataset_path}")

        # Load CSV with ALL columns as string
        df = pd.read_csv(dataset_path, dtype=str)
        
        # Clean and prepare data
        df = df.dropna(subset=['Aciklama', 'bolum_adi'])
        
        # Manual ranking conversion with comprehensive error handling
        rankings = []
        valid_rows = []
        
        for idx, row in df.iterrows():
            ranking_value = row['2025_Taban_Sıralama']
            
            try:
                # Skip if NaN or empty
                if pd.isna(ranking_value) or ranking_value == '':
                    continue
                    
                ranking_str = str(ranking_value).strip()
                
                # Skip any value containing comma
                if ',' in ranking_str:
                    continue
                    
                # Convert clean values
                if '.' in ranking_str:
                    clean_value = ranking_str.replace('.', '')
                else:
                    clean_value = ranking_str
                    
                ranking_int = int(clean_value)
                
                # Add to valid data
                rankings.append(ranking_int)
                valid_rows.append(idx)
                
            except:
                # Skip any problematic row silently
                continue
        
        # Create clean dataframe
        df_clean = df.iloc[valid_rows].copy()
        df_clean['ranking_2025'] = rankings
        df_clean = df_clean.reset_index(drop=True)
        
        self.departments_df = df_clean
        logger.info(f"Loaded {len(df_clean)} clean departments")
        
        if len(rankings) > 0:
            logger.info(f"Ranking range: {min(rankings)} - {max(rankings)}")
        print("CSV'den okunan ilk 5 ranking değeri:")
        print(df['2025_Taban_Sıralama'].head().tolist())
        
        # Manual ranking conversion kısmında da debug ekle:
        print(f"İlk 5 converted ranking: {rankings[:5]}")
        print(f"41 değeri nasıl convert ediliyor: {df[df['2025_Taban_Sıralama']=='41']['2025_Taban_Sıralama'].iloc[0] if len(df[df['2025_Taban_Sıralama']=='41']) > 0 else 'Yok'}")
        
        return df_clean
        
    def prepare_embeddings(self):
        """Create embeddings for all department descriptions"""
        logger.info("Creating embeddings for department descriptions...")
    
        self.departments_df = self.departments_df.reset_index(drop=True)
    
        descriptions = self.departments_df['Aciklama'].tolist()
        self.department_embeddings = self.model.encode(descriptions, show_progress_bar=True)
    
        logger.info("Embeddings created successfully")
    
    def extract_interests_and_ranking(self, user_input: str):
        
        import re
        
        # Enhanced ranking patterns - sadece geçerli formatları kabul et
        ranking_patterns = [
            r'(?:YKS sıralamasi|sıralama|sıralamam):?\s*(\d+(?:\.\d{3})*k?)',
            r'sıralamam\s+(\d+(?:\.\d{3})*k?)',
            r'(\d+)\s*bin',  # "19 bin" yakalamak için
            r'(\d+k?)\s*sıralama',
            r'(\d{1,3}(?:\.\d{3})+)',
            r'(\d{4,7})',
            r'sıralama.*?(\d+(?:\.\d{3})*k?)'
        ]
        
        ranking = None
        for pattern in ranking_patterns:
            ranking_match = re.search(pattern, user_input, re.IGNORECASE)
            if ranking_match:
                rank_str = ranking_match.group(1)
                
                try:
                    # SADECE GEÇERLİ FORMATLARI İŞLE
                    # Virgül içeren formatları IGNORE ET
                    if ',' in rank_str:
                        continue  # Bu formatı atla, sonraki pattern'i dene
                    
                    # Handle 'bin' notation (42 bin = 42000)
                    if 'bin' in user_input.lower() and not 'k' in rank_str:
                        ranking = int(rank_str) * 1000
                    # Handle 'k' notation (32k = 32000)
                    elif 'k' in rank_str.lower():
                        ranking = int(float(rank_str.lower().replace('k', '')) * 1000)
                    elif '.' in rank_str and len(rank_str) > 4:
                        ranking = int(rank_str.replace('.', ''))  # 32.000 -> 32000
                    else:
                        ranking = int(rank_str)
                    
                    # Geçerli ranking bulundu, döngüden çık
                    if ranking:
                        break
                        
                except (ValueError, TypeError):
                    # Bu pattern çalışmazsa sonrakini dene
                    continue
        
        # Extract career intentions and interests using NLP patterns
        interests_keywords = self.extract_career_interests(user_input)
        
        return ', '.join(interests_keywords), ranking
    
    def extract_career_interests(self, text: str):
        """Extract career interests and keywords from natural language with negative filtering"""
        import re
        
        text_lower = text.lower()
        extracted_interests = set()
        excluded_interests = set()  
        
        # Negative patterns - önce bunları kontrol et
        negative_patterns = {
            'teknoloji': [
                r'teknoloji.*?(?:sevmiyorum|istemiyorum|ilgilenmiyorum|olmasın|sevmem|alakalı.*?olsun.*?istemiyorum)',
                r'(?:sevmiyorum|istemiyorum|ilgilenmiyorum|sevmem).*?teknoloji',
                r'teknoloji.*?ile.*?alakalı.*?(?:olsun.*?istemiyorum|istemem)'
            ],
            'sağlık': [
                r'sağlık.*?(?:sevmiyorum|istemiyorum|ilgilenmiyorum|sevmem)',
                r'(?:sevmiyorum|istemiyorum|sevmem).*?sağlık'
            ],
            'matematik': [
                r'matematik.*?(?:sevmiyorum|kötüyüm|zor|sevmem)',
                r'(?:sevmiyorum|kötüyüm|sevmem).*?matematik'
            ]
        }
        
        # Check negative patterns first
        for category, patterns in negative_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    excluded_interests.add(category)
                    break
        
        # Career intention patterns (pozitif)
        career_patterns = {
            'sağlık': [
                r'sağlık.*?(?:sektör|alan|çalış)',
                r'hasta.*?bakım',
                r'tıp.*?alan'
            ],
            'sanat': [
                r'(?:yaratıcı|sanat).*?(?:iş|alan|çalış)',
                r'tasarım.*?(?:yapma|alan)',
                r'görsel.*?(?:sanat|tasarım)'
            ],
            'teknoloji': [
                r'teknoloji.*?(?:sektör|alan|çalış)',
                r'yazılım.*?(?:geliştir|alan)',
                r'bilgisayar.*?(?:program|alan)'
            ],
            'spor': [
                r'spor.*?(?:alan|aktivite|sektör)',
                r'antrenör.*?(?:olma|çalış)'
            ]
        }
        
        # Check positive career patterns
        for category, patterns in career_patterns.items():
            if category not in excluded_interests:  # Sadece exclude edilmemişleri ekle
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        extracted_interests.add(category)
                        break
        
        # Direct keyword matching
        context_keywords = {
            'sağlık': ['sağlık', 'hasta', 'tedavi', 'tıp', 'hemşire'],
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım', 'program'],
            'sanat': ['sanat', 'tasarım', 'yaratıcı', 'görsel', 'grafik'],
            'spor': ['spor', 'fitness', 'antrenör', 'egzersiz']
        }
        
        for category, keywords in context_keywords.items():
            if category not in excluded_interests:  # Exclude edilmemişleri kontrol et
                for keyword in keywords:
                    if keyword in text_lower:
                        extracted_interests.add(category)
                        break
        
        # Return final interests excluding negatives
        final_interests = extracted_interests - excluded_interests
        return list(final_interests) if final_interests else ['genel']
    
    def filter_negative_interests(self, results: list, user_input: str):
        user_lower = user_input.lower()
        
        negative_categories = {
            'mühendislik': ['mühendislik', 'mühendis'],
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım'],
            'sağlık': ['sağlık', 'tıp', 'hemşire', 'diş'],
            'matematik': ['matematik', 'hesap'],
            'spor': ['spor', 'fitness'],
            'işletme': ['işletme', 'pazarlama'],
            'eğitim': ['öğretmen', 'eğitim'],
            'hukuk': ['hukuk', 'avukat'],
            'finans': ['finans', 'banka']
        }
        
        negative_words = ['istemiyorum', 'sevmiyorum', 'sevmem', 'olmasın']
        
        for category, keywords in negative_categories.items():
            for keyword in keywords:
                for neg_word in negative_words:
                    pattern1 = f"{keyword} {neg_word}"
                    pattern2 = f"{neg_word} {keyword}"
                    
                    if pattern1 in user_lower or pattern2 in user_lower:
                        print(f"DEBUG: {category} kategorisi filtreleniyor")
                        results = [r for r in results if not any(kw in self.departments_df.iloc[r['index']]['bolum_adi'].lower() for kw in keywords)]
                        break
        
        return results 
    
    def filter_by_ranking(self, ranking: int, tolerance_percent: float = 0.20):
        """Filter departments by ranking range with percentage-based tolerance"""
        if ranking is None:
            return self.departments_df.index.tolist()
        
        # Yüzde bazlı tolerance hesaplama yapılarak tutarlı sonuç sağlanır
        tolerance_value = int(ranking * tolerance_percent)
        
        min_rank = max(1, ranking - tolerance_value)
        max_rank = ranking + tolerance_value
            
        filtered_indices = self.departments_df[
            (self.departments_df['ranking_2025'] >= min_rank) & 
            (self.departments_df['ranking_2025'] <= max_rank)
        ].index.tolist()
        
        logger.info(f"Ranking: {ranking}, Tolerance: %{tolerance_percent*100} = ±{tolerance_value}")
        logger.info(f"Range: {min_rank} - {max_rank}")
        logger.info(f"Filtered to {len(filtered_indices)} departments")
        return filtered_indices
    
    def compute_semantic_similarity(self, interests: str, candidate_indices: list):
        """Compute semantic similarity between interests and candidate departments"""
        if not interests.strip():
            return []
            
        # Encode user interests
        interest_embedding = self.model.encode([interests])
        
        # Get embeddings for candidate departments
        candidate_embeddings = self.department_embeddings[candidate_indices]
        
        # Compute cosine similarity
        similarities = cosine_similarity(interest_embedding, candidate_embeddings)[0]
        
        # Create results with indices and scores
        results = []
        for i, idx in enumerate(candidate_indices):
            results.append({
                'index': idx,
                'similarity_score': similarities[i]
            })
            
        return results
    
    def boost_keyword_matches(self, interests: str, results: list):
        """Boost scores for exact keyword matches with expanded keywords"""
        interests_lower = interests.lower()
        
        # Genişletilmiş keyword mappings
        expanded_mappings = {
            'teknoloji': ['bilgisayar', 'yazılım', 'programlama', 'web', 'oyun', 'dijital', 'sistem', 'kodlama', 'algoritma', 'veri', 'yapay zeka', 'robotik'],
            'sağlık': ['sağlık', 'tıp', 'hemşire', 'hasta', 'tedavi', 'anestezi', 'veteriner', 'diş', 'fizyoterapi', 'biyoloji', 'eczacılık', 'laboratuvar'],
            'sanat': ['sanat', 'tasarım', 'grafik', 'müzik', 'sinema', 'fotoğraf', 'görsel', 'yaratıcı', 'moda', 'animasyon', 'illüstrasyon', 'estetik'],
            'spor': ['spor', 'antrenör', 'fitness', 'egzersiz', 'rekreasyon', 'beden', 'atletik', 'kondisyon', 'performans', 'müsabaka', 'takım', 'saha'],
            'işletme': ['işletme', 'pazarlama', 'muhasebe', 'ticaret', 'yönetim', 'ekonomi', 'finans', 'satış', 'girişimcilik', 'lojistik', 'insan kaynakları', 'strateji'],
            'gastronomi': ['gastronomi', 'mutfak', 'yemek', 'aşçılık', 'pasta', 'şef', 'fırıncılık', 'gıda', 'restoran', 'menü', 'lezzet', 'sunum'],
            'eğitim': ['öğretmen', 'eğitim', 'öğretim', 'ders', 'okul', 'çocuk', 'akademik', 'öğrenci', 'pedagoji', 'psikoloji', 'rehberlik', 'müfredat'],
            'mühendislik': ['mühendislik', 'mühendis', 'teknik', 'endüstri', 'makina', 'elektrik', 'inşaat', 'çevre', 'proje', 'tasarım', 'analiz', 'yapı'],
            'hukuk': ['hukuk', 'avukat', 'mahkeme', 'dava', 'kanun', 'yasa', 'adalet', 'hâkim', 'savcı', 'anayasa', 'ceza', 'medeni'],
            'finans': ['finans', 'banka', 'borsa', 'yatırım', 'kredi', 'sigorta', 'muhasebe', 'vergi', 'ekonomi', 'para', 'döviz', 'risk'],
            'medya': ['medya', 'gazete', 'televizyon', 'radyo', 'haber', 'basın', 'yayın', 'sosyal medya', 'reklam', 'pazarlama', 'içerik', 'editör'],
            'turizm': ['turizm', 'otel', 'seyahat', 'rehber', 'konaklama', 'resepsiyon', 'acenta', 'rezervasyon', 'müze', 'kültür', 'tatil', 'gezi']
        }
        
        
        all_keywords = set()
        for word in interests_lower.split(','):
            word = word.strip()
            for category, expanded_keywords in expanded_mappings.items():
                if word in expanded_keywords[:3]:
                    all_keywords.update(expanded_keywords)
                    break
        
        # Keyword boost hesapla
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            dept_text = (dept_row['bolum_adi'] + ' ' + dept_row['Aciklama']).lower()
            
            keyword_boost = 0
            for keyword in all_keywords:
                if keyword in dept_text:
                    keyword_boost += 0.1
                    
            result['similarity_score'] += keyword_boost
            result['keyword_boost'] = keyword_boost
            
        return results
    
    def recommend(self, user_input: str, top_k: int = 10, tolerance_percent: float = 0.20):
        """Main recommendation function with percentage-based ranking tolerance"""
        logger.info(f"Processing recommendation for: {user_input}")
        def safe_taban_puan(value):
            if pd.isna(value):
                return None
            try:
                str_val = str(value)
                if ',' in str_val:
                    return None  # Virgüllü değerleri skip et
                return float(str_val.replace('.', ''))
            except:
                return None

        # Parse input
        interests, ranking = self.extract_interests_and_ranking(user_input)
        logger.info(f"Extracted interests: '{interests}', ranking: {ranking}")
        
        # Filter by ranking with percentage tolerance
        candidate_indices = self.filter_by_ranking(ranking, tolerance_percent)
        
        if not candidate_indices:
            return []
            
        # Compute semantic similarity
        results = self.compute_semantic_similarity(interests, candidate_indices)
        
        # Boost keyword matches
        results = self.boost_keyword_matches(interests, results)

        # Filter negative interests
        results = self.filter_negative_interests(results, user_input)
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Apply diversification
        results = self.diversify_by_department_type(results, top_k)
        
        # Prepare final recommendations
        recommendations = []
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            
            # Similarity_Prompt.py'de recommend fonksiyonunda

            recommendation = {
                'bolum_adi': dept_row['bolum_adi'],
                'universite': dept_row['Universite'],
                'sehir': dept_row['Sehir'],
                'ranking_2025': int(dept_row['ranking_2025']),  # Mevcut - değiştirme
                'taban_puan': None,  
                'similarity_score': round(result['similarity_score'], 4),
                'keyword_boost': round(result.get('keyword_boost', 0), 4),
                'description_preview': dept_row['Aciklama'][:150] + '...'
            }
            recommendations.append(recommendation)
            
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
        
    def explain_recommendation(self, recommendation: dict):
        """Explain why this recommendation was made"""
        explanation = f"""
        Bölüm: {recommendation['bolum_adi']}
        Üniversite: {recommendation['universite']}
        Sıralama: {recommendation['ranking_2025']}
        
        Benzerlik Skoru: {recommendation['similarity_score']:.4f}
        Anahtar Kelime Bonusu: {recommendation['keyword_boost']:.4f}
        
        Açıklama: {recommendation['description_preview']}
        """
        return explanation.strip()
    
    def diversify_by_department_type(self, results, top_k=6):
        """Farklı bölüm türlerinden seç"""
        diverse_results = []
        used_dept_names = {}  # Dict ile count tutalım
        
        for result in results:
            idx = result['index']
            dept_name = self.departments_df.iloc[idx]['bolum_adi']
            
            # Bölüm adının temel kısmını al
            dept_base = dept_name.split('(')[0].split('-')[0].strip().upper()
            
            # Bu bölüm türünden kaç tane aldık kontrol et
            current_count = used_dept_names.get(dept_base, 0)
            
            # Aynı bölüm türünden maksimum 2 tane al
            if current_count < 2:
                diverse_results.append(result)
                used_dept_names[dept_base] = current_count + 1
                
                logger.info(f"Added: {dept_base} (Count: {current_count + 1})")
            else:
                logger.info(f"Skipped: {dept_base} (Already have {current_count})")
                
            if len(diverse_results) >= top_k:
                break
        
        return diverse_results
def main():
    """Test the recommendation engine"""
    
    # Initialize engine
    dataset_path = "./Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv"
    engine = HybridRecommendationEngine(dataset_path)
    
    # Test cases
    test_cases = [
        "sağlık alanında çalışmak istiyorum ama sayısal iyi değilim içinde teknolojik bir şey olmasın sıralamam 500.000"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST {i}: {test_case}")
        print('='*80)
        
        recommendations = engine.recommend(test_case, top_k=6)
        
        for j, rec in enumerate(recommendations, 1):
            print(f"{j}. {rec['bolum_adi']} - {rec['universite']}")
            print(f"   Sıralama: {rec['ranking_2025']}")
            print(f"   Benzerlik: {rec['similarity_score']:.4f}")

if __name__ == "__main__":
    main()