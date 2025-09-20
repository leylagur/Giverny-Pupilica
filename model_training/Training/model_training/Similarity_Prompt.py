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
        
        # Load and prepare data
        self.load_dataset(dataset_path)
        self.prepare_embeddings()
        
    def load_dataset(self, dataset_path: str):
        """Load department dataset"""
        logger.info(f"Loading dataset from {dataset_path}")
    
        # Load CSV
        df = pd.read_csv(dataset_path)
    
        # Clean and prepare data
        df = df.dropna(subset=['Aciklama', 'bolum_adi'])
        df['ranking_2025'] = pd.to_numeric(df['2025_Taban_Sıralama'], errors='coerce')
    
        # Remove invalid rankings
        df = df.dropna(subset=['ranking_2025'])
    
        # ÖNEMLİ: Index'leri sıfırla
        df = df.reset_index(drop=True)
    
        self.departments_df = df
        logger.info(f"Loaded {len(df)} departments")
        
        df = df.reset_index(drop=True)
        
    def prepare_embeddings(self):
        """Create embeddings for all department descriptions"""
        logger.info("Creating embeddings for department descriptions...")
    
        # ÖNEMLİ: Index'lerin sıfır olduğundan emin ol
        self.departments_df = self.departments_df.reset_index(drop=True)
    
        descriptions = self.departments_df['Aciklama'].tolist()
        self.department_embeddings = self.model.encode(descriptions, show_progress_bar=True)
    
        logger.info("Embeddings created successfully")
    
    def extract_interests_and_ranking(self, user_input: str):
        """Parse user input to extract interests and ranking with NLP"""
        import re
        
        # Enhanced ranking patterns
        ranking_patterns = [
            r'(?:YKS sıralamasi|sıralama|sıralamam):?\s*(\d+(?:\.\d+)?k?)',
            r'sıralamam\s+(\d+(?:\.\d+)?k?)',
            r'(\d+(?:\.\d+)?k?)\s*sıralama',
            r'(\d{1,3}(?:\.\d{3})+)',  # 500.000 format
            r'(\d{4,7})',  # 500000 format
            r'sıralama.*?(\d+(?:\.\d+)?k?)'
        ]
        
        ranking = None
        for pattern in ranking_patterns:
            ranking_match = re.search(pattern, user_input, re.IGNORECASE)
            if ranking_match:
                rank_str = ranking_match.group(1)
                # Handle 'k' notation (650k = 650000)
                if 'k' in rank_str.lower():
                    ranking = int(float(rank_str.lower().replace('k', '')) * 1000)
                else:
                    ranking = int(float(rank_str))

                # YENİ:
                if 'k' in rank_str.lower():
                    ranking = int(float(rank_str.lower().replace('k', '')) * 1000)
                elif '.' in rank_str and len(rank_str) > 4:
                    ranking = int(rank_str.replace('.', ''))  # 500.000 -> 500000
                else:
                    ranking = int(float(rank_str))
        
        # Extract career intentions and interests using NLP patterns
        interests_keywords = self.extract_career_interests(user_input)
        
        return ', '.join(interests_keywords), ranking
    
    def extract_career_interests(self, text: str):
        """Extract career interests and keywords from natural language with negative filtering"""
        import re
        
        text_lower = text.lower()
        extracted_interests = set()
        excluded_interests = set()  # Bu satır eksikti
        
        # Negative patterns - önce bunları kontrol et
        negative_patterns = {
            'teknoloji': [
                r'teknoloji.*?(?:sevmiyorum|istemiyorum|ilgilenmiyorum|olmasın|alakalı.*?olsun.*?istemiyorum)',
                r'(?:sevmiyorum|istemiyorum|ilgilenmiyorum).*?teknoloji',
                r'teknoloji.*?ile.*?alakalı.*?(?:olsun.*?istemiyorum|istemem)'
            ],
            'sağlık': [
                r'sağlık.*?(?:sevmiyorum|istemiyorum|ilgilenmiyorum)',
                r'(?:sevmiyorum|istemiyorum).*?sağlık'
            ],
            'matematik': [
                r'matematik.*?(?:sevmiyorum|kötüyüm|zor)',
                r'(?:sevmiyorum|kötüyüm).*?matematik'
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
        """Remove departments that match negative interests"""
        import re
        
        user_lower = user_input.lower()
        filtered_results = []
        
        # Gemini AI tarafından oluşturulan negative keywords
        negative_keywords = {
            'teknoloji': ['teknoloji', 'bilgisayar', 'matematik', 'sayısal', 'programlama', 'kodlama', 'karmaşık', 'zor', 'anlaşılmaz'],
            'sağlık': ['sağlık', 'hasta', 'kan', 'tıp', 'ameliyat', 'hastalık', 'ölüm', 'acı', 'korkutucu'],
            'matematik': ['matematik', 'hesap', 'sayı', 'formül', 'problem', 'çözüm', 'karmaşık', 'zor'],
            'sosyal': ['tarih', 'edebiyat', 'ezber', 'okuma', 'yazma', 'analiz', 'sıkıcı', 'yorucu'],
            'spor': ['tembel', 'pasif', 'hareketsiz'],
            'işletme': ['sıkıcı', 'karmaşık', 'zor', 'stresli'],
            'eğitim': ['sıkıcı', 'zor', 'yorucu', 'stresli', 'ezber']
        }
        
        # Define negative patterns and corresponding keywords to filter
        negative_filters = {
            'teknoloji': {
                'patterns': [
                    r'teknoloji.*?(?:istemiyorum|sevmiyorum|olmasın)',
                    r'teknoloji.*?ile.*?alakalı.*?(?:olsun.*?istemiyorum|istemem)',
                    r'bilgisayar.*?(?:istemiyorum|sevmiyorum)',
                    r'matematik.*?(?:sevmiyorum|kötüyüm|zor).*?(?:teknoloji|bilgisayar)',
                    r'programlama.*?(?:sevmiyorum|istemiyorum|zor)'
                ],
                'filter_keywords': negative_keywords['teknoloji']  # Gemini'den gelen keywords
            },
            'sağlık': {
                'patterns': [
                    r'sağlık.*?(?:istemiyorum|sevmiyorum)',
                    r'kan.*?(?:görmek.*?istemiyorum|korkuyorum)',
                    r'hasta.*?(?:görmek.*?istemiyorum|ilgilenmiyorum)',
                    r'ameliyat.*?(?:korkuyorum|istemiyorum)'
                ],
                'filter_keywords': negative_keywords['sağlık']
            },
            'matematik': {
                'patterns': [
                    r'matematik.*?(?:sevmiyorum|kötüyüm|zor|anlayamıyorum)',
                    r'sayısal.*?(?:kötüyüm|zor|başarısızım)',
                    r'hesap.*?(?:yapmak.*?zor|sevmiyorum)'
                ],
                'filter_keywords': negative_keywords['matematik']
            },
            'sosyal': {
                'patterns': [
                    r'tarih.*?(?:sevmiyorum|sıkıcı|ezberleme)',
                    r'edebiyat.*?(?:sevmiyorum|sıkıcı)',
                    r'ezberleme.*?(?:sevmiyorum|zor)',
                    r'sosyal.*?(?:sevmiyorum|istemiyorum)'
                ],
                'filter_keywords': negative_keywords['sosyal']
            },
            'spor': {
                'patterns': [
                    r'spor.*?(?:sevmiyorum|istemiyorum|yapmam)',
                    r'fiziksel.*?aktivite.*?(?:sevmiyorum|istemiyorum)',
                    r'egzersiz.*?(?:sevmiyorum|yapmam)',
                    r'tembel.*?(?:im|sayılırım)'
                ],
                'filter_keywords': negative_keywords['spor']
            },
            'işletme': {
                'patterns': [
                    r'işletme.*?(?:sevmiyorum|istemiyorum|sıkıcı)',
                    r'pazarlama.*?(?:sevmiyorum|istemiyorum)',
                    r'muhasebe.*?(?:sevmiyorum|zor)'
                ],
                'filter_keywords': negative_keywords['işletme']
            },
            'eğitim': {
                'patterns': [
                    r'öğretmen.*?(?:olmak.*?istemiyorum|sevmiyorum)',
                    r'eğitim.*?(?:sevmiyorum|istemiyorum|sıkıcı)',
                    r'çocuk.*?(?:sevmiyorum|ilgilenmiyorum)'
                ],
                'filter_keywords': negative_keywords['eğitim']
            }
        }
        
        # Check which categories to filter out
        categories_to_filter = set()
        for category, config in negative_filters.items():
            for pattern in config['patterns']:
                if re.search(pattern, user_lower):
                    categories_to_filter.add(category)
                    logger.info(f"🚫 Detected negative interest: {category}")
                    break
        
        # Filter results
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            dept_text = (dept_row['bolum_adi'] + ' ' + dept_row['Aciklama']).lower()
            
            # Check if department should be filtered out
            should_filter = False
            for category in categories_to_filter:
                filter_keywords = negative_filters[category]['filter_keywords']
                matching_keywords = [kw for kw in filter_keywords if kw in dept_text]
                
                if matching_keywords:
                    should_filter = True
                    logger.info(f"❌ Filtered out: {dept_row['bolum_adi']} (negative: {category}, keywords: {matching_keywords})")
                    break
            
            if not should_filter:
                filtered_results.append(result)
        
        logger.info(f"🔍 Filtered from {len(results)} to {len(filtered_results)} departments")
        return filtered_results    
    
    def filter_by_ranking(self, ranking: int, tolerance: int = 50000):
        """Filter departments by ranking range"""
        if ranking is None:
            return self.departments_df.index.tolist()
            
        min_rank = max(1, ranking - tolerance)
        max_rank = ranking + tolerance
            
        filtered_indices = self.departments_df[
            (self.departments_df['ranking_2025'] >= min_rank) & 
            (self.departments_df['ranking_2025'] <= max_rank)
        ].index.tolist()
            
        logger.info(f"Filtered to {len(filtered_indices)} departments in ranking range {min_rank}-{max_rank}")
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
                'teknoloji': ['bilgisayar', 'yazılım', 'programlama', 'web', 'oyun', 'dijital', 'sistem', 'kodlama', 'geliştirme', 'uygulama', 'veri', 'yapay zeka', 'robotik', 'siber güvenlik'],
        'sağlık': ['sağlık', 'tıp', 'hemşire', 'hasta', 'tedavi', 'anestezi', 'veteriner', 'diş', 'fizyoterapi', 'tıbbi', 'biyoloji', 'eczacılık', 'tıbbi görüntüleme'],
        'sanat': ['sanat', 'tasarım', 'grafik', 'müzik', 'sinema', 'fotoğraf', 'görsel', 'yaratıcı', 'illüstrasyon', 'heykel', 'resim', 'seramik', 'tasarım', 'moda'],
        'spor': ['spor', 'antrenör', 'fitness', 'egzersiz', 'rekreasyon', 'beden', 'atletik', 'hareket', 'yüzme', 'basketbol', 'futbol', 'tenis', 'spor yönetimi'],
        'işletme': ['işletme', 'pazarlama', 'muhasebe', 'ticaret', 'yönetim', 'ekonomi', 'finans', 'satış', 'finansal', 'strateji', 'iş geliştirme', 'girişimcilik', 'ticaret', 'lojistik', 'insan kaynakları'],
        'gastronomi': ['gastronomi', 'mutfak sanatları', 'yemek', 'aşçılık', 'pasta', 'şef', 'fırıncılık', 'gıda', 'restoran'],
        'eğitim': ['öğretmen', 'eğitim', 'öğretim', 'ders', 'okul', 'çocuk', 'akademik', 'öğrenci', 'pedagoji', 'psikoloji', 'rehberlik']
        }
        
        # Keywords belirle
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
    
    def recommend(self, user_input: str, top_k: int = 10):
        """Main recommendation function with diversification"""
        logger.info(f"Processing recommendation for: {user_input}")
        
        # Parse input
        interests, ranking = self.extract_interests_and_ranking(user_input)
        logger.info(f"Extracted interests: '{interests}', ranking: {ranking}")
        
        # Filter by ranking
        candidate_indices = self.filter_by_ranking(ranking)
        
        if not candidate_indices:
            return []
            
        # Compute semantic similarity
        results = self.compute_semantic_similarity(interests, candidate_indices)
        
        # Boost keyword matches
        results = self.boost_keyword_matches(interests, results)

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
            
            recommendation = {
                'bolum_adi': dept_row['bolum_adi'],
                'universite': dept_row['Universite'],
                'sehir': dept_row['Sehir'],
                'ranking_2025': int(dept_row['ranking_2025']),
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
    dataset_path = "/Users/ardaerdegirmenci/Desktop/u/Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv"
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