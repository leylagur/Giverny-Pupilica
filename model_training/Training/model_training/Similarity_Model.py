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
    
        # INDEX'İ SIFIRLA - BU ÇÖK ÖNEMLİ
        df = df.reset_index(drop=True)
    
        self.departments_df = df
        logger.info(f"Loaded {len(df)} departments")
        
    def prepare_embeddings(self):
        """Create embeddings for all department descriptions"""
        logger.info("Creating embeddings for department descriptions...")
    
        descriptions = self.departments_df['Aciklama'].tolist()
    
        # ÖNEMLI: Index'leri sıfırla
        self.departments_df = self.departments_df.reset_index(drop=True)
    
        self.department_embeddings = self.model.encode(descriptions, show_progress_bar=True)
    
        logger.info("Embeddings created successfully")
    
    def extract_interests_and_ranking(self, user_input: str):
        """Parse user input to extract interests and ranking"""
        import re
        
        # Extract ranking with regex
        ranking_pattern = r'(?:YKS sıralaması|sıralama|sıralamam):?\s*(\d+)'
        ranking_match = re.search(ranking_pattern, user_input, re.IGNORECASE)
        
        if ranking_match:
            ranking = int(ranking_match.group(1))
        else:
            ranking = None
            
        # Extract interests (everything before ranking or whole text)
        if ranking_match:
            interests_text = user_input[:ranking_match.start()].strip()
        else:
            interests_text = user_input
            
        # Clean interests text
        interests_text = re.sub(r'(?:İlgi alanlarım|ilgi alanları|sevdiğim konular):?\s*', '', interests_text, flags=re.IGNORECASE)
        interests_text = interests_text.strip(' .,;:')
        
        return interests_text, ranking
    
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
        "İlgi alanlarım: sağlık, hasta bakımı. YKS sıralaması: 400000",
        "İlgi alanlarım: sanat, tasarım, yaratıcılık. YKS sıralaması: 600000",
        "İlgi alanlarım: spor, fitness. YKS sıralaması: 800000"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case}")
        print('='*60)
        
        recommendations = engine.recommend(test_case, top_k=5)
        
        for j, rec in enumerate(recommendations, 1):
            print(f"\n{j}. {rec['bolum_adi']} - {rec['universite']}")
            print(f"   Sıralama: {rec['ranking_2025']}")
            print(f"   Benzerlik: {rec['similarity_score']:.4f}")
            print(f"   Açıklama: {rec['description_preview']}")

if __name__ == "__main__":
    main()