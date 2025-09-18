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
            r'(?:YKS sıralaması|sıralama|sıralamam):?\s*(\d+)',
            r'sıralamam\s+(\d+)',
            r'(\d+)\s*sıralama',
            r'(\d+\.?\d*k?)\s*(?:sıralama|puan)',
            r'sıralama.*?(\d+)'
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
                break
        
        # Extract career intentions and interests using NLP patterns
        interests_keywords = self.extract_career_interests(user_input)
        
        return ', '.join(interests_keywords), ranking
    
    def extract_career_interests(self, text: str):
        """Extract career interests and keywords from natural language"""
        import re
        
        text_lower = text.lower()
        extracted_interests = set()
        
        # Career intention patterns
        career_patterns = {
            'sağlık': [
                r'sağlık.*?(?:sektör|alan|çalış)',
                r'hasta.*?bakım',
                r'tıp.*?alan',
                r'sağlık.*?hizmet',
                r'medikal.*?alan'
            ],
            'teknoloji': [
                r'teknoloji.*?(?:sektör|alan|çalış)',
                r'yazılım.*?(?:geliştir|alan)',
                r'bilgisayar.*?(?:program|alan)',
                r'IT.*?(?:sektör|alan)',
                r'dijital.*?(?:dünya|alan)'
            ],
            'sanat': [
                r'sanat.*?(?:alan|çalış)',
                r'tasarım.*?(?:yapma|alan)',
                r'yaratıcı.*?(?:iş|alan)',
                r'görsel.*?(?:sanat|tasarım)'
            ],
            'spor': [
                r'spor.*?(?:alan|aktivite|sektör)',
                r'fitness.*?(?:aktivite|merkez)',
                r'antrenör.*?(?:olma|çalış)',
                r'sporcu.*?(?:olma|çalış)'
            ],
            'işletme': [
                r'işletme.*?(?:alan|çalış)',
                r'yönetici.*?(?:olma|pozisyon)',
                r'girişimci.*?(?:olma|çalış)',
                r'ticaret.*?(?:yapma|alan)'
            ],
            'mühendislik': [
                r'mühendis.*?(?:olma|çalış)',
                r'teknik.*?(?:alan|çalış)',
                r'inşaat.*?(?:sektör|alan)',
                r'proje.*?(?:yönet|geliştir)'
            ]
        }
        
        # Check career intention patterns
        for category, patterns in career_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    extracted_interests.add(category)
                    break
        
        # Direct keyword matching with context
        context_keywords = {
            'sağlık': ['sağlık', 'hasta', 'tedavi', 'tıp', 'hemşire', 'doktor', 'klinik', 'hastane'],
            'teknoloji': ['teknoloji', 'bilgisayar', 'yazılım', 'program', 'kod', 'web', 'app'],
            'sanat': ['sanat', 'tasarım', 'yaratıcı', 'görsel', 'grafik', 'müzik', 'resim'],
            'spor': ['spor', 'fitness', 'antrenör', 'egzersiz', 'atletik', 'futbol'],
            'matematik': ['matematik', 'hesap', 'analiz', 'sayısal', 'istatistik'],
            'iletişim': ['iletişim', 'sosyal', 'medya', 'gazetecilik', 'halkla'],
            'işletme': ['işletme', 'yönetim', 'pazarlama', 'satış', 'ticaret'],
            'mühendislik': ['mühendislik', 'teknik', 'inşaat', 'makine', 'elektrik']
        }
        
        for category, keywords in context_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    extracted_interests.add(category)
                    break
        
        # Extract explicit mentions
        interest_phrases = [
            r'(?:ilgi\s*alanlarım|ilgi\s*alanları|sevdiğim\s*konular|hobiler):?\s*([^.!?]+)',
            r'(?:seviyorum|ilgileniyorum|hoşlanıyorum)\s*([^.!?]+)',
            r'(?:çalışmak\s*istiyorum|kariyer\s*yapmak\s*istiyorum).*?([^.!?]+)'
        ]
        
        for phrase_pattern in interest_phrases:
            matches = re.finditer(phrase_pattern, text_lower, re.IGNORECASE)
            for match in matches:
                phrase = match.group(1)
                # Extract keywords from the phrase
                for category, keywords in context_keywords.items():
                    for keyword in keywords:
                        if keyword in phrase:
                            extracted_interests.add(category)
        
        # If no interests found, extract all meaningful words
        if not extracted_interests:
            # Remove common words and extract potential interests
            meaningful_words = re.findall(r'\b(?:teknoloji|sağlık|sanat|spor|matematik|bilgisayar|tasarım|fitness|program|yazılım)\b', text_lower)
            for word in meaningful_words:
                for category, keywords in context_keywords.items():
                    if word in keywords:
                        extracted_interests.add(category)
        
        return list(extracted_interests) if extracted_interests else ['genel']
    
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
        """Boost scores for exact keyword matches"""
        interests_lower = interests.lower()
        keywords = [word.strip() for word in interests_lower.split(',')]
        
        for result in results:
            idx = result['index']
            dept_row = self.departments_df.iloc[idx]
            
            # Check for keyword matches in department name and description
            dept_text = (dept_row['bolum_adi'] + ' ' + dept_row['Aciklama']).lower()
            
            keyword_boost = 0
            for keyword in keywords:
                if keyword in dept_text:
                    keyword_boost += 0.1  # Boost score by 0.1 for each keyword match
                    
            result['similarity_score'] += keyword_boost
            result['keyword_boost'] = keyword_boost
            
        return results
    
    def recommend(self, user_input: str, top_k: int = 10):
        """Main recommendation function"""
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
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Prepare final recommendations
        recommendations = []
        for result in results[:top_k]:
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

def main():
    """Test the recommendation engine"""
    
    # Initialize engine
    dataset_path = "/Users/ardaerdegirmenci/Desktop/u/Dataset_creation/Datasets/2yillik_Bolumler_aciklamali_yeni.csv"
    engine = HybridRecommendationEngine(dataset_path)
    
    # Test cases
    test_cases = [
        "İlgi alanlarım: teknoloji, matematik, programlama. YKS sıralaması: 200000",
        "Ben sağlık sektöründe çalışmak istiyorum aynı zamanda spor ve fitness aktivitelerini de seviyorum sıralamam 650000",
        "Teknoloji alanında kariyer yapmak istiyorum, özellikle yazılım geliştirme ilgimi çekiyor. 300k sıralama yaptım",
        "Sanat ve tasarım konularını seviyorum, yaratıcı işler yapmak istiyorum. Sıralama: 450000",
        "Spor antrenörü olmak istiyorum, fitness ve atletik aktivitelerde çalışmayı planlıyorum. 800000 sıralama"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test_case}")
        print('='*80)
        
        recommendations = engine.recommend(test_case, top_k=6, diversify=True)
        
        for j, rec in enumerate(recommendations, 1):
            print(f"\n{j}. {rec['bolum_adi']} - {rec['universite']}")
            print(f"   Sıralama: {rec['ranking_2025']}")
            print(f"   Benzerlik: {rec['similarity_score']:.4f} (Boost: {rec['keyword_boost']:.4f})")
            print(f"   Açıklama: {rec['description_preview']}")
            print(f"   💡 Neden: {rec['match_reason']}")
if __name__ == "__main__":
    main()