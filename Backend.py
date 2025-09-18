#print("ily")
#print("cko seviom")

# Backend.py dosyasının başına
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Frontend erişimi için

# Senin mevcut model loading kodu...

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        keywords = data.get('keywords', '')
        
        # Senin similarity model fonksiyonunu buraya çağır
        # Örnek format:
        predictions = your_similarity_function(keywords)
        
        # Sonucu frontend için formatla
        recommendations = [
            {
                "department": dept_name,
                "score": similarity_score
            }
            for dept_name, similarity_score in predictions
        ]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
    