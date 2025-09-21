import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatWidget.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      type: 'bot', 
      text: 'Merhaba! Ben BölümBul asistanınızım. Bölüm seçimi hakkında size nasıl yardımcı olabilirim?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userProfile, setUserProfile] = useState({
    interests: [],
    strengths: [],
    concerns: [],
    previousQuestions: []
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Kapsamlı cevap sistemi
  const generateBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Kullanıcı profilini güncelle
    setUserProfile(prev => ({
      ...prev,
      previousQuestions: [...prev.previousQuestions, lowerMessage]
    }));

    // 1. MAAŞ VE PARA KAZANDIRAN BÖLÜMLER
    if (lowerMessage.includes('para kazandıran') || lowerMessage.includes('maaşı yüksek') || lowerMessage.includes('en çok para') || lowerMessage.includes('kazanç')) {
      return `💰 **En Yüksek Maaşlı Bölümler (2024 verileri):**

**Tıp Alanları:** (₺15.000 - ₺50.000+)
• Beyin Cerrahisi, Kalp Cerrahisi, Anestezi
• Radyoloji, Dermatoloji, Göz Hastalıkları

**Mühendislik:** (₺12.000 - ₺35.000)
• Yazılım/Bilgisayar Mühendisliği (özellikle AI/ML)
• Petrol/Maden Mühendisliği
• Endüstri Mühendisliği (büyük şirketlerde)

**Finans/İş Dünyası:** (₺10.000 - ₺40.000+)
• Yatırım Bankacılığı, Risk Yönetimi
• Aktüerya, Ekonometri
• MBA + deneyim kombinasyonu

**Teknoloji:** (₺8.000 - ₺30.000)
• Veri Bilimi, Siber Güvenlik
• DevOps, Cloud Mimarı

⚠️ **Dikkat:** Maaş sadece mesleğe değil, deneyim, şirket ve lokasyona da bağlı. Tutkulu olduğunuz alanı seçerseniz hem daha başarılı olur hem de maaşınız artar!

Hangi alanda çalışmayı hayal ediyorsunuz?`;
    }

    // 2. MÜHENDİSLİK VS TIP KARŞILAŞTIRMASI
    if ((lowerMessage.includes('mühendislik') && lowerMessage.includes('tıp')) || 
        lowerMessage.includes('mühendislik mi tıp mi')) {
      return `🏥⚙️ **Mühendislik vs Tıp - Detaylı Karşılaştırma:**

**TIP FAKÜLTESİ:**
✅ **Artıları:**
• Çok prestijli ve saygın meslek
• Yüksek ve garantili gelir (₺15K-50K+)
• İnsanlara doğrudan yardım etme hissi
• İş garantisi (her zaman doktor lazım)

❌ **Eksileri:**
• 6 yıl + 4-6 yıl uzmanlık = 10-12 yıl
• Çok yüksek YKS puanı gerekli (480K+)
• Çok stresli ve yorucu meslek
• Mesai saatleri düzensiz

**MÜHENDİSLİK:**
✅ **Artıları:**
• 4 yıl eğitim, hızlıca iş hayatına
• Çok çeşitli sektör seçenekleri
• Teknoloji ile iç içe (gelişen alan)
• Yaratıcılık + analitik düşünce

❌ **Eksileri:**
• Sürekli kendini güncelleme gerekli
• Bazı dallar doygun (makine, inşaat)
• Maaş başlangıçta düşük olabilir

**KARAR VERMENİZ İÇİN SORULAR:**
1. Matematik/Fizik mi yoksa Biyoloji/Kimya mı daha kolay geliyor?
2. 12 yıl eğitime katlanabilir misiniz?
3. İnsan hayatına dokunmak mı yoksa teknoloji geliştirmek mi daha çekici?

Hangi yönde eğiliminiz var?`;
    }

    // 3. KARARSIZLIK VE BÖLÜM SEÇİMİ REHBERİ
    if (lowerMessage.includes('kararsız') || lowerMessage.includes('seçemiyorum') || 
        lowerMessage.includes('ne seçmeli') || lowerMessage.includes('bilmiyorum')) {
      return `🤔 **Bölüm Seçiminde Kararsızlık Çok Normal! Size Rehberlik Edeyim:**

**1. KENDİNİZİ TANIMAK:**
📚 **En sevdiğiniz dersler neler?**
• Matematik-Fizik → Mühendislik, Fen
• Biyoloji-Kimya → Tıp, Eczacılık, Veteriner
• Edebiyat-Tarih → Hukuk, Öğretmenlik, Gazetecilik
• Coğrafya-Sosyal → İşletme, Turizm, Uluslararası İlişkiler

🎯 **2. KİŞİLİK ANALİZİ:**
• **İnsanlarla mı çalışmayı seviyorsunuz?** → Öğretmenlik, Psikoloji, Hukuk
• **Yalnız çalışmayı mı?** → Programlama, Grafik Tasarım, Muhasebe
• **Pratik işler mi teorik mi?** → Mühendislik vs Akademik alanlar

💰 **3. GELECEK HEDEFLERİ:**
• Ne kadar maaş hedefliyorsunuz?
• Hangi şehirde yaşamak istiyorsunuz?
• Kaç yıl eğitim almaya hazırsınız?

**HEMEN YAPILACAKLAR:**
✨ Meslek mensubu tanıdıklarınızla konuşun
✨ Üniversite tanıtım günlerine katılın  
✨ YouTube'da "Bir günüm" videolarını izleyin
✨ İnternetten meslek testleri yapın

**Size özel öneri verebilmem için hangi konularda daha güçlüsünüz söyleyebilir misiniz?**`;
    }

    // 4. ÜNİVERSİTE KARŞILAŞTIRMALARI
    if (lowerMessage.includes('hangi üniversite') || lowerMessage.includes('en iyi üniversite') ||
        lowerMessage.includes('üniversite öner')) {
      return `🏛️ **Türkiye'nin En İyi Üniversiteleri (2024 Sıralaması):**

**🥇 SÜPER LİG (Dünya Çapında Tanınan):**
• **Boğaziçi:** İngilizce eğitim, çok güçlü mezun ağı, sosyal bilimler + mühendislik
• **ODTÜ:** Mühendislik + fen bilimleri zirvesi, kampüs yaşamı harika
• **İTÜ:** En köklü teknik üniversite, mühendislik + mimarlık

**🥈 1. LİG (Çok Kaliteli):**
• **Koç/Sabancı:** Özel, İngilizce, küçük sınıflar, burslu eğitim
• **Hacettepe:** Tıp + fen bilimleri güçlü
• **İstanbul Üniversitesi:** Köklü, özellikle tıp + hukuk
• **Gazi:** Öğretmenlik + mühendislik
• **Bilkent:** Teknoloji + işletme

**🥉 BÖLGESEL LİDERLER:**
• **Ege, Dokuz Eylül (İzmir):** Batı'nın kaliteli seçenekleri
• **Erciyes (Kayseri):** Anadolu'nun yükselen yıldızı
• **KTÜ (Trabzon):** Karadeniz'in teknik üniversitesi

**BÖLÜM SEÇİMİ ÖNERİLERİ:**
🔥 **Teknoloji → Boğaziçi, ODTÜ, İTÜ, Bilkent**
🏥 **Tıp → Hacettepe, İÜ, Ege, Akdeniz**
⚖️ **Hukuk → İÜ, Ankara, Marmara, Galatasaray**
🏢 **İşletme → Boğaziçi, Koç, Sabancı, İÜ**

Hangi bölüm alanı sizi daha çok ilgilendiriyor? Size o alana göre detaylı üniversite önerisi yapabilirim!`;
    }

    // 5. MATEMATIK ZOR GELİYOR PROBLEMİ
    if (lowerMessage.includes('matematik zor') || lowerMessage.includes('matematik sevmiyorum') ||
        lowerMessage.includes('sayısal zor')) {
      return `📚 **Matematik Zorlanıyorsanız Panik Yok! Birçok Harika Seçenek Var:**

**🎨 SOSYAL VE SANAT ALANLARI:**
• **Hukuk:** Mantıklı düşünme yetisi yeterli, matematik minimal
• **Psikoloji:** İnsan davranışları, istatistik temel düzeyde
• **Türk Dili ve Edebiyatı:** Yaratıcılık + dil becerileri
• **Tarih:** Araştırma + analiz yeteneği
• **Gazetecilik:** İletişim + güncel olayları takip

**💼 İŞ DÜNYASI (Az Matematik):**
• **İşletme:** Temel matematik, daha çok strateji
• **Uluslararası İlişkiler:** Dil + diplomasi
• **Turizm İşletmeciliği:** İnsan ilişkileri + organizasyon
• **Reklamcılık:** Yaratıcılık + pazarlama

**🏥 SAĞLIK (Biyoloji Ağırlıklı):**
• **Hemşirelik:** Tıbbi bilgi + hasta bakımı
• **Fizyoterapi:** Anatomi + rehabilitasyon
• **Beslenme ve Diyetetik:** Sağlık + beslenme bilimi

**🎭 SANAT VE TASARIM:**
• **Grafik Tasarım:** Yaratıcılık + teknoloji
• **İç Mimarlık:** Estetik + fonksiyonellik
• **Müzik/Resim:** Sanatsal yetenek

**💡 ÖNEMLİ NOT:** Matematik zorlanmanız başarısız olacağınız anlamına gelmez! Birçok başarılı hukukçu, gazeteci, psikolog matematik konusunda zorlanmıştı.

**Hangi alanlar daha çok ilginizi çekiyor? Detayına inelim!**`;
    }

    // 6. ÜNİVERSİTE HAYATI VE KAMPÜS SORULARI
    if (lowerMessage.includes('üniversite hayatı') || lowerMessage.includes('kampüs') || 
        lowerMessage.includes('sosyal yaşam')) {
      return `🎓 **Üniversite Hayatı ve Kampüs Rehberi:**

**🏕️ EN İYİ KAMPÜS YAŞAMI:**
• **ODTÜ:** 4500 dönüm orman içi, bisiklet yolları, çok aktif öğrenci kulüpleri
• **Boğaziçi:** Boğaz manzarası, tarihi yapılar, şehir merkezine yakın
• **İTÜ:** Şehir kampüsü, sosyal aktiviteler bol
• **Bilkent:** Modern kampüs, spor tesisleri

**🎉 SOSYAL AKTİVİTELER:**
• **Öğrenci kulüpleri:** Dans, müzik, spor, teknoloji...
• **Festivaller:** ODTÜ Kültür Festival, Boğaziçi Bahar Şenlikleri
• **Spor:** Futbol, basketbol, yüzme havuzları
• **Konserler ve etkinlikler**

**🏠 BARINMA SEÇENEKLERİ:**
• **Devlet yurdu:** En ucuz (₺200-500/ay)
• **Özel yurt:** Daha konforlu (₺800-2000/ay)
• **Ev paylaşımı:** Arkadaşlarla (₺1000-3000/ay)
• **Ailede kalma:** Şehir içi üniversiteler

**💰 AYLIK GİDERLER (Ortalama):**
• Yemek: ₺1500-3000
• Ulaşım: ₺200-500
• Sosyal aktivite: ₺500-1500
• Kırtasiye: ₺200-400

**📚 AKADEMİK HAYAT:**
• Dersler genelde sabah 8-akşam 6 arası
• Ödevler, projeler, sınavlar
• Hocalarla ofis saatleri
• Kütüphane çalışması

Hangi şehirde üniversite okumayı planlıyorsunuz?`;
    }

    // 7. İŞ İMKANLARI VE GELECEK
    if (lowerMessage.includes('iş imkan') || lowerMessage.includes('istihdam') || 
        lowerMessage.includes('gelecek') || lowerMessage.includes('kariyer')) {
      return `🚀 **2024-2030 Arası En Çok İş İmkanı Olan Alanlar:**

**📱 TEKNOLOJİ (Çok Yüksek Talep):**
• **Yapay Zeka/Makine Öğrenmesi:** Maaş ₺15K-40K
• **Siber Güvenlik Uzmanı:** Çok aranıyor, ₺12K-35K
• **Veri Bilimci:** Her sektörde gerekli, ₺10K-30K
• **Mobil/Web Developer:** Freelance imkanı da var
• **DevOps/Cloud:** Infrastructure uzmanları

**🏥 SAĞLIK (Sürekli İhtiyaç):**
• **Hemşire:** Avrupa'da da çalışma imkanı
• **Fizyoterapist:** Yaşlanan nüfus, spor sektörü
• **Beslenme Uzmanı:** Sağlıklı yaşam trendi
• **Tıbbi Sekreter:** Hastanelerde çok aranıyor

**🎓 EĞİTİM (Garantili İstihdam):**
• **Matematik/Fen Öğretmeni:** Her zaman açık var
• **İngilizce Öğretmeni:** Özel sektörde de geçerli
• **Okul Öncesi Öğretmeni:** 0-6 yaş eğitimi zorunlu

**💼 İŞ DÜNYASI:**
• **Dijital Pazarlama:** E-ticaret büyüyor
• **İnsan Kaynakları:** Her şirkette gerekli
• **Satış Uzmanı:** Deneyimle çok iyi maaş
• **Muhasebe:** TÜRMOB sertifikası ile garanti

**🌱 YENİ SEKTÖRLER:**
• **Çevre Mühendisliği:** Sürdürülebilirlik trendi
• **Yenilenebilir Enerji:** Güneş, rüzgar santralleri
• **E-spor:** Oyun sektörü büyüyor
• **İçerik Üretimi:** YouTube, sosyal medya

**💡 TAVSİYE:** Hangi bölümü seçerseniz seçin, kendinizi sürekli geliştirin. Sertifikalar alın, staj yapın, network kurun!

Hangi sektör daha çok ilginizi çekiyor?`;
    }

    // 8. YKS VE PUAN SORULARI
    if (lowerMessage.includes('yks') || lowerMessage.includes('puan') || lowerMessage.includes('sınav')) {
      return `📊 **YKS 2024 Puan Rehberi ve Strateji:**

**🎯 PUAN ARALIĞI STRATEJİLERİ:**

**🥇 SÜPER LİG (450K+ Puan):**
• Boğaziçi, ODTÜ, İTÜ tıp/mühendislik
• Günde 8-10 saat çalışma gerekli
• **Strateji:** AYT'ye ağırlık, TYT'yi sağlama alın

**🥈 1. LİG (300K-450K):**
• İyi devlet üniversiteleri, güzel bölümler
• Günde 6-8 saat düzenli çalışma
• **Strateji:** Dengeli çalışma, eksik konuları kapatın

**🥉 2. LİG (150K-300K):**
• Devlet üniversiteleri, 2 yıllık programlar
• Günde 4-6 saat çalışma
• **Strateji:** TYT'ye odaklanın, temel konuları sağlamlaştırın

**📚 ÇALIŞMA TAKVİMİ:**
• **Eylül-Ocak:** Konu anlatım + soru çözümü
• **Şubat-Nisan:** Deneme sınavları + eksik kapatma
• **Mayıs-Haziran:** Son tekrar + psikolojik hazırlık

**📈 PUAN ARTIRMA İPUÇLARI:**
✅ **TYT'de 100+ doğru** yapın (çok kritik!)
✅ **Matematik-Fen** ağırlık verin (katsayı yüksek)
✅ **Deneme sınavları** düzenli çözün
✅ **Zayıf dersleri** ihmal etmeyin
✅ **Soru bankası** + **video dersler** kombinasyonu

**⚠️ ÖNEMLİ:** Hedef belirlemek motivasyon sağlar! Hangi puan aralığını hedefliyorsunuz? Size uygun strateji önerebilirim.

Şu anki durumunuz nasıl? Hangi derslerde zorlanıyorsunuz?`;
    }

    // 9. MESLEKİ EĞİTİM VE ÖNLISANS
    if (lowerMessage.includes('2 yıllık') || lowerMessage.includes('önlisans') || 
        lowerMessage.includes('meslek yüksekokulu') || lowerMessage.includes('myo')) {
      return `🎓 **Önlisans/Meslek Yüksekokulu - Hızlıca İş Hayatına Atılın!**

**💼 EN POPÜLER VE İŞ GARANTİLİ BÖLÜMLER:**

**💻 BİLİŞİM TEKNOLOJİLERİ:**
• **Bilgisayar Programcılığı:** Web/mobil geliştirme
• **Bilişim Güvenliği:** Siber güvenlik uzmanı
• **Veri Tabanı Yönetimi:** SQL, veri analizi
• **Maaş:** ₺6K-20K (deneyimle artıyor)

**🏥 SAĞLIK HİZMETLERİ:**
• **Anestezi Teknisyeni:** Ameliyathane ekibi
• **Tıbbi Görüntüleme:** Röntgen, MR teknisyeni
• **Laboratuvar Teknisyeni:** Tahlil yapma
• **Maaş:** ₺5K-15K + devlet garantisi

**⚙️ TEKNİK ALANLAR:**
• **Makine Teknolojisi:** Üretim sektörü
• **Elektrik-Elektronik:** Enerji, telekomünikasyon
• **Otomotiv Teknolojisi:** Servis, üretim
• **İnşaat Teknolojisi:** Şantiye yönetimi

**💰 TİCARET VE YÖNETİM:**
• **Dış Ticaret:** İhracat-ithalat firmaları
• **Lojistik:** Kargo, depolama şirketleri
• **Muhasebe:** Her şirkette gerekli
• **Bankacılık:** Şube operasyonları

**✅ ÖNLİSANS AVANTAJLARI:**
• 2 yıl eğitim → Hızlıca iş hayatına
• Daha pratik, uygulamalı eğitim
• Staj zorunluluğu → İş bağlantıları
• Daha düşük puan ile giriş
• Çalışırken DGS ile lisans tamamlama

**📈 BAŞARILI OLMAK İÇİN:**
• Stajı ciddiye alın
• Sertifikalar edinin
• Sektörel fuarlara katılın
• Network kurun

Hangi alan daha çok ilginizi çekiyor?`;
    }

    // 10. ÖZEL VE DEVLET ÜNİVERSİTESİ
    if (lowerMessage.includes('özel üniversite') || lowerMessage.includes('devlet üniversite') ||
        lowerMessage.includes('özel mi devlet mi')) {
      return `🏛️ **Özel vs Devlet Üniversitesi - Detaylı Karşılaştırma:**

**🎓 DEVLET ÜNİVERSİTESİ:**
✅ **Artıları:**
• **Çok düşük harç:** Yılda sadece ₺1000-2000
• **Prestijli olanlar var:** ODTÜ, Boğaziçi, İTÜ
• **Geniş kampüs:** Sosyal aktiviteler, kulüpler
• **Çok öğrenci:** Geniş arkadaş çevresi
• **Araştırma imkanları:** Akademik kariyer için ideal

❌ **Eksileri:**
• **Kalabalık sınıflar:** 200-300 kişilik dersler
• **Hoca ilgisi sınırlı:** Bireysel takip zor
• **Bürokrasi:** İşlemler uzun sürebilir
• **Eskimiş alt yapı:** Bazı üniversitelerde

**🏢 ÖZEL ÜNİVERSİTE:**
✅ **Artıları:**
• **Küçük sınıflar:** 20-40 kişi, bireysel ilgi
• **Modern donanım:** Son teknoloji laboratuvarlar
• **İngilizce eğitim:** Uluslararası fırsatlar
• **Sektör bağlantıları:** İş imkanları daha kolay
• **Hızlı mezuniyet:** Müfredat optimize
• **Burs imkanları:** %25-100 burs olanakları

❌ **Eksileri:**
• **Yüksek maliyet:** Yılda ₺30K-150K
• **Prestij farkı:** Bazıları pek tanınmıyor
• **Sınırlı kampüs:** Sosyal aktiviteler az olabilir

**💰 MALİYET KARŞILAŞTIRMASI (4 yıl):**
• **Devlet:** ₺5K-10K (sadece harç)
• **Özel (burslu):** ₺30K-100K
• **Özel (burssuz):** ₺120K-600K

**🎯 HANGİSİNİ SEÇMELİSİNİZ?**

**Devlet üniversitesi seçin eğer:**
• Bütçeniz kısıtlı
• Prestijli bir bölüme girebiliyorsanız
• Akademik kariyer planlıyorsanız
• Sosyal yaşam önemli

**Özel üniversite seçin eğer:**
• Burs alabiliyorsanız
• Bireysel ilgi istiyorsanız
• İş dünyasına hızlıca atılmak istiyorsanız
• İngilizce eğitim önceliğiniz

Bütçeniz ve hedefleriniz neler?`;
    }

    // 11. GENEL SELAMLAMA VE KILAVUZLUK
    if (lowerMessage.includes('merhaba') || lowerMessage.includes('selam') || lowerMessage.includes('hey')) {
      return `Merhaba! 😊 BölümBul asistanınız olarak size yardım etmekten mutluluk duyarım. 

**Size nasıl yardımcı olabilirim?**
🎓 Bölüm seçimi danışmanlığı
🏛️ Üniversite karşılaştırmaları  
💰 Maaş ve kariyer bilgileri
📊 YKS strateji önerileri
🤔 Kararsızlık çözümleri

Hangi konuda kafanızda soru işaretleri var?`;
    }

    // 12. TEŞEKKÜR VE OLUMLU GERİ DÖNÜŞ
    if (lowerMessage.includes('teşekkür') || lowerMessage.includes('sağol') || lowerMessage.includes('yardım') || lowerMessage.includes('güzel')) {
      return `Çok memnun oldum yardımcı olabildiysem! 🌟 

Bölüm seçimi çok önemli bir karar ve doğru bilgiyle hareket etmeniz harika. Başka sorularınız olduğunda çekinmeyin.

**Unutmayın:** En iyi bölüm, sizin yetenekleriniz ve tutkularınızla uyumlu olandır. Size başarılar diliyorum! 🚀

Başka merak ettiğiniz bir konu var mı?`;
    }

    // 13. OLUMSUZ/STRES BELİRTİLERİ
    if (lowerMessage.includes('stres') || lowerMessage.includes('kaygı') || lowerMessage.includes('korku') || 
        lowerMessage.includes('başaramam') || lowerMessage.includes('zor')) {
      return `💪 **Stres ve Kaygılarınız Çok Normal! Beraber Çözelim:**

**🧠 BÖLÜM SEÇİMİ STRESI:**
Her gencin yaşadığı doğal bir süreç. Kendinizi yalnız hissetmeyin!

**✨ STRESİ AZALTMAK İÇİN:**
• **Bilgi edinin:** Belirsizlik stresi artırır
• **Küçük adımlar atın:** Büyük hedefi parçalayın
• **Konuşun:** Aile, öğretmen, arkadaşlarla paylaşın
• **Zamanınız var:** Aceleniz yok, düşünme fırsatınız çok

**🎯 DOĞRU BAKIŞ AÇISI:**
• "Mükemmel" seçim yoktur, "uygun" seçim vardır
• Hata yaparsanız da düzeltilebilir (yatay geçiş, çift anadal)
• Başarı = doğru seçim + çaba + tutku
• Her bölümden başarılı insanlar çıkıyor

**🌟 MOTİVASYON:**
Siz bu karaarı verebilecek kapasitedesiniz! Kendine güven ve adım adım ilerleyin.

Ne konuda en çok kaygı duyuyorsunuz? Beraber çözüm bulalım.`;
    }

    // 14. SPESIFIK BÖLÜM SORULARI - TEKNOLOJİ
    if (lowerMessage.includes('yazılım') || lowerMessage.includes('bilgisayar mühendisliği') || 
        lowerMessage.includes('programlama') || lowerMessage.includes('kod')) {
      return `💻 **Yazılım ve Bilgisayar Mühendisliği - Detaylı Rehber:**

**🚀 NEDEN BU ALAN?**
• En hızla büyüyen sektör (her yıl %15+ büyüme)
• Remote çalışma imkanı (dünyanın her yerinden)
• Sürekli öğrenme ve gelişim
• Yaratıcılık + mantık birleşimi

**🎓 EĞİTİM SEÇENEKLERİ:**
• **Bilgisayar Mühendisliği:** Daha teorik, algorithm ağırlıklı
• **Yazılım Mühendisliği:** Daha pratik, proje odaklı
• **Bilgisayar Programcılığı (2 yıllık):** Hızlıca iş hayatına

**💼 ÇALIŞMA ALANLARI:**
• **Frontend Developer:** Kullanıcı arayüzleri (React, Vue)
• **Backend Developer:** Sunucu tarafı (Node.js, Python, Java)
• **Mobile Developer:** Mobil uygulamalar (iOS, Android)
• **Game Developer:** Oyun geliştirme (Unity, Unreal)
• **AI/ML Engineer:** Yapay zeka, veri bilimi
• **DevOps Engineer:** Sistem yönetimi, cloud

**💰 MAAŞ BEKLENTİLERİ:**
• **Junior (0-2 yıl):** ₺8K-15K
• **Mid-level (2-5 yıl):** ₺15K-25K
• **Senior (5+ yıl):** ₺25K-40K+
• **Tech Lead/Architect:** ₺40K-60K+

**📚 ÖĞRENMENİZ GEREKENLER:**
• **Temel:** HTML, CSS, JavaScript
• **Backend:** Python, Java, C# seçeneklerinden biri
• **Database:** SQL, NoSQL
• **Versiyon Kontrol:** Git/GitHub
• **Cloud:** AWS, Google Cloud basics

**🏆 BAŞARILI OLMAK İÇİN:**
• Sürekli practice yapın (LeetCode, HackerRank)
• GitHub'da proje portföyü oluşturun
• Open source projelere katkıda bulunun
• Teknoloji topluluklarına katılın

Programlama deneyiminiz var mı? Hangi alanda uzmanlaşmak istiyorsunuz?`;
    }

    // 15. EĞİTİM FAKÜLTESİ VE ÖĞRETMENLİK
    if (lowerMessage.includes('öğretmen') || lowerMessage.includes('eğitim fakültesi') || 
        lowerMessage.includes('pedagoji') || lowerMessage.includes('öğretim')) {
      return `👨‍🏫 **Öğretmenlik - Geleceği Şekillendiren Meslek:**

**🌟 NEDEN ÖĞRETMENLİK?**
• Topluma doğrudan katkı
• İş garantisi (her zaman öğretmen ihtiyacı var)
• Düzenli mesai (tatiller guaranteed!)
• Maaş güvencesi + yan haklar
• Her gün yeni deneyimler

**📚 ÖĞRETMENLİK ALANLARI:**

**🔬 FEN BİLİMLERİ (Çok Aranıyor!):**
• **Matematik Öğretmenliği:** En çok açık olan alan
• **Fizik Öğretmenliği:** Lise düzeyinde yüksek maaş
• **Kimya/Biyoloji:** Laboratuvar imkanları

**🗣️ SOSYAL VE DİL:**
• **İngilizce Öğretmenliği:** Özel sektörde de çalışabilir
• **Türkçe Öğretmenliği:** Edebiyat severlere ideal
• **Tarih/Coğrafya:** Sosyal bilimler meraklıları

**🎨 ÖZEL ALANLAR:**
• **Okul Öncesi:** 0-6 yaş, çok sabır gerekli ama çok sevimli
• **Özel Eğitim:** Engelli bireylerle çalışma, çok anlamlı
• **Rehber Öğretmen:** Psikolojik danışmanlık

**💰 MAAŞ VE HAKLAR:**
• **Başlangıç:** ₺17.000 (2024)
• **Kıdemli:** ₺25.000+
• **Ek dersler:** +₺3.000-8.000
• **Tatiller:** Yaz, kış, sömestr tatilleri
• **Emeklilik:** 25 yıl hizmet

**📊 ATANMA DURUMLARI (2024):**
• **En kolay atanan:** Matematik, Fen, İngilizce
• **Orta zorluk:** Türkçe, Sosyal Bilimler
• **En zor:** Sınıf öğretmenliği, Okul öncesi

**✅ ÖĞRETMENLİK İÇİN GEREKLİ ÖZELLİKLER:**
• Sabırlı ve anlayışlı olma
• İletişim becerisi güçlü olma
• Sürekli öğrenmeye açık olma
• Liderlik ve organizasyon yetisi

**🎯 ALTERNATIF KARIYERLER:**
• Özel okullarda çalışma
• Dershane/etüt merkezi
• Online eğitim platformları
• Eğitim danışmanlığı
• Akademisyen olma

Hangi yaş grubu ve alan daha çok ilginizi çekiyor?`;
    }

    // 16. TIP FAKÜLTESİ DETAYLI
    if (lowerMessage.includes('tıp') || lowerMessage.includes('doktor') || lowerMessage.includes('hekim')) {
      return `🏥 **Tıp Fakültesi - En Prestijli Meslek Yolu:**

**⚕️ TIP FAKÜLTESİ SÜRECİ:**
• **6 yıl temel eğitim** (preklinik + klinik)
• **TUS sınavı** (uzmanlık için)
• **4-6 yıl uzmanlık** (dal seçimine göre)
• **Toplam süre:** 10-12 yıl

**📊 GİRİŞ ŞARTLARI (2024):**
• **YKS Puanı:** 480.000+ (en düşük devlet)
• **TYT:** En az 150+ doğru
• **AYT Fen:** En az 35+ doğru
• **Dil puanı:** Bazı üniversitelerde ek puan

**🏥 UZMANLIK ALANLARI VE MAAŞLARI:**

**💰 YÜKSEK MAAŞLI ALANLAR:**
• **Beyin Cerrahisi:** ₺40K-100K+
• **Kalp Cerrahisi:** ₺35K-80K
• **Plastik Cerrahi:** ₺30K-70K
• **Radyoloji:** ₺25K-60K
• **Anestezi:** ₺25K-55K

**🩺 ORTA MAAŞLI ALANLAR:**
• **Dahiliye:** ₺20K-40K
• **Pediatri:** ₺18K-35K
• **Kadın Doğum:** ₺20K-45K
• **Göz Hastalıkları:** ₺22K-50K

**👨‍⚕️ DİĞER ALANLAR:**
• **Aile Hekimliği:** ₺15K-25K (En kolay atanma)
• **Acil Tıp:** ₺18K-30K
• **Psikiyatri:** ₺17K-35K

**📚 EĞİTİM SÜRECİ:**
• **1-3. sınıf:** Temel bilimler (anatomi, fizyoloji)
• **4-6. sınıf:** Klinik dersler (hastane stajları)
• **İnternlik:** 1 yıl pratik deneyim
• **TUS:** Uzmanlık sınavı (%15 başarı oranı)

**✅ TIP İÇİN GEREKLİ ÖZELLİKLER:**
• Güçlü fen bilimleri (özellikle biyoloji, kimya)
• Yüksek stres toleransı
• Empati ve iletişim becerisi
• Uzun süreli eğitime sabır
• Sürekli öğrenme isteği

**⚠️ ZORLUKLAR:**
• Çok uzun eğitim süreci
• Yoğun müfredat ve ezberlemek
• Nöbet sistemi (düzensiz mesai)
• Yüksek sorumluluk ve stres
• TUS sınavının zorluğu

**🌍 ALTERNATİF SEÇENEKLER:**
• **Diş Hekimliği:** 5 yıl, daha az rekabet
• **Veteriner Hekim:** 5 yıl, hayvan sevgisi gerekli
• **Eczacılık:** 5 yıl, ilaç sektörü

Tıp alanında hangi uzmanlık dalları sizi daha çok ilgilendiriyor?`;
    }

    // 17. HUKUK FAKÜLTESİ
    if (lowerMessage.includes('hukuk') || lowerMessage.includes('avukat') || lowerMessage.includes('hukukçu')) {
      return `⚖️ **Hukuk Fakültesi - Adaletin Bekçileri:**

**📚 HUKUK EĞİTİMİ:**
• **4 yıl lisans** eğitimi
• **Staj:** 1 yıl avukatlık stajı
• **Avukatlık Sınavı:** Baro'ya kayıt için gerekli
• **Alternatif:** Hakim/Savcı için ayrı sınav

**⚖️ ÇALIŞMA ALANLARI:**

**💼 ÖZEL SEKTÖR:**
• **Şirket Hukuk Müşaviri:** ₺15K-40K
• **Bağımsız Avukat:** ₺8K-50K+ (müvekkil sayısına göre)
• **Hukuk Bürosu Ortağı:** ₺25K-100K+
• **Şirketlerde Legal:** ₺12K-30K

**🏛️ KAMU SEKTÖRÜ:**
• **Hakim:** ₺18K-35K + yan haklar
• **Savcı:** ₺18K-35K + yan haklar
• **Kaymakam/Vali:** İdari kariyer
• **Müfettiş:** Denetim alanları

**🏢 UZMANLIK ALANLARI:**
• **Ticaret Hukuku:** Şirket işlemleri, M&A
• **Ceza Hukuku:** Suç ve ceza davaları
• **Medeni Hukuk:** Aile, miras, kişilik hakları
• **İş Hukuku:** Çalışan hakları, işten çıkarma
• **Vergi Hukuku:** Mali müşavirlikle birlikte
• **Uluslararası Hukuk:** Global şirketler

**📊 BAŞARI FAKTÖRLERI:**
• **Güçlü Türkçe:** Yazma ve konuşma
• **Analitik düşünce:** Kanun maddelerini yorumlama
• **Araştırma becerisi:** İçtihat, doktrin tarama
• **İkna kabiliyeti:** Mahkemede savunma
• **Sabır:** Davalar uzun sürebilir

**💰 GELİR BEKLENTİLERİ:**
• **Yeni mezun:** ₺8K-15K (stajyer)
• **3-5 yıl deneyim:** ₺15K-25K
• **Deneyimli avukat:** ₺25K-50K
• **Tanınmış avukat:** ₺50K-200K+

**🎓 EN İYİ HUKUK FAKÜLTELERİ:**
• **İstanbul Üniversitesi:** En köklü, prestijli
• **Ankara Üniversitesi:** Kamu hukuku güçlü
• **Marmara Üniversitesi:** İyi mezun ağı
• **Galatasaray:** Fransızca eğitim
• **Boğaziçi:** Uluslararası perspektif

**⚠️ SEKTÖRÜN ZORLUKLARI:**
• Yoğun rekabet (çok sayıda mezun)
• İlk yıllarda düşük gelir
• Stresli davalar ve müvekkiller
• Sürekli kanun değişiklikleri takibi

**🚀 BAŞARILI OLMAK İÇİN:**
• Staj döneminde iyi mentör bulun
• Networking'e önem verin
• Uzmanlık alanı seçin
• Sürekli kendinizi güncelleyin
• İkinci dil öğrenin (özellikle İngilizce)

Hangi hukuk alanı daha çok ilginizi çekiyor?`;
    }

    // 18. İŞLETME VE EKONOMİ
    if (lowerMessage.includes('işletme') || lowerMessage.includes('yönetim') || 
        lowerMessage.includes('ekonomi') || lowerMessage.includes('iş dünyası')) {
      return `💼 **İşletme ve İş Dünyası - Geniş Kariyer İmkanları:**

**🏢 İŞLETME FAKÜLTESİ BÖLÜMLER:**

**📊 İŞLETME (En Popüler):**
• **Pazarlama:** Marka yönetimi, dijital pazarlama
• **Finans:** Yatırım, risk yönetimi, bankacılık
• **İnsan Kaynakları:** Personel, eğitim, performans
• **Operasyon:** Üretim, lojistik, kalite yönetimi
• **Girişimcilik:** Startup kurma, inovasyon

**💰 EKONOMİ:**
• Daha teorik ve analitik
• Ekonomi politikaları, makro/mikro analiz
• Bankacılık, kamu sektörü, akademi

**📈 ULUSLARARASI TİCARET:**
• İhracat-ithalat, gümrük işlemleri
• Global pazarlara açılım
• Dış ticaret şirketleri

**💵 ÇALIŞMA ALANLARI VE MAAŞLAR:**

**🏦 BANKACILIK:**
• **Giriş seviye:** ₺8K-12K
• **Şef/Müdür yardımcısı:** ₺15K-25K
• **Şube müdürü:** ₺25K-40K
• **Bölge müdürü:** ₺40K-80K

**📱 PAZARLAMA:**
• **Junior Marketer:** ₺7K-12K
• **Marketing Specialist:** ₺12K-20K
• **Brand Manager:** ₺20K-35K
• **Marketing Director:** ₺35K-60K

**👥 İNSAN KAYNAKLARI:**
• **HR Specialist:** ₺8K-15K
• **HR Business Partner:** ₺15K-25K
• **HR Director:** ₺25K-45K

**💼 YÖNETİM DANIŞMANLIĞI:**
• **Analyst:** ₺12K-20K
• **Consultant:** ₺20K-35K
• **Senior Consultant:** ₺35K-60K
• **Partner:** ₺60K-150K+

**🚀 GİRİŞİMCİLİK:**
• Kendi işinizi kurma
• Startup ekosistemi
• Risk sermayesi
• E-ticaret platformları

**📚 EĞİTİM İÇERİĞİ:**
• **Temel dersler:** Matematik, istatistik, ekonomi
• **Uzmanlık:** Pazarlama, finans, muhasebe
• **Beceriler:** Liderlik, proje yönetimi
• **Stajlar:** Şirketlerde deneyim

**✅ BAŞARILI OLMAK İÇİN GEREKLİLER:**
• İletişim becerileri güçlü
• Analitik düşünme
• Liderlik potansiyeli
• Takım çalışması
• Sürekli öğrenme isteği

**🎓 EN İYİ İŞLETME FAKÜLTELERİ:**
• **Boğaziçi:** En prestijli, uluslararası tanınırlık
• **Koç Üniversitesi:** Güçlü mezun ağı
• **Sabancı:** İnovatif yaklaşım
• **İÜ İktisat:** Köklü ve saygın
• **ODTÜ:** Analitik yaklaşım

**💡 BONUS İPUÇLARI:**
• İkinci dil çok önemli (İngilizce şart)
• Staj döneminde network kurun
• Sertifikalar edinin (Google Analytics, PMP vs.)
• Case study çalışmaları yapın

İş dünyasının hangi alanı daha çok ilginizi çekiyor?`;
    }

    // 19. EKONOMİK ŞEHİRLER
    if (lowerMessage.includes('ekonomik şehir') || lowerMessage.includes('ucuz şehir') || 
        lowerMessage.includes('hangi şehir') || lowerMessage.includes('öğrenci için şehir')) {
      return `🏙️ **Öğrenci için En Ekonomik Şehirler:**

**💰 EN UCUZ ŞEHİRLER:**
• **Kayseri:** Barınma ₺800-1500, yemek ₺1200-2000
• **Eskişehir:** Barınma ₺1000-1800, yemek ₺1500-2500
• **Konya:** Barınma ₺700-1300, yemek ₺1000-1800
• **Sivas:** Barınma ₺600-1200, yemek ₺1000-1600
• **Afyon:** Barınma ₺650-1100, yemek ₺900-1500

**🎯 ORTA SEVİYE (İyi Kalite/Fiyat):**
• **Trabzon:** Deniz kenarı, canlı şehir ₺1200-2200
• **Bursa:** İstanbul'a yakın ₺1300-2500
• **Denizli:** Güney Ege ₺1000-1800
• **Sakarya:** İstanbul'a 1 saat ₺1100-2000
• **Kocaeli:** Sanayi şehri, iş imkanı ₺1400-2600

**💸 PAHALIYA KAÇANLAR (Kaçının):**
• **İstanbul:** ₺2500-5000+ (çok pahalı)
• **Ankara:** ₺2000-3500
• **İzmir:** ₺1800-3200
• **Antalya:** ₺1600-3000

**🏠 MALİYET KARŞILAŞTIRMASI (Aylık):**
• **Yurt:** ₺500-2000
• **Ev paylaşımı:** ₺800-2500
• **Özel yurt:** ₺1200-3000
• **Yemek:** ₺1000-2500
• **Ulaşım:** ₺150-400

**💡 TAVSİYE:** Ekonomik şehirler tercih ederseniz 4 yılda ₺50.000-100.000 tasarruf edebilirsiniz!

Hangi bölgeyi düşünüyorsunuz?`;
    }

    // 20. ATAMA ORANI YÜKSEK BÖLÜMLER
    if (lowerMessage.includes('atama') || lowerMessage.includes('atanma') || 
        lowerMessage.includes('iş garantisi') || lowerMessage.includes('atama oranı')) {
      return `👨‍💼 **Atama Oranı En Yüksek Bölümler (2024):**

**🥇 %90+ ATAMA ORANI:**
• **Matematik Öğretmenliği:** %95+ (Çok aranıyor!)
• **Fen Bilgisi Öğretmenliği:** %92+
• **Fizik Öğretmenliği:** %90+
• **İngilizce Öğretmenliği:** %88+

**🏥 SAĞLIK ALANLARI (%85+):**
• **Hemşirelik:** %95+ (Avrupa'da da çalışabilir)
• **Ebe:** %90+
• **Fizyoterapist:** %85+
• **Diyetisyen:** %80+

**⚖️ KAMU GÖREVLİLİĞİ:**
• **Hukuk:** %70+ (KPSS ile)
• **İktisat:** %65+ (Maliye, hazine)
• **Kamu Yönetimi:** %75+
• **Maliye:** %70+

**🔧 TEKNİK ALANLAR:**
• **Elektrik Mühendisliği:** %80+ (Enerji sektörü)
• **İnşaat Mühendisliği:** %75+ (Devlet yatırımları)
• **Makine Mühendisliği:** %70+

**📊 EN DÜŞÜK ATAMA ORANLARI:**
• **Sınıf Öğretmenliği:** %15-20 (Çok doygun!)
• **Okul Öncesi:** %25-30
• **Türkçe Öğretmenliği:** %30-35
• **Tarih Öğretmenliği:** %20-25

**💡 ATAMA STRATEJİLERİ:**
• **Doğu illeri tercihi:** +%20-30 şans
• **Ek sertifikalar:** Bilgisayar, yabancı dil
• **Lisansüstü:** Ek puan kazandırır
• **Staj deneyimi:** Özel sektör backup

**⚠️ ÖNEMLİ:** Atama oranları yıllık değişebilir. İhtiyaç analizi yapıp ona göre tercih yapın!

Hangi alanda güvenceli iş arıyorsunuz?`;
    }

    // 21. YURTDIŞI İMKANI OLAN BÖLÜMLER
    if (lowerMessage.includes('yurtdışı') || lowerMessage.includes('yurt dışı') || 
        lowerMessage.includes('abroad') || lowerMessage.includes('avrupa') || lowerMessage.includes('america')) {
      return `🌍 **Yurtdışı İmkanı En Yüksek Bölümler:**

**💻 TEKNOLOJI (Çok Yüksek Talep):**
• **Yazılım/Bilgisayar Mühendisliği:** ABD, Kanada, Almanya
• **Veri Bilimi:** Dünyanın her yerinde aranıyor
• **Siber Güvenlik:** Özellikle AB ülkelerinde
• **Yapay Zeka/ML:** Silicon Valley, Londra

**🏥 SAĞLIK (Garantili Geçiş):**
• **Hemşirelik:** Almanya, İngiltere, Kanada (dil sertifikası ile)
• **Fizyoterapist:** AB ülkeleri, Avustralya
• **Diş Hekimi:** ABD, Kanada (denklik sınavı ile)
• **Tıp:** Her yerde (uzmanlık denkliği gerekli)

**🏗️ MÜHENDİSLİK:**
• **İnşaat Mühendisliği:** Körfez ülkeleri, Almanya
• **Elektrik Mühendisliği:** Almanya, Hollanda
• **Makine Mühendisliği:** Otomotiv sektörü (Almanya)
• **Petrol Mühendisliği:** Körfez, Norveç, Kanada

**🎓 AKADEMİK KARIYER:**
• **PhD + Araştırma:** ABD, İngiltere, Almanya
• **Mühendislik + MBA:** Global şirketler
• **Yabancı Dil Öğretmenliği:** AB programları

**📈 İŞ DÜNYASI:**
• **İşletme/MBA:** Multinational şirketler
• **Finans/Ekonomi:** Londra, New York, Singapur
• **Uluslararası İlişkiler:** BM, AB, büyükelçilikler

**🗺️ EN POPÜLER ÜLKELER:**
• **Almanya:** Mühendislik, sağlık (ücretsiz eğitim)
• **Kanada:** Teknoloji, sağlık (göçmen dostu)
• **Hollanda:** Mühendislik, işletme (İngilizce eğitim)
• **ABD:** Teknoloji, akademi (yüksek maaş)
• **İngiltere:** Finans, hukuk (kısa eğitim)

**🎯 HAZIRLIK STRATEJİSİ:**
• **İngilizce:** IELTS/TOEFL minimum 6.5-7.0
• **İkinci dil:** Almanca, Fransızca avantaj
• **Uluslararası sertifikalar:** Cisco, AWS, Google
• **Erasmus:** Üniversitede değişim programı
• **Staj:** Yurtdışı şirketlerde deneyim

**💰 MAAŞ BEKLENTİLERİ (Net):**
• **Yazılımcı (Almanya):** €45K-80K/yıl
• **Hemşire (İngiltere):** £25K-40K/yıl
• **Mühendis (Kanada):** CAD 60K-100K/yıl

Hangi ülke/sektör daha çok ilginizi çekiyor?`;
    }

    // 22. ÖZEL VS DEVLET ÜNİVERSİTE DETAYLI
    if (lowerMessage.includes('özel üniversite') || lowerMessage.includes('devlet üniversite') ||
        lowerMessage.includes('özel mi devlet mi')) {
      return `🎓 **Özel vs Devlet Üniversite - 2024 Gerçekleri:**

**🏛️ DEVLET ÜNİVERSİTESİ:**
✅ **Artıları:**
• **Maliyet:** Yılda sadece ₺1.000-2.000 harç
• **Prestij:** ODTÜ, Boğaziçi, İTÜ gibi dünya çapında tanınan
• **Araştırma:** Daha güçlü akademik alt yapı
• **Kampüs yaşamı:** Geniş sosyal aktiviteler
• **Mezun ağı:** Çok geniş ve güçlü network

❌ **Eksileri:**
• **Kalabalık:** 300+ kişilik sınıflar
• **Bireysel ilgi:** Hoca ile iletişim zor
• **Bürokrasi:** Yavaş işlemler
• **Eski alt yapı:** Bazı bölümlerde

**🏢 ÖZEL ÜNİVERSİTE:**
✅ **Artıları:**
• **Küçük sınıflar:** 15-30 kişi, bireysel takip
• **Modern donanım:** Son teknoloji lab/kütüphane
• **İngilizce eğitim:** Global fırsatlar
• **Sektör bağlantısı:** Kolay staj/iş bulma
• **Hızlı mezuniyet:** Optimize edilmiş müfredat

❌ **Eksileri:**
• **Yüksek maliyet:** ₺35K-200K/yıl
• **Prestij farkı:** İş piyasasında ayrım
• **Sınırlı araştırma:** Akademik kariyer için zayıf

**💰 4 YILLIK MALİYET KARŞILAŞTIRMASI:**

**Devlet Üniversitesi:**
• Harç: ₺8.000
• Yurt: ₺8.000
• Toplam: ~₺16.000

**Özel Üniversite (Burslu %50):**
• Harç: ₺200.000
• Yurt: ₺80.000
• Toplam: ~₺280.000

**Özel Üniversite (Burssuz):**
• Harç: ₺400.000
• Yurt: ₺80.000
• Toplam: ~₺480.000

**🎯 HANGİSİNİ SEÇMELİSİNİZ?**

**Devlet seçin eğer:**
• Bütçeniz kısıtlı
• Prestij önemli
• Araştırma/akademi hedefliyorsanız
• Geniş sosyal çevre istiyorsanız

**Özel seçin eğer:**
• %50+ burs alabiliyorsanız
• Bireysel ilgi istiyorsanız
• İş dünyasına hızla atılmak istiyorsanız
• İngilizce eğitim şart

**🏆 EN İYİ DEVLET ÜNİVERSİTELERİ:**
1. Boğaziçi, ODTÜ, İTÜ (Dünya sıralamasında)
2. Hacettepe, Ankara, Gazi (Prestijli)
3. Ege, Dokuz Eylül (Bölgesel lider)

**🏆 EN İYİ ÖZEL ÜNİVERSİTELER:**
1. Koç, Sabancı (Dünya standartında)
2. Bilkent, Özyeğin (Güçlü akademi)
3. İstanbul Bilgi, Kadir Has (Sosyal bilimler)

Bütçeniz ve hedefleriniz nedir?`;
    }
    const contextAwareDefaults = [
      `Bu konuda size daha detaylı yardım edebilmem için biraz daha bilgi verebilir misiniz? Örneğin hangi sınıfta okuyorsunuz veya en sevdiğiniz dersler neler?`,
      
      `İlginç bir soru! Size en uygun tavsiyeleri verebilmek için şu bilgileri paylaşabilir misiniz: Güçlü olduğunuz alanlar neler ve gelecekte kendinizi nasıl bir ortamda görüyorsunuz?`,
      
      `Tabii ki yardımcı olabilirim! Daha kişiselleştirilmiş öneriler yapabilmem için ilgi alanlarınız veya merak ettiğiniz bölümler hakkında biraz bilgi verebilir misiniz?`,
      
      `Bu sorunuza en doğru cevabı verebilmek için sizi biraz daha tanımak istiyorum. Akademik durumunuz nasıl ve hangi konular daha çok dikkatinizi çekiyor?`,
      
      `Size yardımcı olmak için buradayım! Daha detaylı bilgi verebilmek için hangi konularda rehberlik beklediğinizi söyleyebilir misiniz? Bölüm seçimi, üniversite karşılaştırması veya kariyer planlaması gibi...`
    ];
    
    return contextAwareDefaults[Math.floor(Math.random() * contextAwareDefaults.length)];
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);

    // Gerçekçi düşünme süresi
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        type: 'bot',
        text: generateBotResponse(currentInput),
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 2000 + Math.random() * 2000); // 2-4 saniye arası
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Daha iyi ve güncel hızlı cevaplar
  const quickReplies = [
    "Özel üniversite mi devlet mi?",
    "Hangi şehirler öğrenci için ekonomik?",
    "Hangi bölümlerin ataması yüksek?",
    "Hangi bölümlerin yurtdışı imkanı var?",
    "En garantili bölümler neler?"
  ];

  return (
    <div className="chat-widget">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="chat-window"
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="chat-header">
              <div className="header-info">
                <h4>🎓 BölümBul Asistanı</h4>
                <span className="online-status">● Çevrimiçi</span>
              </div>
              <button 
                className="chat-close"
                onClick={() => setIsOpen(false)}
              >
                ×
              </button>
            </div>

            <div className="chat-messages">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.type}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {message.type === 'bot' && (
                    <div className="bot-avatar">🤖</div>
                  )}
                  <div className="message-content">
                    <div className="message-text">
                      {message.text.split('\n').map((line, index) => (
                        <React.Fragment key={index}>
                          {line}
                          {index < message.text.split('\n').length - 1 && <br />}
                        </React.Fragment>
                      ))}
                    </div>
                    <div className="message-time">
                      {message.timestamp.toLocaleTimeString('tr-TR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  className="message bot typing"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="bot-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span className="typing-text">Düşünüyor...</span>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {messages.length === 1 && (
              <div className="quick-replies">
                <div className="quick-replies-header">
                  💡 Popüler sorular:
                </div>
                {quickReplies.map((reply, index) => (
                  <motion.button
                    key={index}
                    className="quick-reply"
                    onClick={() => {
                      setInput(reply);
                      setTimeout(sendMessage, 100);
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {reply}
                  </motion.button>
                ))}
              </div>
            )}

            <div className="chat-input">
              <div className="input-container">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Mesajınızı yazın..."
                  maxLength={500}
                  disabled={isTyping}
                />
                <button 
                  onClick={sendMessage} 
                  disabled={!input.trim() || isTyping}
                  className="send-button"
                >
                  {isTyping ? '⏳' : '📤'}
                </button>
              </div>
              <div className="input-info">
                {input.length}/500 karakter
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        className="chat-toggle"
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{ 
          boxShadow: isOpen 
            ? "0 0 0 0px rgba(99, 102, 241, 0.4)" 
            : "0 0 0 4px rgba(99, 102, 241, 0.4)"
        }}
        transition={{ 
          boxShadow: { duration: 2, repeat: Infinity, repeatType: "reverse" }
        }}
      >
        {isOpen ? '×' : '💬'}
      </motion.button>
    </div>
  );
};

export default ChatWidget;