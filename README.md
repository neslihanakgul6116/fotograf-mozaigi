# 🎨 Yüksek Netlikte Foto Mozaik Tablo Oluşturucu

Bu proje, hedef bir görseli (veya web kamerasından alınan canlı görüntüyü) küçük fotoğraflardan örerek yüksek netlikte bir mozaik tabloya dönüştüren **Python (OpenCV & NumPy)** ve **Flask** tabanlı bir web uygulamasıdır.

Proje, saf matris işlemleriyle renk uzayında en yakın komşuluk araması yapar ve **Alfa Harmanlama (Alpha Blending)** tekniği sayesinde mikro fotoğraflar net bir şekilde seçilirken ana görselin hatlarını da korur.

---

## 🌟 Öne Çıkan Özellikler

- **Yüksek Netlik (Alfa Harmanlama):** Ana resim ile oluşturulan mozaik tabanını harmanlayarak pürüzsüz hatlar elde eder.
- **Renk Algoritması Seçenekleri:** 
  - `CIELAB (L*a*b*)`: İnsan gözünün renk algısına en uygun doğal eşleşme.
  - `BGR / RGB`: Hızlı ve standart matris renk eşleşmesi.
- **Akıllı Renk Adaptasyonu (Color Tinting):** Mikro resimlerin renk tonlarını hedef bölgenin rengine hafifçe adapte eder.
- **Yan Yana Tekrar Engelleyici:** Komşu karelerde aynı mikro fotoğrafın üst üste ve yan yana dizilmesini engeller.
- **Çeşitli Parça Biçimleri:** Kare veya Daire parça maskeleme seçeneği.
- **Gelişmiş Web Arayüzü (Flask):**
  - **Canlı Before/After Slider:** Orijinal resim ile mozaik halini çizgiyle kıyaslama.
  - **Derin Zoom & Pan:** Fare tekerleğiyle yakınlaşma ve tutup sürükleme.
  - **İstatistik Paneli & Top 5 Analysis:** İşlem süresi, parça sayısı ve kütüphanede en çok kullanılan ilk 5 fotoğrafın analizi.
  - **Karanlık / Aydınlık Tema:** Tek tıkla tema değişimi.
  - **Canlı Kamera (Webcam) Modu:** Kamera görüntüsünü anlık mozaikleyerek yayınlama.
  - **HD İndirme ve Yazdırma:** Sonucu tek tıkla cihazınıza indirme veya PDF raporu oluşturma.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimleri Yükleyin
Projenin çalışması için gerekli kütüphaneleri terminalden yükleyin:
```bash
pip install flask opencv-python numpy


2. Klasör Yapısını Hazırlayın
Proje dizininizin şu şekilde olduğundan emin olun:

fotograf_mozaigi/
├── app.py
├── logo.png                   # Varsayılan test resmi
├── kaynak_resimler/           # Mikro (küçük) fotoğrafların konulacağı klasör
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── ...
├── static/                    # Çıktı görsellerinin kaydedildiği yer
└── templates/
    └── index.html             # Web arayüzü şablonu


3. Uygulamayı Başlatın
Terminalden ana dosyayı çalıştırın:
        python app.py

4. Tarayıcıda Açın
Tarayıcınızı açıp şu adrese gidin:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)





