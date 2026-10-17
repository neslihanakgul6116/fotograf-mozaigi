import os
import cv2
import numpy as np

def mikro_kutuphane_yukle(klasor_yolu, blok_boyutu=(8, 8)):
    """
    Kaynak klasördeki tüm küçük resimleri yükler, 
    belirlenen blok boyutuna küçültür ve ortalama renklerini hesaplar.
    """
    renkler = []
    resimler = []
    
    print("Mikro resimler yükleniyor ve renkleri hesaplanıyor...")
    if not os.path.exists(klasor_yolu):
        print("Hata: Kaynak klasör bulunamadı!")
        return np.array([]), []

    for dosya_adi in os.listdir(klasor_yolu):
        dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        if dosya_adi.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(dosya_yolu)
            if img is not None:
                img = cv2.resize(img, blok_boyutu)
                resimler.append(img)
                # Ortalama BGR rengini hesapla
                ortalama_renk = img.mean(axis=(0, 1)) 
                renkler.append(ortalama_renk)
                
    return np.array(renkler), resimler

def mozaik_olustur(hedef_resim_yolu, kaynak_klasor, blok_boyutu=8):
    print("Bulunduğum klasördeki dosyalar:", os.listdir('.'))
    
    # 1. Mikro kütüphaneyi hazırla
    kutuphane_renkleri, kutuphane_resimleri = mikro_kutuphane_yukle(kaynak_klasor, (blok_boyutu, blok_boyutu))
    
    if len(kutuphane_resimleri) == 0:
        print("Hata: Kaynak klasörde hiç resim bulunamadı veya klasör boş!")
        return

    # 2. Hedef resmi yükle (NumPy tabanlı güvenli bayt okuma)
    dosya_bulundu = False
    hedef_img = None
    
    denenecek_yollar = [hedef_resim_yolu, "hedef.jpg", "hedef.JPG", "hedef.jpeg", "hedef.JPEG", "hedef_resim.jpg"]
    for yol in denenecek_yollar:
        if os.path.exists(yol):
            try:
                with open(yol, "rb") as f:
                    bytes_data = bytearray(f.read())
                    np_array = np.asarray(bytes_data, dtype=np.uint8)
                    hedef_img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            except Exception:
                hedef_img = cv2.imread(yol)
                
            if hedef_img is not None:
                print(f"Hedef resim başarıyla yüklendi: {yol}")
                dosya_bulundu = True
                break

    if not dosya_bulundu or hedef_img is None:
        print("Hata: Hedef resim bulunamadı veya OpenCV tarafından okunamadı! Lütfen hedef resmin adını ve formatını kontrol edin.")
        return

    # Resmi blok boyutlarının tam katı olacak şekilde kırp/boyutlandır
    h, w, _ = hedef_img.shape
    yeni_h = (h // blok_boyutu) * blok_boyutu
    yeni_w = (w // blok_boyutu) * blok_boyutu
    hedef_img = cv2.resize(hedef_img, (yeni_w, yeni_h))

    mozaik_img = np.zeros_like(hedef_img)

    print("Mozaik örülüyor, lütfen bekleyin...")
    
    # 3. Her blok için en yakın rengi NumPy kullanarak hızlıca bulma
    for y in range(0, yeni_h, blok_boyutu):
        for x in range(0, yeni_w, blok_boyutu):
            blok = hedef_img[y:y+blok_boyutu, x:x+blok_boyutu]
            blok_ortalama = blok.mean(axis=(0, 1))
            
            # Matris tabanlı Öklid mesafesi hesabı
            mesafeler = np.linalg.norm(kutuphane_renkleri - blok_ortalama, axis=1)
            en_yakin_idx = np.argmin(mesafeler)
            
            # Bulunan mikro resmi yerine yerleştir
            mozaik_img[y:y+blok_boyutu, x:x+blok_boyutu] = kutuphane_resimleri[en_yakin_idx]

    cikis_dosyasi = "cikis_mozaik.jpg"
    cv2.imwrite(cikis_dosyasi, mozaik_img)
    print(f"İşlem tamamlandı! Mozaik '{cikis_dosyasi}' olarak kaydedildi.")

if __name__ == "__main__":
    KAYNAK_KLASOR = "kaynak_resimler"
    HEDEF_RESIM = "hedef.jpg"
    BLOK_BOYUTU = 6 # 16 yerine 8 yapılarak detay ve çözünürlük 2 katına çıkarıldı
    
    mozaik_olustur(HEDEF_RESIM, KAYNAK_KLASOR, BLOK_BOYUTU)