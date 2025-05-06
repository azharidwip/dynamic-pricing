#  Dynamic Pricing E-Commerce

Proyek ini menerapkan model **penetapan harga dinamis (dynamic pricing)** menggunakan *machine learning* berdasarkan data historis. Model diaplikasikan pada web menggunakan **Streamlit**. Model ini dapat memprediksi **harga yang optimal berdasarkan fitur produk**, yang dapat membantu pengambilan keputusan dalam strategi penetapan harga di bidang **e-commerce**.

---

##  Fitur Utama

-  Upload dan pratinjau data  
-  Prediksi harga optimal menggunakan model  
-  Visualisasi performa harga  
-  Antarmuka interaktif berbasis Streamlit  

---

##  Final Model Testing 

###  Deskripsi
Model **Dynamic Pricing** yang telah dilatih dan diuji menggunakan **Random Forest Regressor**.  
Tujuan dari pengujian ini adalah untuk mengukur seberapa baik model dapat menggeneralisasi terhadap data baru dan memberikan prediksi yang akurat.

###  Langkah-Langkah
1. Model terbaik diterapkan untuk memprediksi harga yang akan diuji  
2. Prediksi dibandingkan dengan nilai aktualnya  
3. Metrik evaluasi dihitung untuk menilai performa model  

---

##  Link Aplikasi Streamlit

Kunjungi aplikasi Dynamic Pricing:  
(https://dynamic-pricing-e-commerce.streamlit.app/)

---

##  Cara Menjalankan

### 1. Clone repository

git clone https://github.com/MuhamadFrhnn/dynamic-pricing
cd dynamic-pricing

### 2. Install dependencies

Copy
Edit
pip install -r requirements.txt

### 3. Jalankan aplikasi Streamlit

Copy
Edit
streamlit run app.py
