import os
import cv2
import time
import numpy as np
from collections import Counter
from flask import Flask, render_template, request, send_from_directory, Response

app = Flask(__name__)

# Global değişkenler
kutuphane_cache = {'renkler': None, 'resimler': None, 'boyut': None}

def mikro_kutuphane_yukle(klasor_yolu, blok_boyutu=(64, 64), renk_uzayi='LAB'):
    renkler = []
    resimler = []
    dosya_listesi = []
    if not os.path.exists(klasor_yolu):
        return np.array([]), [], []

    for dosya_adi in os.listdir(klasor_yolu):
        dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        if dosya_adi.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(dosya_yolu)
            if img is not None:
                img = cv2.resize(img, blok_boyutu)
                resimler.append(img)
                dosya_listesi.append(dosya_adi)
                
                if renk_uzayi == 'LAB':
                    lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                    renkler.append(lab_img.mean(axis=(0, 1)))
                else:
                    renkler.append(img.mean(axis=(0, 1)))
                
    return np.array(renkler), resimler, dosya_listesi

def generate_webcam_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        return
    
    blok_boyutu = 32 # Canlı akış performansı için hızlı blok boyutu
    kaynak_klasor = 'kaynak_resimler'
    kutuphane_renkleri, kutuphane_resimleri, _ = mikro_kutuphane_yukle(kaynak_klasor, (blok_boyutu, blok_boyutu), 'BGR')
    
    if len(kutuphane_resimleri) == 0:
        camera.release()
        return

    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Aynalama ve Boyutlandırma
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        yeni_h = (h // blok_boyutu) * blok_boyutu
        yeni_w = (w // blok_boyutu) * blok_boyutu
        frame = cv2.resize(frame, (yeni_w, yeni_h))
        
        mozaik_frame = np.zeros_like(frame)
        
        for y in range(0, yeni_h, blok_boyutu):
            for x in range(0, yeni_w, blok_boyutu):
                blok = frame[y:y+blok_boyutu, x:x+blok_boyutu]
                blok_ortalama = blok.mean(axis=(0, 1))
                mesafeler = np.linalg.norm(kutuphane_renkleri - blok_ortalama, axis=1)
                en_yakin_idx = np.argmin(mesafeler)
                mozaik_frame[y:y+blok_boyutu, x:x+blok_boyutu] = kutuphane_resimleri[en_yakin_idx]
                
        # Harmanlama
        sonuc_frame = cv2.addWeighted(frame, 0.40, mozaik_frame, 0.60, 0)
        
        ret, buffer = cv2.imencode('.jpg', sonuc_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    camera.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_webcam_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/', methods=['GET', 'POST'])
def index():
    mozaik_resim_adi = None
    hedef_resim_adi = None
    istatistikler = None
    top_5_resimler = []
    kaynak_galeri = []
    
    if os.path.exists('kaynak_resimler'):
        kaynak_galeri = [f for f in os.listdir('kaynak_resimler') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if request.method == 'POST':
        baslangic_zamani = time.time()
        hedef_yolu = None
        
        if 'hedef_resim' in request.files and request.files['hedef_resim'].filename != '':
            file = request.files['hedef_resim']
            hedef_yolu = os.path.join('static', 'hedef_gecici.jpg')
            file.save(hedef_yolu)
            hedef_resim_adi = 'hedef_gecici.jpg'
        elif os.path.exists('logo.png'):
            hedef_yolu = 'logo.png'
            hedef_img_temp = cv2.imread('logo.png')
            if hedef_img_temp is not None:
                cv2.imwrite(os.path.join('static', 'logo_temp.png'), hedef_img_temp)
                hedef_resim_adi = 'logo_temp.png'

        if hedef_yolu and os.path.exists(hedef_yolu):
            blok_boyutu = int(request.form.get('blok_boyutu', 64))
            harmanlama_orani = float(request.form.get('harmanlama_orani', 0.45))
            renk_uzayi = request.form.get('renk_uzayi', 'LAB')
            parca_sekli = request.form.get('parca_sekli', 'kare')
            renk_tonlama = 'renk_tonlama' in request.form
            izgara_ekle = 'izgara_ekle' in request.form
            
            kaynak_klasor = 'kaynak_resimler'
            kutuphane_renkleri, kutuphane_resimleri, dosya_listesi = mikro_kutuphane_yukle(
                kaynak_klasor, (blok_boyutu, blok_boyutu), renk_uzayi
            )
            toplam_kutuphane = len(kutuphane_resimleri)
            
            if toplam_kutuphane > 0:
                with open(hedef_yolu, "rb") as f:
                    bytes_data = bytearray(f.read())
                    np_array = np.asarray(bytes_data, dtype=np.uint8)
                    hedef_img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                    
                if hedef_img is not None:
                    h, w, _ = hedef_img.shape
                    satir_sayisi = h // blok_boyutu
                    sutun_sayisi = w // blok_boyutu
                    yeni_h = satir_sayisi * blok_boyutu
                    yeni_w = sutun_sayisi * blok_boyutu
                    hedef_img = cv2.resize(hedef_img, (yeni_w, yeni_h))
                    
                    cv2.imwrite(os.path.join('static', 'hedef_orijinal.jpg'), hedef_img)
                    hedef_resim_adi = 'hedef_orijinal.jpg'
                    
                    mozaik_tabani = np.zeros_like(hedef_img)
                    kullanilan_harita = np.full((satir_sayisi, sutun_sayisi), -1, dtype=int)
                    kullanim_sayaclari = []
                    
                    if renk_uzayi == 'LAB':
                        hedef_islem_img = cv2.cvtColor(hedef_img, cv2.COLOR_BGR2LAB)
                    else:
                        hedef_islem_img = hedef_img

                    daire_mask = np.zeros((blok_boyutu, blok_boyutu), dtype=np.uint8)
                    cv2.circle(daire_mask, (blok_boyutu // 2, blok_boyutu // 2), blok_boyutu // 2, 255, -1)

                    for r, y in enumerate(range(0, yeni_h, blok_boyutu)):
                        for c, x in enumerate(range(0, yeni_w, blok_boyutu)):
                            blok = hedef_islem_img[y:y+blok_boyutu, x:x+blok_boyutu]
                            blok_ortalama = blok.mean(axis=(0, 1))
                            
                            mesafeler = np.linalg.norm(kutuphane_renkleri - blok_ortalama, axis=1)
                            
                            sol_idx = kullanilan_harita[r, c-1] if c > 0 else -1
                            ust_idx = kullanilan_harita[r-1, c] if r > 0 else -1
                            sirali_idxler = np.argsort(mesafeler)
                            
                            en_yakin_idx = sirali_idxler[0]
                            if toplam_kutuphane > 2:
                                for idx in sirali_idxler:
                                    if idx != sol_idx and idx != ust_idx:
                                        en_yakin_idx = idx
                                        break
                                        
                            kullanilan_harita[r, c] = en_yakin_idx
                            kullanim_sayaclari.append(dosya_listesi[en_yakin_idx])
                            
                            secilen_parca = kutuphane_resimleri[en_yakin_idx].copy()
                            
                            if renk_tonlama:
                                hedef_bgr_blok = hedef_img[y:y+blok_boyutu, x:x+blok_boyutu]
                                hedef_renk = hedef_bgr_blok.mean(axis=(0, 1))
                                secilen_parca = cv2.addWeighted(secilen_parca, 0.75, np.full_like(secilen_parca, hedef_renk, dtype=np.uint8), 0.25, 0)

                            if parca_sekli == 'daire':
                                arkaplan = hedef_img[y:y+blok_boyutu, x:x+blok_boyutu]
                                secilen_parca = np.where(daire_mask[:, :, None] == 255, secilen_parca, arkaplan)

                            mozaik_tabani[y:y+blok_boyutu, x:x+blok_boyutu] = secilen_parca
                            
                            if izgara_ekle:
                                cv2.rectangle(mozaik_tabani, (x, y), (x + blok_boyutu, y + blok_boyutu), (50, 50, 50), 1)
                            
                    sonuc_mozaik = cv2.addWeighted(hedef_img, harmanlama_orani, mozaik_tabani, 1 - harmanlama_orani, 0)
                    
                    mozaik_resim_adi = 'cikis_mozaik.jpg'
                    cv2.imwrite(os.path.join('static', mozaik_resim_adi), sonuc_mozaik)
                    
                    gecen_sure = round(time.time() - baslangic_zamani, 3)
                    toplam_kare = satir_sayisi * sutun_sayisi
                    
                    sayac = Counter(kullanim_sayaclari)
                    top_5_resimler = sayac.most_common(5)
                    
                    istatistikler = {
                        'sure': gecen_sure,
                        'toplam_kare': toplam_kare,
                        'duzen': f"{sutun_sayisi} × {satir_sayisi}",
                        'kutuphane_sayisi': toplam_kutuphane,
                        'renk_uzayi': renk_uzayi,
                        'sekil': parca_sekli.capitalize()
                    }
                    
    return render_template(
        'index.html', 
        mozaik_resim=mozaik_resim_adi, 
        hedef_resim=hedef_resim_adi, 
        stats=istatistikler, 
        top_5=top_5_resimler,
        galeri=kaynak_galeri
    )

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)

@app.route('/kaynak_resimler/<filename>')
def kaynak_resim_getir(filename):
    return send_from_directory('kaynak_resimler', filename)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)