# 🌙 TUA Astro: Otonom Ay Aracı Navigasyon Sistemi

![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.10%2B-orange.svg)

Bu proje, Ay yüzeyindeki engelleri (kayaları) derin öğrenme ile tespit eden ve rover (ay aracı) için en güvenli, dinamik rotayı oluşturan uçtan uca bir navigasyon sistemidir. **Stardevs TUA Hackathon** kapsamında geliştirilmiştir.

##  Proje Özeti

Sistem, lunar yüzey görüntülerini analiz ederek otonom sürüş için gerekli olan engel tespitini yapar. Kullanıcı dostu bir arayüz üzerinden hedef belirleme ve bu hedefe giden en optimize yolun simülasyonunu gerçekleştirir.

### Temel Bileşenler:
1.  **Engel Tespiti (Yapay Zeka):** Görüntü segmentasyonu ile yüzeydeki tehlikeli kayaların tespiti.
2.  **Rota Planlama (Algoritma):** * **Ultimate A*:** Potansiyel alan (Potential Field) mantığıyla engellerin çevresinden "güvenli mesafe" bırakarak geçer.
    * **Hybrid A*:** Aracın fiziksel dönüş kabiliyetini (kinematik kısıtlar) hesaplayarak gerçekçi bir rota çizer.
3.  **Görev Kontrol (Arayüz):** Streamlit tabanlı interaktif harita paneli.
4.  **Simülasyon:** Pygame motoru ile rover'ın rota üzerindeki gerçek zamanlı hareketi.

##  Kurulum

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/sinemceng/stardevs_tua_hackathon.git](https://github.com/sinemceng/stardevs_tua_hackathon.git)
    cd stardevs_tua_hackathon
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    python hackathon.py
    streamlit run app2.py
    ```

##  Kullanım Klavuzu

1.  **Harita Seçimi:** Uygulama açıldığında model otomatik olarak lunar görüntüsünü analiz eder.
2.  **Başlangıç ve Hedef:** Harita üzerinde önce **Başlangıç (Mavi)**, sonra **Hedef (Sarı)** noktasına tıklayın.
3.  **Algoritma Seçimi:** Yan panelden (sidebar) istediğiniz navigasyon algoritmasını seçin.
4.  **Simülasyon:** Rota hesaplandığında simülasyon penceresi otomatik olarak açılacak ve rover göreve başlayacaktır.

##  Dosya Yapısı

* `app.py`: Ana Streamlit arayüzü ve algoritma mantığı.
* `simulation.py`: Pygame tabanlı görsel simülasyon motoru.
* `lunar_model_v1.keras`: Eğitilmiş derin öğrenme modeli.
* `requirements.txt`: Proje bağımlılıkları.
* `pcam/`: Lunar yüzey görüntüleri klasörü.

##  Kullanılan Teknolojiler

* **Deep Learning:** TensorFlow, Keras (U-Net mimarisi tabanlı segmentasyon)
* **Computer Vision:** OpenCV, Pillow
* **Web Framework:** Streamlit
* **Simulation & Graphics:** Pygame
* **Data Science:** NumPy, Pandas, Matplotlib

## Veri Seti
Kaggle üzerinden alınmıştır.

##### https://www.kaggle.com/code/basu369victor/transferlearning-and-unet-to-segment-rocks-on-moon
---
*Bu proje, otonom uzay araçları navigasyon sistemleri üzerine geliştirilmiş bir konsept çalışmasıdır.*
