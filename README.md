# Air Quality Analysis

## Deskripsi

Project ini dibuat untuk menganalisis kualitas udara menggunakan Air Quality Dataset yang berisi data pengamatan kualitas udara per jam dari beberapa stasiun pemantauan di Beijing. Analisis berfokus pada konsentrasi PM2.5 berdasarkan stasiun pemantauan, periode waktu, musim, dan kondisi cuaca.

Project ini juga dilengkapi dengan dashboard interaktif menggunakan Streamlit untuk menampilkan hasil analisis agar lebih mudah dipahami.

## Pertanyaan Bisnis

1. Berapa rata-rata PM2.5 dan persentase hari yang melampaui ambang harian 75 µg/m³ pada tiap stasiun, dan stasiun mana yang harus diprioritaskan?
2. Bagaimana tren PM2.5 per periode 12 bulan (Mar-Feb) dan seberapa besar perbedaan musim dingin vs musim panas?
3. Seberapa kuat pengaruh kecepatan angin dan faktor cuaca lain terhadap PM2.5, dan pada kecepatan angin berapa risiko hari tercemar turun?

## Dataset

Dataset yang digunakan adalah Air Quality Dataset yang berisi data pengamatan kualitas udara per jam dari 12 stasiun pemantauan di Beijing, Tiongkok, selama Maret 2013 hingga Februari 2017.

File data yang digunakan dalam project ini:
- `main_data.csv`
- `hourly_profile.csv`

## Teknologi yang Digunakan

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit

## Ringkasan Temuan

- Rata-rata PM2.5 seluruh stasiun sebesar 79,9 µg/m³ atau 1,07 kali ambang harian. Sembilan stasiun perkotaan memiliki persentase hari yang melampaui ambang sekitar 41–43%, sedangkan Dingling, Huairou, dan Changping memiliki persentase lebih rendah, yaitu sekitar 32–36%.
- Konsentrasi PM2.5 pada musim dingin 48% lebih tinggi dibandingkan musim panas. Seluruh bulan Oktober–Maret memiliki rata-rata PM2.5 di atas ambang. Rata-rata per periode 12 bulan (Maret–Februari) turun dari 87,2 menjadi 72,9 µg/m³, kemudian naik kembali menjadi 78,1 µg/m³.
- Kecepatan angin memiliki hubungan negatif paling kuat dengan PM2.5 di antara faktor cuaca yang dianalisis, dengan korelasi Spearman sebesar -0,45. Pada kecepatan angin kurang dari 1 m/s, persentase hari yang melampaui ambang mencapai 65,6%, sedangkan pada kecepatan angin lebih dari 4 m/s turun menjadi 3,9%.

## Dashboard Streamlit

Project ini menyediakan dashboard interaktif yang dibuat menggunakan Streamlit untuk membantu pengguna melihat hasil analisis kualitas udara.

File utama aplikasi:
- `dashboard_streamlit.py`

File data yang digunakan:
- `main_data.csv`
- `hourly_profile.csv`

## Cara Menjalankan Aplikasi

1. Clone repository GitHub.
2. Masuk ke folder project.
3. Buat dan aktifkan virtual environment.
4. Install library yang dibutuhkan.
5. Jalankan aplikasi Streamlit.

Setelah aplikasi berjalan, buka alamat lokal yang ditampilkan di terminal untuk melihat dashboard melalui browser.

## Kesimpulan

Berdasarkan hasil analisis, konsentrasi PM2.5 berbeda antarstasiun dan musim. Konsentrasi PM2.5 cenderung lebih tinggi pada musim dingin dibandingkan musim panas. Kecepatan angin juga memiliki hubungan negatif dengan PM2.5, yaitu konsentrasi PM2.5 cenderung lebih tinggi ketika kecepatan angin rendah.

Hasil analisis ini dapat digunakan untuk memahami pola kualitas udara berdasarkan data yang tersedia, tetapi tidak secara langsung membuktikan hubungan sebab-akibat.

## Catatan

Project ini dibuat sebagai bagian dari tugas analisis data. Hasil analisis didasarkan pada dataset yang digunakan dan memiliki keterbatasan sesuai dengan cakupan data tersebut.