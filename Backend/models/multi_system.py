from hybrid_engine import HybridRecommendationEngine
import os
import logging

logger = logging.getLogger(__name__)

class UniversityRecommendationSystem:
    def __init__(self, data_path: str = "./Backend/Data/"):
        self.models = {}
        self.data_path = data_path
        
        # Dataset paths - sadece dosya isimleri
        self.datasets = {
            '2_yillik': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv',
            'sayisal': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Sayisal_Bolumler_Aciklamali.csv', 
            'sozel': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Sozel_Bolumler_aciklamali.csv',
            'esit_agirlik': '/Users/ardaerdegirmenci/Desktop/u/Backend/Data/Esit_Agirlik_Aciklamali.csv'
        }
        
        logger.info("Initializing University Recommendation System...")
        self._load_models()
    
    def _load_models(self):
        """Initialize models for available datasets"""
        for program_type, filename in self.datasets.items():
            filepath = os.path.join(self.data_path, filename)
            
            if os.path.exists(filepath):
                try:
                    logger.info(f"Loading model for {program_type}...")
                    self.models[program_type] = HybridRecommendationEngine(filepath)
                    logger.info(f" Model loaded for {program_type}")
                except Exception as e:
                    logger.error(f" Failed to load {program_type}: {e}")
            else:
                logger.warning(f" Dataset not found: {filepath}")
    
    def recommend(self, program_type: str, user_input: str, top_k: int = 6):
        """Get recommendations for specific program type"""
        if program_type not in self.models:
            available = list(self.models.keys())
            raise ValueError(f"Program type '{program_type}' not available. Available types: {available}")
        
        logger.info(f"Getting recommendations for {program_type}: {user_input}")
        return self.models[program_type].recommend(user_input, top_k)
    
    def get_available_programs(self):
        """Get list of available program types"""
        return list(self.models.keys())
    
    def get_program_info(self):
        """Get detailed info about available programs"""
        info = {}
        for program_type in self.models.keys():
            engine = self.models[program_type]
            info[program_type] = {
                'name': program_type.replace('_', ' ').title(),
                'total_departments': len(engine.departments_df),
                'available': True
            }
        
        # Add unavailable programs
        for program_type, filename in self.datasets.items():
            if program_type not in self.models:
                info[program_type] = {
                    'name': program_type.replace('_', ' ').title(),
                    'total_departments': 0,
                    'available': False,
                    'error': f"Dataset not found: {filename}"
                }
        
        return info
    
    def health_check(self):
        """System health check"""
        return {
            'status': 'healthy' if self.models else 'no_models_loaded',
            'loaded_models': len(self.models),
            'available_programs': list(self.models.keys()),
            'data_path': self.data_path
        }