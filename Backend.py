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
        program_type = data.get('program_type', 'sayisal')
        
        # Geçici mock response - gerçek ML model buraya gelecek
        mock_results = [
            {"department": "Bilgisayar Mühendisliği", "score": 0.95},
            {"department": "Yazılım Mühendisliği", "score": 0.92},
            {"department": "Endüstri Mühendisliği", "score": 0.88}
        ]
        
        return jsonify({
            'success': True,
            'recommendations': mock_results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
    