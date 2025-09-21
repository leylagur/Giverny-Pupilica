import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [keywords, setKeywords] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('sayisal');
  const [isTyping, setIsTyping] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  
  const toggleTheme = () => {
    setDarkMode(prev => !prev);
  };

  const programTypes = {
    '2_yillik': '2 Yıllık Önlisans',
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
      const response = await axios.post('http://127.0.0.1:8000/api/recommend', {
        user_input: keywords.trim(),
        dataset_type: selectedProgram,
        top_k: 6
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

  const handleInputChange = (e) => {
    setKeywords(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };

  const handleClear = () => {
    setKeywords('');
    setResults([]);
    setError('');
    setIsTyping(false);
  };

  return (
    <div className={`App ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <motion.div 
        className="container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        {/* Background Animation */}
        <div className="background-animation">
          {[...Array(40)].map((_, i) => (
            <motion.div
              key={i}
              className="floating-particle"
              animate={{
                y: [0, -120, 0],
                x: [0, Math.sin(i) * 50, 0],
                opacity: [0.1, 0.4, 0.1],
              }}
              transition={{
                duration: 15 + Math.random() * 10,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.1
              }}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`
              }}
            />
          ))}
          
          {/* University Names */}
            <div className="university-names">
              {[
                'İTÜ', 'ODTÜ', 'Boğaziçi', 'YTÜ', 'Bilkent', 'Koç', 'Sabancı',
                'Hacettepe', 'Ankara', 'Gazi', 'Marmara', 'İstanbul', 'Ege', 
                'Dokuz Eylül', 'Çukurova', 'Erciyes', 'Akdeniz', 'Hitit',
                'Selçuk', 'Atatürk', 'Fırat', 'İnönü', 'Mersin', 'Pamukkale',
                'Karadeniz Teknik', 'Uludağ', 'Anadolu', 'Eskişehir Osmangazi'
              ].map((uni, index) => (
                <motion.span
                  key={`university-${index}`}
                  className="university-name"
                  animate={{
                    x: [0, Math.sin(index * 0.5) * 40, 0],
                    y: [0, Math.cos(index * 0.3) * 30, 0],
                    opacity: [0.15, 0.35, 0.15],
                    scale: [0.95, 1.05, 0.95],
                    rotateZ: [0, 5, 0, -5, 0]
                  }}
                  transition={{
                    duration: 12 + (index % 5) * 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: index * 0.3
                  }}
                  style={{
                    position: 'absolute',
                    left: `${(index % 6) * 16 + 5}%`,
                    top: `${Math.floor(index / 6) * 20 + 15}%`,
                    fontSize: `${1.8 + Math.random() * 0.6}rem`,
                    color: '#64748b',
                    opacity: 0.25,
                    fontWeight: '300',
                    transform: `rotate(${(Math.random() - 0.5) * 15}deg)`,
                    userSelect: 'none',
                    pointerEvents: 'none'
                  }}
                >
                  {uni}
                </motion.span>
              ))}
            </div>
        </div>
          {/* Hero Section */}
          <section className="hero">
            <motion.button
              onClick={toggleTheme}
              className="theme-toggle"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              {darkMode ? '☀️' : '🌙'}
            </motion.button>

            <motion.div 
              className="hero-content"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
            <h1 className="hero-title">
              <span className="gradient-text">BölümBul</span>
              <br />
              Geleceğiniz için doğru bölümü keşfedin
            </h1>
            <p className="hero-subtitle">
              Yapay zeka destekli platform ile ilgi alanlarınıza en uygun
              <br />
              üniversite bölümlerini bulun
            </p>
          </motion.div>

          {/* Main Search Section */}
          <motion.div 
            className="search-section"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {/* Program Type Selector */}
            <div className="program-tabs">
              {Object.entries(programTypes).map(([key, label]) => (
                <motion.button
                  key={key}
                  className={`program-tab ${selectedProgram === key ? 'active' : ''}`}
                  onClick={() => setSelectedProgram(key)}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ duration: 0.2 }}
                >
                  {label}
                </motion.button>
              ))}
            </div>

            {/* Main Search Bar */}
            <form onSubmit={handleSubmit} className="search-form">
              <div className="search-container">
                <motion.div 
                  className="search-input-wrapper"
                  animate={{ 
                    boxShadow: isTyping 
                      ? "0 0 0 2px rgba(99, 102, 241, 0.3), 0 0 20px rgba(99, 102, 241, 0.1)" 
                      : "0 0 0 0px rgba(99, 102, 241, 0.2)"
                  }}
                  transition={{ duration: 0.3 }}
                >
                  <input
                    type="text"
                    value={keywords}
                    onChange={handleInputChange}
                    placeholder="İlgi alanlarınızı yazın... (matematik, tasarım, teknoloji)"
                    className="search-input"
                  />
                  
                  {isTyping && (
                    <motion.div 
                      className="typing-indicator"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="typing-dots">
                        <motion.span
                          animate={{ scale: [1, 1.3, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                        />
                        <motion.span
                          animate={{ scale: [1, 1.3, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                        />
                        <motion.span
                          animate={{ scale: [1, 1.3, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                        />
                      </div>
                    </motion.div>
                  )}
                </motion.div>

                <motion.button
                  type="submit"
                  disabled={loading || !keywords.trim()}
                  className="search-button"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ duration: 0.2 }}
                >
                  {loading ? (
                    <motion.div 
                      className="loading-spinner"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                  ) : (
                    'Bölümleri Keşfet'
                  )}
                </motion.button>
              </div>
            </form>

            {error && (
              <motion.div 
                className="error-message"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {error}
              </motion.div>
            )}
          </motion.div>
        </section>

        {/* Results Section */}
        <AnimatePresence mode="wait">
          {results.length > 0 && (
            <motion.section 
              className="results-section"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.6 }}
            >
              <div className="results-header">
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  Önerilen Bölümler
                </motion.h2>
                <motion.div 
                  className="results-meta"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <span className="program-badge">{programTypes[selectedProgram]}</span>
                  <span className="result-count">{results.length} sonuç</span>
                </motion.div>
              </div>

              <motion.div 
                className="results-grid"
                initial="hidden"
                animate="visible"
                variants={{
                  visible: {
                    transition: {
                      staggerChildren: 0.1
                    }
                  }
                }}
              >
                {results.map((result, index) => (
                  <motion.div
                    key={`${result.bolum_adi}-${index}`}
                    className="result-card"
                    variants={{
                      hidden: { opacity: 0, y: 30, scale: 0.9 },
                      visible: { opacity: 1, y: 0, scale: 1 }
                    }}
                    whileHover={{ 
                      y: -10,
                      scale: 1.02,
                      transition: { duration: 0.3 }
                    }}
                    transition={{ duration: 0.4 }}
                  >
                    <motion.div 
                      className="result-rank"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.5 + index * 0.1, type: "spring" }}
                    >
                      #{index + 1}
                    </motion.div>

                    <h3 className="result-title">{result.bolum_adi}</h3>

                    <div className="result-details">
                      <div className="university-info">
                        <span className="university-name">{result.universite}</span>
                        <span className="city-name">{result.sehir}</span>
                      </div>
                      
                     {result.ranking_2025 && (
                      <div className="ranking-info">
                        <span className="ranking-label">2025 Sıralaması:</span>
                        <span className="ranking-value">{result.ranking_2025.toLocaleString('tr-TR')}</span>
                      </div>
                    )}

                    {result.taban_puan && (
                      <div className="ranking-info">
                        <span className="ranking-label">Taban Puan:</span>
                        <span className="taban-puan-value">{result.taban_puan}</span>
                      </div>
                    )}

                    </div>
                    
                    <div className="result-score">
                      <div className="score-bar">
                        <motion.div
                          className="score-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${result.similarity_score * 100}%` }}
                          transition={{ 
                            duration: 1.5, 
                            delay: 0.5 + index * 0.1,
                            ease: "easeOut"
                          }}
                        />
                      </div>
                      <motion.span 
                        className="score-text"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1 + index * 0.1 }}
                      >
                        {(result.similarity_score * 100).toFixed(0)}% uyum
                      </motion.span>
                    </div>
                  </motion.div>
                ))}
              </motion.div>

              <motion.button
                onClick={handleClear}
                className="clear-button"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.4 }}
              >
                Yeni Arama Yap
              </motion.button>
            </motion.section>
          )}
        </AnimatePresence>
        {/* Footer */}
          <footer className="app-footer">
            <div className="footer-content">
              <div className="footer-main">
                <h3>BölümBul</h3>
                <p>Yapay zeka destekli üniversite bölüm önerme platformu</p>
              </div>
              
              <div className="footer-credits">
                <p>Powered by <strong>Pupilica</strong> </p>
                <p className="disclaimer">
                   Bu projede Salim Ünsal'ın derlediği veriler kullanılmıştır
                </p>
                <p className="disclaimer">
                  Bu platform eğitim amaçlı geliştirilmiştir. Kesin kararlar için resmi kaynaklara başvurunuz.
                </p>
              </div>
            </div>
          </footer>
      </motion.div>
    </div>
  );
}


export default App;