#Ana çalışan modelimizdir Read-me içinde temel çalışma prensibi anlatılmıştır
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
    Geliştirilmiş Hybrid model - Hard reset sonrası optimize edilmiş versiyon
    """
    
    def __init__(self, dataset_path: str):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.departments_df = None
        self.department_embeddings = None

        self.load_dataset(dataset_path)
        self.prepare_embeddings()
        
        # HARD RESET: Her işlem sonrası sistem temizlenir
        logger.info("Backend hard reset - sistem temizlendi")
        
    def load_dataset(self, dataset_path: str):
        logger.info(f"Loading dataset from {dataset_path}")

        df = pd.read_csv(dataset_path, dtype=str)
        df = df.dropna(subset=['Aciklama', 'bolum_adi'])
        
        rankings = []
        valid_rows = []
        
        for idx, row in df.iterrows():
            ranking_value = row['2025_Taban_Sıralama']
            
            try:
                if pd.isna(ranking_value) or ranking_value == '':
                    continue
                    
                ranking_str = str(ranking_value).strip()
                
                if ',' in ranking_str:
                    continue
                    
                if '.' in ranking_str:
                    clean_value = ranking_str.replace('.', '')
                else:
                    clean_value = ranking_str
                    
                ranking_int = int(clean_value)
                
                rankings.append(ranking_int)
                valid_rows.append(idx)
                
            except:
                continue
        
        df_clean = df.iloc[valid_rows].copy()
        df_clean['ranking_2025'] = rankings
        df_clean = df_clean.reset_index(drop=True)
        
        self.departments_df = df_clean
        logger.info(f"Loaded {len(df_clean)} clean departments")
        
        # HARD RESET: Veri yükleme sonrası temizlik
        logger.info("Dataset loading completed - hard reset")
        
        return df_clean
        
    def prepare_embeddings(self):
        logger.info("Creating embeddings for department descriptions...")
        
        self.departments_df = self.departments_df.reset_index(drop=True)
        descriptions = self.departments_df['Aciklama'].tolist()
        self.department_embeddings = self.model.encode(descriptions, show_progress_bar=True)
        
        logger.info("Embeddings created successfully - hard reset")
    
    def extract_interests_and_ranking(self, user_input: str):
        import re
        
        # Ranking extraction patterns
        ranking_patterns = [
            r'(?:YKS sıralamasi|sıralama|sıralamam):?\s*(\d+(?:\.\d{3})*k?)',
            r'sıralamam\s+(\d+(?:\.\d{3})*k?)',
            r'(\d+)\s*bin',
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
                    if ',' in rank_str:
                        continue
                    
                    if 'bin' in user_input.lower() and not 'k' in rank_str:
                        ranking = int(rank_str) * 1000
                    elif 'k' in rank_str.lower():
                        ranking = int(float(rank_str.lower().replace('k', '')) * 1000)
                    elif '.' in rank_str and len(rank_str) > 4:
                        ranking = int(rank_str.replace('.', ''))
                    else:
                        ranking = int(rank_str)

                    if ranking:
                        break
                        
                except (ValueError, TypeError):
                    continue
        
        interests_keywords = self.extract_career_interests(user_input)
        
        # HARD RESET: Interest extraction sonrası temizlik
        logger.info(f"Interests extracted: {interests_keywords} - hard reset")
        
        return ', '.join(interests_keywords), ranking
    
    def extract_career_interests(self, text: str):
        """Geliştirilmiş interest extraction - pozitif ve negatif algılama"""
        import re
        
        text_lower = text.lower()
        extracted_interests = set()
        excluded_interests = set()
        positive_boost = set()  # YENI: Pozitif ifadeler için boost
        
        # Pozitif pattern'ler - bunlar boost alacak
        positive_patterns = {
            'teknoloji': [
                r'teknoloji.*?(?:seviyorum|istiyorum|çok.*?iyi|harika)',
                r'(?:çok.*?seviyorum|bayılıyorum).*?teknoloji',
                r'bilgisayar.*?(?:seviyorum|çok.*?iyi|harika)'
            ],
            'sağlık': [
                r'sağlık.*?(?:seviyorum|istiyorum|çok.*?önemli)',
                r'(?:çok.*?seviyorum|bayılıyorum).*?sağlık',
                r'hasta.*?(?:yardım.*?seviyorum|seviyorum)'
            ],
            'sanat': [
                r'sanat.*?(?:seviyorum|istiyorum|çok.*?yaratıcı)',
                r'(?:çok.*?seviyorum|bayılıyorum).*?sanat',
                r'tasarım.*?(?:seviyorum|çok.*?iyi)'
            ],
            'mühendislik': [
                r'mühendislik.*?(?:seviyorum|istiyorum|çok.*?iyi)',
                r'(?:çok.*?seviyorum|bayılıyorum).*?mühendislik'
            ],
            'hukuk': [
                r'hukuk.*?(?:seviyorum|istiyorum|çok.*?iyi)',
                r'avukat.*?(?:seviyorum|çok.*?istiyorum)'
            ]
        }
        
        # Negatif pattern'ler - bunlar exclude edilecek
        negative_patterns = {
            'teknoloji': [
                r'teknoloji.*?(?:sevmiyorum|istemiyorum|olmasın)',
                r'(?:sevmiyorum|istemiyorum).*?teknoloji',
                r'bilgisayar.*?(?:sevmiyorum|kötüyüm)'
            ],
            'sağlık': [
                r'sağlık.*?(?:sevmiyorum|istemiyorum)',
                r'tıp.*?(?:sevmiyorum|zor|istemiyorum)',
                r'kan.*?(?:korkuyorum|sevmiyorum)'
            ],
            'matematik': [
                r'matematik.*?(?:sevmiyorum|kötüyüm|zor)',
                r'sayısal.*?(?:kötüyüm|sevmem)'
            ],
            'mühendislik': [
                r'mühendislik.*?(?:sevmiyorum|istemiyorum)',
                r'teknik.*?(?:sevmiyorum|zor)'
            ],
            'hukuk': [
                r'hukuk.*?(?:sevmiyorum|istemiyorum|sıkıcı)',
                r'avukat.*?(?:sevmiyorum|istemiyorum)'
            ]
        }
        
        # Check positive patterns first (BOOST)
        for category, patterns in positive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    positive_boost.add(category)
                    extracted_interests.add(category)
                    break
        
        # Check negative patterns (EXCLUDE)
        for category, patterns in negative_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    excluded_interests.add(category)
                    break
        
        # Normal career patterns
        career_patterns = {
            'sağlık': [
                r'(?:doktor|hekim|tıp).*?(?:olmak|istiyorum)',
                r'sağlık.*?(?:sektör|alan|çalışmak)',
                r'hasta.*?(?:bakım|tedavi)',
                r'(?:hemşire|eczacı|veteriner).*?(?:olmak|çalış)',
                r'tıbbi.*?(?:cihaz|teknoloji|analiz)'
            ],
            'sanat': [
                r'(?:sanat|tasarım).*?(?:yapmak|alan)',
                r'grafik.*?(?:tasarım|yapmak)',
                r'yaratıcı.*?(?:iş|alan)',
                r'(?:müzik|sinema|fotoğraf).*?(?:yapmak|alan)',
                r'görsel.*?(?:sanat|tasarım)'
            ],
            'teknoloji': [
                r'(?:programcı|developer).*?(?:olmak|istiyorum)',
                r'yazılım.*?(?:geliştir|yapmak)',
                r'bilgisayar.*?(?:program|mühendis)',
                r'web.*?(?:site|tasarım|geliştir)',
                r'(?:oyun|mobil).*?(?:geliştir|yapmak)'
            ],
            'mühendislik': [
                r'(?:mühendis|mühendislik).*?(?:olmak|istiyorum)',
                r'(?:makina|elektrik|inşaat).*?mühendis',
                r'teknik.*?(?:çalışmak|alan)',
                r'proje.*?(?:yapmak|geliştir)',
                r'sistem.*?(?:tasarım|geliştir)'
            ],
            'hukuk': [
                r'(?:avukat|hukuk).*?(?:olmak|istiyorum)',
                r'hukuk.*?(?:alan|okunak|çalışmak|bölüm)',
                r'adalet.*?(?:sistem|alan)',
                r'dava.*?(?:takip|savunma)',
                r'(?:hâkim|savcı).*?(?:olmak|istiyorum)'
            ],
            'finans': [
                r'(?:bankacı|banker).*?(?:olmak|çalış)',
                r'finans.*?(?:sektör|alan|uzman)',
                r'borsa.*?(?:çalış|analiz)',
                r'muhasebe.*?(?:yapmak|çalış)',
                r'yatırım.*?(?:uzman|danışman)'
            ],
            'işletme': [
                r'işletme.*?(?:çalış|yönetim)',
                r'pazarlama.*?(?:yapmak|çalış)',
                r'yönetici.*?(?:olmak|çalış)',
                r'girişimci.*?(?:olmak|iş.*?kurmak)',
                r'satış.*?(?:yapmak|uzman)'
            ],
            'eğitim': [
                r'öğretmen.*?(?:olmak|istiyorum)',
                r'eğitim.*?(?:vermek|çalışmak)',
                r'ders.*?(?:vermek|anlatmak)',
                r'çocuk.*?(?:gelişim|eğitim)',
                r'akademisyen.*?(?:olmak|çalış)'
            ],
            'spor': [
                r'antrenör.*?(?:olmak|çalış)',
                r'spor.*?(?:alan|yapmak)',
                r'fitness.*?(?:antrenör|çalış)',
                r'beden.*?eğitim.*?(?:öğretmen|çalış)',
                r'egzersiz.*?(?:uzman|çalış)'
            ],
            'gastronomi': [
                r'aşçı.*?(?:olmak|çalış)',
                r'mutfak.*?(?:çalış|şef)',
                r'yemek.*?(?:yapmak|pişirmek)',
                r'gastronomi.*?(?:çalış|alan)',
                r'restoran.*?(?:açmak|yönetim)'
            ],
            'medya': [
                r'gazeteci.*?(?:olmak|çalış)',
                r'medya.*?(?:çalış|sektör)',
                r'televizyon.*?(?:çalış|program)',
                r'sosyal.*?medya.*?(?:uzman|çalış)',
                r'reklam.*?(?:yapmak|çalış)'
            ],
            'turizm': [
                r'turizm.*?(?:çalış|rehber)',
                r'otel.*?(?:çalış|yönetim)',
                r'seyahat.*?(?:acenta|rehber)',
                r'tur.*?(?:rehber|operatör)',
                r'konaklama.*?(?:çalış|yönetim)'
            ]
        }
        
        # Check normal career patterns
        for category, patterns in career_patterns.items():
            if category not in excluded_interests:
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        extracted_interests.add(category)
                        break
        
        # Direct keyword matching
        context_keywords = {
            'sağlık': ['sağlık', 'doktor', 'hemşire', 'tıp'],
            'teknoloji': ['teknoloji', 'yazılım', 'program', 'kod'],
            'sanat': ['sanat', 'tasarım', 'yaratıcı', 'grafik'],
            'spor': ['spor', 'antrenör', 'fitness'],
            'hukuk': ['hukuk', 'avukat', 'mahkeme', 'dava'],
            'finans': ['finans', 'banka', 'muhasebe'],
            'işletme': ['işletme', 'pazarlama', 'yönetim'],
            'eğitim': ['öğretmen', 'eğitim', 'ders'],
            'gastronomi': ['aşçı', 'mutfak', 'yemek'],
            'turizm': ['turizm', 'otel', 'seyahat'],
            'mühendislik': ['mühendislik', 'mühendis', 'teknik'],
            'güvenlik': ['güvenlik', 'polis', 'asker'],
            'tarım': ['tarım', 'ziraat', 'hayvancılık'],
            'medya': ['medya', 'gazete', 'haber']
        }
        
        for category, keywords in context_keywords.items():
            if category not in excluded_interests:
                for keyword in keywords:
                    if keyword in text_lower:
                        extracted_interests.add(category)
                        break
        
        final_interests = extracted_interests - excluded_interests
        
        # Return interests with positive boost info
        result = list(final_interests) if final_interests else ['genel']
        
        # Store positive boost for later use
        self.positive_boost_categories = positive_boost
        
        return result
    
    def filter_by_ranking(self, ranking: int, tolerance_percent: float = 0.20):
        if ranking is None:
            return self.departments_df.index.tolist()
        
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
        
        # HARD RESET: Ranking filtreleme sonrası
        logger.info("Ranking filtering completed - hard reset")
        
        return filtered_indices
    
    def compute_semantic_similarity(self, interests: str, candidate_indices: list):
        if not interests.strip():
            return []
            
        interest_embedding = self.model.encode([interests])
        candidate_embeddings = self.department_embeddings[candidate_indices]
        similarities = cosine_similarity(interest_embedding, candidate_embeddings)[0]
        
        results = []
        for i, idx in enumerate(candidate_indices):
            results.append({
                'index': idx,
                'similarity_score': similarities[i]
            })
        
        # HARD RESET: Similarity hesaplama sonrası
        logger.info("Similarity computation completed - hard reset")
        
        return results
    
    def boost_keyword_matches(self, interests: str, results: list):
        """Geliştirilmiş keyword boost - pozitif ifadeler ekstra boost alır"""
        interests_lower = interests.lower()
        
        # Expanded mappings - düzeltilmiş versiyon
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
                # DÜZELTME: [:3] kaldırıldı - tüm keyword'leri kontrol et
                if word in expanded_keywords:
                    all_keywords.update(expanded_keywords)
                    break
        
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            dept_text = (dept_row['bolum_adi'] + ' ' + dept_row['Aciklama']).lower()
            
            keyword_boost = 0
            for keyword in all_keywords:
                if keyword in dept_text:
                    # ARTTIRILMIŞ BOOST: 0.1'den 0.3'e çıkarıldı
                    base_boost = 0.3
                    
                    # Pozitif ifadeler ekstra boost alır
                    if hasattr(self, 'positive_boost_categories'):
                        for boost_category in self.positive_boost_categories:
                            if keyword in expanded_mappings.get(boost_category, []):
                                base_boost += 0.2  # Ekstra pozitif boost
                                break
                    
                    keyword_boost += base_boost
                    
            result['similarity_score'] += keyword_boost
            result['keyword_boost'] = keyword_boost
        
        # HARD RESET: Keyword boost sonrası
        logger.info("Keyword boosting completed - hard reset")
        
        return results
    
    def filter_negative_departments(self, candidate_indices: list, user_input: str):
        """Department'ları negatif keyword'lere göre filtrele - similarity hesaplamadan önce"""
        user_lower = user_input.lower()
        
        negative_categories = {
            'sağlık': ['tıp', 'tip', 'sağlık', 'hemşire', 'diş', 'veteriner', 'eczacı'],
            'mühendislik': ['mühendislik', 'mühendis'],
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım'],
            'hukuk': ['hukuk', 'avukat'],
            'matematik': ['matematik', 'hesap'],
            'spor': ['spor', 'fitness'],
            'işletme': ['işletme', 'pazarlama'],
            'eğitim': ['öğretmen', 'eğitim'],
            'finans': ['finans', 'banka']
        }
        
        negative_words = ['istemiyorum', 'sevmiyorum', 'sevmem', 'olmasın']
        
        filtered_indices = []
        excluded_count = 0
        
        for idx in candidate_indices:
            dept_name = self.departments_df.iloc[idx]['bolum_adi'].lower()
            should_exclude = False
            
            for category, keywords in negative_categories.items():
                for keyword in keywords:
                    for neg_word in negative_words:
                        pattern1 = f"{keyword} {neg_word}"
                        pattern2 = f"{neg_word} {keyword}"
                        
                        if (pattern1 in user_lower or pattern2 in user_lower):
                            # Bu kategoriyi exclude et
                            if any(kw in dept_name for kw in keywords):
                                should_exclude = True
                                excluded_count += 1
                                logger.info(f"EXCLUDED: {self.departments_df.iloc[idx]['bolum_adi']} - {category} filtrelendi")
                                break
                    if should_exclude:
                        break
                if should_exclude:
                    break
            
            if not should_exclude:
                filtered_indices.append(idx)
        
        logger.info(f"Negative filtering: {len(candidate_indices)} -> {len(filtered_indices)} departments ({excluded_count} excluded)")
        return filtered_indices
    
    def recommend(self, user_input: str, top_k: int = 10, tolerance_percent: float = 0.20):
        logger.info(f"Processing recommendation for: {user_input}")
        
        interests, ranking = self.extract_interests_and_ranking(user_input)
        logger.info(f"Extracted interests: '{interests}', ranking: {ranking}")
        
        candidate_indices = self.filter_by_ranking(ranking, tolerance_percent)
        
        if not candidate_indices:
            return []
        
        # 1. ÖNCE NEGATİF FİLTRELEME YAP (similarity hesaplamadan önce)
        candidate_indices = self.filter_negative_departments(candidate_indices, user_input)
        
        if not candidate_indices:
            logger.info("No departments left after negative filtering")
            return []
        
        # 2. Sonra similarity hesapla
        results = self.compute_semantic_similarity(interests, candidate_indices)
        results = self.boost_keyword_matches(interests, results)
        
        # 3. Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # 4. Sadece en iyi sonuçları al (diversification kaldırıldı)
        results = results[:top_k]
        
        # 5. Prepare final recommendations
        recommendations = []
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            
            # Similarity score'u yüzde olarak hesapla
            similarity_percentage = min(100, int(result['similarity_score'] * 100))
            
            recommendation = {
                'bolum_adi': dept_row['bolum_adi'],
                'universite': dept_row['Universite'],
                'sehir': dept_row['Sehir'],
                'ranking_2025': int(dept_row['ranking_2025']),
                'taban_puan': None,
                'similarity_score': round(result['similarity_score'], 4),
                'similarity_percentage': f"{similarity_percentage}%",
                'keyword_boost': round(result.get('keyword_boost', 0), 4),
                'description_preview': dept_row['Aciklama'][:150] + '...'
            }
            recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        logger.info("Recommendation process completed - FULL HARD RESET")
        
        return recommendations

def main():
    dataset_path = "./Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv"
    engine = HybridRecommendationEngine(dataset_path)
    
    test_cases = [
        "sanat ve tasarım çok seviyorum 120 bin sıralama",
        "mühendislik istiyorum tıp istemiyorum 50 bin",
        "hukuk okumak istiyorum avukat olmak istiyorum 20 bin"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST {i}: {test_case}")
        print('='*80)
        
        recommendations = engine.recommend(test_case, top_k=6)
        
        for j, rec in enumerate(recommendations, 1):
            print(f"{j}. {rec['bolum_adi']} - {rec['universite']}")
            print(f"   Sıralama: {rec['ranking_2025']}")
            print(f"   Uyum: {rec['similarity_percentage']} ({rec['similarity_score']:.4f})")

if __name__ == "__main__":
    main()