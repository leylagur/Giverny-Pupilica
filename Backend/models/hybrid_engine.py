import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

class HybridRecommendationEngine:
    """Hybrid model using semantic similarity + rule-based filtering """
    
    def __init__(self, dataset_path: str):
        """Initialize the recommendation engine"""
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  
        self.departments_df = None
        self.department_embeddings = None
        
        # Load and prepare data
        self.load_dataset(dataset_path)
        self.prepare_embeddings()
