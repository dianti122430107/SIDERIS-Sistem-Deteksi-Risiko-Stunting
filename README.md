
# <img src="assets/logo_login.png" alt="Logo" width="250" style="vertical-align: middle;"/>

### Sistem Deteksi Risiko Stunting pada Balita Menggunakan Random Forest

**SIDERIS** merupakan aplikasi desktop berbasis Python yang dikembangkan sebagai bagian dari tugas akhir untuk membantu proses deteksi dini risiko stunting pada balita menggunakan algoritma **Random Forest**.

---

## ✨ About SIDERIS

SIDERIS dirancang untuk membantu tenaga kesehatan dan kader dalam melakukan deteksi dini risiko stunting berdasarkan beberapa faktor yang berkaitan dengan kondisi balita.

Aplikasi mengintegrasikan proses **perhitungan Z-score antropometri, dan klasifikasi Random Forest** dalam satu sistem.

---

## 🚀 Features

* 👶 Input dan pengelolaan data balita
* 📏 Perhitungan Z-score antropometri
* 🧠 Prediksi risiko menggunakan Random Forest
* 📊 Menampilkan hasil klasifikasi
* 💾 Penyimpanan data
* 🖥️ Antarmuka aplikasi desktop
* 🔐 Sistem login pengguna

---

## 🧠 Machine Learning

Model Random Forest menggunakan beberapa variabel sebagai input klasifikasi:

| Feature     | Keterangan                  |
| ----------- | --------------------------- |
| BBL         | Berat Badan Lahir           |
| ASI         | Status ASI Eksklusif        |
| Imunisasi   | Riwayat Imunisasi           |
| Asupan Gizi | Hasil penilaian asupan gizi |

Ketidakseimbangan kelas pada data training ditangani menggunakan **Borderline-SMOTE**.

### Model Performance

| Metric    | Result |
| --------- | -----: |
| Accuracy  |    95% |
| Precision |    96% |
| Recall    |    95% |
| F1-Score  |    95% |

---

## 🔄 System Workflow

```text
Data Balita
     ↓
Data Preprocessing
     ↓
Perhitungan Z-score
     ↓
Random Forest
     ↓
Prediksi Risiko
     ↓
Hasil Deteksi
```

---

## 🛠️ Tech Stack

| Kategori | Teknologi / Pustaka |
| :--- | :--- |
| **Programming Language** | Python |
| **Machine Learning** | Scikit-learn, Random Forest, Borderline-SMOTE |
| **Data Processing** | Pandas, NumPy |
| **Model Storage** | Joblib / Pickle |
| **Database** | MySQL |
| **Application** | Python Desktop GUI (CustomTkinter) |

---

## 📸 Application Preview

<table width="100%">
  <tr>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Login.png" alt="Login" width="100%"/>
      <sub><b>1. Login</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Registrasi.png" alt="Registrasi" width="100%"/>
      <sub><b>2. Registrasi</b></sub>
    </td>
  </tr>

  <tr>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Informasi SIDERIS.png" alt="Informasi SIDERIS" width="100%"/>
      <sub><b>3. Informasi SIDERIS</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Dashboard.png" alt="Dashboard" width="100%"/>
      <sub><b>4. Dashboard</b></sub>
    </td>
  </tr>

  <tr>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Input Data Balita.png" alt="Input Data Balita" width="100%"/>
      <sub><b>5. Input Data Balita</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Pemeriksaan.png" alt="Pemeriksaan" width="100%"/>
      <sub><b>6. Pemeriksaan</b></sub>
    </td>
  </tr>

  <tr>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Hasil Pemeriksaan.png" alt="Hasil Pemeriksaan" width="100%"/>
      <sub><b>7. Hasil Pemeriksaan</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Riwayat Pemeriksaan.png" alt="Riwayat Pemeriksaan" width="100%"/>
      <sub><b>8. Riwayat Pemeriksaan</b></sub>
    </td>
  </tr>

  <tr>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Riwayat Detail.png" alt="Riwayat Detail" width="100%"/>
      <sub><b>9. Riwayat Detail</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="GUI SIDERIS/Logout.png" alt="Logout" width="100%"/>
      <sub><b>10. Logout</b></sub>
    </td>
  </tr>
</table>

---

## 📁 Project Structure

```text
SIDERIS/
├── aplikasi desktop/
├── assets/
├── data/
├── model_deployment
├── rfblsmote
└── requirements.txt
```

---
## 📊 Parameter Deteksi & Penilaian

* **Data Antropometri:**
  * Berat Badan menurut Umur (BB/U)
  * Tinggi/Panjang Badan menurut Umur (TB/U)
  * Berat Badan menurut Tinggi Badan (BB/TB)
  * Lingkar Kepala menurut Umur (LK/U)
* **Kuesioner Frekuensi Makanan (FFQ):**
  * Frekuensi asupan karbohidrat, protein hewani/nabati, sayur, buah, dan makanan selingan.
* **Faktor Risiko Tambahan:**
  * Riwayat ASI eksklusif, kelengkapan imunisasi, dan berat lahir.

---

## 📌 Disclaimer

This project was developed for academic and research purposes. The original research dataset is not included in this repository to protect respondent privacy.

---

<div align="center">

### **Dianti Alia Rahmah**
*Program Studi Teknik Biomedis
Intitut Teknologi Sumatera*

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dianti122430107)
[![Status](https://img.shields.io/badge/Final%20Project%202026-teal?style=for-the-badge)](#)

<p align="center">
  > Developed as a final-year undergraduate thesis project.
</p>

</div>
