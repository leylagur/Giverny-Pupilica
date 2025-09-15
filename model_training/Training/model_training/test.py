import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle

# Model path
model_path = "../models/department_recommendation_model"

print("Model yükleniyor...")
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    
    with open(f"{model_path}/label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    
    print("Model başarıyla yüklendi!")
    
    # Test fonksiyonu
    def predict(text):
        inputs = tokenizer(text, return_tensors="pt", max_length=256, truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_id = predictions.argmax().item()
            confidence = predictions.max().item()
            department = label_encoder.inverse_transform([predicted_id])[0]
        return department, confidence
    
    # Test örnekleri
    tests = [
        "İlgi alanlarım: teknoloji, matematik. YKS sıralaması: 200000",
        "İlgi alanlarım: sağlık, hasta bakımı. YKS sıralaması: 400000", 
        "İlgi alanlarım: sanat, tasarım. YKS sıralaması: 600000"
    ]
    
    for i, test_input in enumerate(tests, 1):
        result, conf = predict(test_input)
        print(f"\nTest {i}:")
        print(f"Input: {test_input}")
        print(f"Prediction: {result}")
        print(f"Confidence: {conf:.4f}")
        
except Exception as e:
    print(f"Hata: {e}")