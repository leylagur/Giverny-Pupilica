# BölümBul

**Yapay Zeka Destekli Üniversite Bölüm Önerme Platformu**

BölümBul, öğrencilerin ilgi alanlarına göre en uygun üniversite bölümlerini keşfetmelerini sağlayan modern bir web uygulamasıdır. Machine learning algoritmaları kullanarak kişiselleştirilmiş bölüm önerileri sunar.

## Özellikler

### Frontend
- **Modern React UI** - Framer Motion animasyonları ile
- **Responsive Tasarım** - Mobil ve desktop uyumlu
- **Dark/Light Theme** - Kullanıcı tercihi
- **Real-time Typing Indicator** - Kullanıcı etkileşimi
- **Program Türü Seçimi** - 2 Yıllık, 4 Yıllık Sayısal/Sözel/Eşit Ağırlık
- **Animated Background** - Hareketli üniversite isimleri ve partiküller
- **Progressive Result Cards** - Staggered loading animasyonları

### Backend
- **Python Flask API** - RESTful servis mimarisi
- **Machine Learning Model** - Similarity-based recommendation
- **Multi-System Support** - Hybrid recommendation engine
- **Data Processing Pipeline** - CSV verilerinden model eğitimi
- **Program-Specific Results** - Her program türü için ayrı model

## Teknoloji Stack

### Frontend
- React 18
- Framer Motion (animasyonlar)
- Axios (API calls)
- CSS3 (modern styling)

### Backend
- Python 3.9+
- Flask (web framework)
- Pandas (veri işleme)
- Scikit-learn (ML modelleri)
- NumPy (numerik hesaplamalar)

## Proje Yapısı

```
BölümBul/
├── Backend/
│   ├── models/
│   │   ├── hybrid_engine.py
│   │   ├── multi_system.py
│   │   └── __init__.py
│   ├── Data/
│   │   ├── 2yillik_Bolumler_aciklamali_yeni.csv
│   │   ├── Sayisal_Bolumler_Aciklamali.csv
│   │   ├── Sozel_Bolumler_aciklamali.csv
│   │   └── Esit_Agirlik_Aciklamali.csv
│   └── Backend.py
├── Training/
│   └── model_training/
│       └── Similarity_Prompt.py
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   └── package.json
└── README.md
```

## Kurulum ve Çalıştırma

### Backend Kurulumu

```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Gerekli paketleri yükle
pip install flask pandas scikit-learn numpy flask-cors

# Backend'i çalıştır
python Backend.py
```

### Frontend Kurulumu

```bash
# Frontend klasörüne git
cd frontend

# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm start
```

## Veri Kaynağı

Üniversite ve bölüm verileri:
- **YÖK (Yükseköğretim Kurulu)** resmi verileri
- **Üniversite yerleştirme istatistikleri**
- **Veri derlemesi**: Salim Ünsal tarafından toplanmış veriler

## Machine Learning Yaklaşımı

### Similarity-Based Recommendation
- **TF-IDF Vectorization** - Metin analizi
- **Cosine Similarity** - Benzerlik hesaplama
- **Keyword Extraction** - Anahtar kelime çıkarımı
- **Multi-Program Support** - Program türüne göre özelleştirme

### Model Eğitimi
```python
# Veri önişleme
keywords → TF-IDF Matrix → Similarity Scores → Ranking
```

## UI/UX Özellikleri

### Animasyonlar
- **Page Load Animation** - Smooth giriş efekti
- **University Names** - Floating background animation
- **Result Cards** - Staggered reveal
- **Score Bars** - Progressive fill animation
- **Hover Effects** - Interactive micro-animations

### Tema Sistemi
- **Dark Mode** - Varsayılan koyu tema
- **Light Mode** - Aydınlık alternatif
- **Theme Toggle** - Kullanıcı kontrolü

## Responsive Tasarım

- **Mobile First** yaklaşımı
- **Tablet** optimizasyonu
- **Desktop** full-feature deneyimi
- **Flexible Grid** sistem

## API Endpoints

### POST /predict
```json
{
  "keywords": "matematik, bilgisayar, analiz",
  "program_type": "sayisal"
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "department": "Bilgisayar Mühendisliği",
      "score": 0.95
    }
  ]
}
```

## Geliştirme Süreci

1. **Veri Analizi** - YÖK verilerinin incelenmesi
2. **Model Geliştirme** - ML algoritması tasarımı
3. **Backend API** - Flask servis geliştirme
4. **Frontend UI** - React arayüz tasarımı
5. **Integration** - Full-stack entegrasyon
6. **Testing** - Kullanıcı deneyimi testleri

## Performans

- **Response Time**: < 500ms
- **Accuracy**: Yüksek similarity scoring
- **Scalability**: Modüler mimari
- **User Experience**: Smooth animasyonlar

## Gelecek Planları

- **User Accounts** - Kişisel profil sistemi
- **Detailed Analytics** - Gelişmiş analiz
- **University Integration** - Üniversite detay sayfaları
- **Mobile App** - React Native uygulaması
- **Advanced ML** - Deep learning modelleri

## Takım

**Hackathon Projesi 2025**
- Frontend Development: React, UI/UX Design
- Backend Development: Python, ML Engineering
- Data Science: Model optimization, Analysis

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Kesin kararlar için resmi kaynaklara başvurunuz.

## İletişim

Proje hakkında sorularınız için repository'nin katkı sağlayıcılarıyla iletişime geçebilirsiniz.

---

**Built with AI for better education decisions**
