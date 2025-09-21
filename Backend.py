from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

sys.path.append('./model_training/Training/model_training')
from Similarity_Prompt import HybridRecommendationEngine

app = Flask(__name__)
CORS(app)

class SimpleRecommendationAPI:
    def __init__(self):
        self.dataset_paths = {
            "2_yillik": "./Backend/Data/2yillik_Bolumler_aciklamali_yeni.csv",
            "sayisal": "./Backend/Data/Sayisal_Bolumler_Aciklamali.csv", 
            "sozel": "./Backend/Data/Sozel_Bolumler_aciklamali.csv",
            "esit_agirlik": "./Backend/Data/Esit_Agirlik_Aciklamali.csv"
        }
        self.engines = {}
    
    def get_engine(self, dataset_type):
        if dataset_type not in self.engines:
            dataset_path = self.dataset_paths.get(dataset_type)
            if not dataset_path or not os.path.exists(dataset_path):
                return None
            
            print(f"Loading AI model for {dataset_type}...")
            self.engines[dataset_type] = HybridRecommendationEngine(dataset_path)
        
        return self.engines[dataset_type]

recommendation_api = SimpleRecommendationAPI()

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        user_input = data.get('user_input', '')
        dataset_type = data.get('dataset_type', 'sayisal')
        
        engine = recommendation_api.get_engine(dataset_type)
        if not engine:
            return jsonify({'success': False, 'error': f'Dataset bulunamadı: {dataset_type}'}), 404
        
        recommendations = engine.recommend(user_input, top_k=6)
        
        # float32 ve diğer NumPy tiplerini Python tipine çevir
        clean_recommendations = []
        for rec in recommendations:
            clean_rec = {
                'bolum_adi': str(rec.get('bolum_adi', '')),
                'universite': str(rec.get('universite', '')),
                'sehir': str(rec.get('sehir', '')),
                'ranking_2025': int(rec.get('ranking_2025', 0)),
                'similarity_score': float(rec.get('similarity_score', 0)),
                'description_preview': str(rec.get('description_preview', ''))
            }
            clean_recommendations.append(clean_rec)
        
        return jsonify({
            'success': True,
            'recommendations': clean_recommendations,
            'total_found': len(clean_recommendations)
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("AI Backend başlatılıyor...")
    app.run(debug=True, host='0.0.0.0', port=8000)