from .hybrid_engine import HybridRecommendationEngine
import os

class UniversityRecommendationSystem:
    def __init__(self, data_path: str):
        self.models = {}
        
        # Dataset paths
        datasets = {
            '2_yillik': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv',
            'Sayisal': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Sayisal_Bolumler_Aciklamali.csv', 
            'Sozel': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Sozel_Bolumler_aciklamali.csv',
            'Esit_Agirlik': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Esit_Agirlik_Aciklamali.csv'
        }
        
        # Initialize models
        for program_type, filename in datasets.items():
            filepath = os.path.join(data_path, filename)
            if os.path.exists(filepath):
                self.models[program_type] = HybridRecommendationEngine(filepath)
            else:
                print(f"Warning: {filepath} not found")
    
    def recommend(self, program_type: str, user_input: str, top_k: int = 6):
        if program_type not in self.models:
            raise ValueError(f"Program type '{program_type}' not available")
        
        return self.models[program_type].recommend(user_input, top_k)
    
    def get_available_programs(self):
        return list(self.models.keys())