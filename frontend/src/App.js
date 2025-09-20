import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [keywords, setKeywords] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('sayisal');

  const programTypes = {
    'onyillik': '2 Yıllık Önlisans',
    'sayisal': '4 Yıllık Sayısal',
    'sozel': '4 Yıllık Sözel',
    'esit_agirlik': '4 Yıllık Eşit Ağırlık'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!keywords.trim()) {
      setError('Lütfen ilgi alanlarınızı yazın!');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.post('http://127.0.0.1:8000/predict', {
        keywords: keywords.trim(),
        program_type: selectedProgram
      });

      if (response.data.success) {
        setResults(response.data.recommendations || []);
      } else {
        setError(response.data.error || 'Bir hata oluştu');
      }
    } catch (error) {
      console.error('API Hatası:', error);
      setError('Sunucuya bağlanırken hata oluştu. Backend çalışıyor mu?');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setKeywords('');
    setResults([]);
    setError('');
  };

  const getResultTitle = () => {
    return `${programTypes[selectedProgram]} Bölümleri`;
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🎓 Pupilica</h1>
          <p>İlgi alanlarınıza göre size en uygun bölümleri öneriyoruz</p>
        </header>

        <main className="main-content">
          <form onSubmit={handleSubmit} className="input-form">
            {/* Program Seçimi */}
            <div className="input-group">
              <label>Program Türü Seçin</label>
              <div className="program-selector">
                {Object.entries(programTypes).map(([key, label]) => (
                  <div key={key} className="program-option">
                    <input
                      type="radio"
                      id={key}
                      name="program"
                      value={key}
                      checked={selectedProgram === key}
                      onChange={(e) => setSelectedProgram(e.target.value)}
                    />
                    <label htmlFor={key} className="program-label">
                      {label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Kelime Girişi */}
            <div className="input-group">
              <label htmlFor="keywords">İlgi Alanlarınız</label>
              <textarea
                id="keywords"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="İlgi alanlarınızı yazın... 
Örnek: matematik, bilgisayar, tasarım, analiz, problem çözme, sanat"
                rows={4}
                className={error ? 'error' : ''}
              />
              {error && <span className="error-message">{error}</span>}
            </div>

            <div className="button-group">
              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Analiz Ediliyor...
                  </>
                ) : (
                  '🔍 Bölüm Öner'
                )}
              </button>
              {(keywords || results.length > 0) && (
                <button type="button" onClick={handleClear} className="clear-btn">
                  🗑️ Temizle
                </button>
              )}
            </div>
          </form>

          {results.length > 0 && (
            <div className="results-section">
              <h2>📋 {getResultTitle()}</h2>
              <div className="results-info">
                <span className="program-badge">{programTypes[selectedProgram]}</span>
                <span className="result-count">{results.length} sonuç bulundu</span>
              </div>
              <div className="results-grid">
                {results.map((result, index) => (
                  <div key={index} className="result-card">
                    <div className="result-content">
                      <h3 className="department-name">{result.department}</h3>
                      <div className="score-container">
                        <div className="score-bar">
                          <div 
                            className="score-fill" 
                            style={{ width: `${result.score * 100}%` }}
                          ></div>
                        </div>
                        <span className="score-text">
                          {(result.score * 100).toFixed(1)}% uyum
                        </span>
                      </div>
                    </div>
                    <div className="result-rank">#{index + 1}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.length === 0 && !loading && keywords && !error && (
            <div className="no-results">
              <p>🤔 Bu anahtar kelimeler için {programTypes[selectedProgram].toLowerCase()} bölümü bulunamadı. Farklı kelimeler deneyin!</p>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>💡 Daha iyi sonuçlar için spesifik kelimeler kullanın</p>
          <p>📊 Seçili: {programTypes[selectedProgram]}</p>
        </footer>
      </div>
    </div>
  );
}

export default App;