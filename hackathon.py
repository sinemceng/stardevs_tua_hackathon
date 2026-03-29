import tensorflow as tf
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os # Dizin işlemleri için ekledik

# 1. Modeli Yükle
model = tf.keras.models.load_model("lunar_model_v1.keras")

def kaya_tespit_et(resim_yolu):
    # 2. Resmi Oku ve Hazırla
    img = cv2.imread(resim_yolu)
    if img is None:
        print(f"Hata: {resim_yolu} bulunamadı!")
        return

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (256, 256))
    
    # 3. Normalizasyon
    input_data = img_resized / 255.0
    input_data = np.expand_dims(input_data, axis=0)
    
    # 4. Tahmin Yap
    prediction = model.predict(input_data)
    squeezed_prediction = np.squeeze(prediction)

    # 5. Görselleştir
    plt.subplot(1, 2, 1)
    plt.imshow(img_resized)
    plt.title("Orijinal Resim")
    
    plt.subplot(1, 2, 2)
    plt.imshow(squeezed_prediction, cmap='gray')
    plt.title("Modelin Tahmini")
    # plt.show() # İstersen açabilirsin

    # --- 🛡️ GÜVENLİ KAYDETME BLOĞU ---
    try:
        # Dosya adını tam yol (absolute path) olarak oluşturuyoruz
        # Bu, Windows'un 'Invalid Argument' hatasını aşmasını sağlar.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, "tahmin_sonucu.npy")
        
        # Diziyi kaydet
        np.save(save_path, squeezed_prediction)
        print(f"✅ Dizi başarıyla kaydedildi: {save_path}")
    except Exception as e:
        print(f"❌ Kaydetme hatası: {e}")
        # Eğer hala hata verirse alternatif isim deneyelim
        np.save("tahmin_v2.npy", squeezed_prediction)

# Test et 
# Windows'ta ters eğik çizgi sorununu önlemek için başına 'r' ekle
kaya_tespit_et(r"pcam/PCAM8.png")