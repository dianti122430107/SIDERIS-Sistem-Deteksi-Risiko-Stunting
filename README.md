# 🩺 SIDERIS

### Sistem Deteksi Dini Risiko Stunting pada Balita Menggunakan Random Forest

**SIDERIS** merupakan aplikasi desktop berbasis Python yang dikembangkan sebagai bagian dari tugas akhir untuk membantu proses deteksi dini risiko stunting pada balita menggunakan algoritma **Random Forest**.

---

## ✨ About SIDERIS

SIDERIS dirancang untuk membantu tenaga kesehatan dan kader dalam melakukan deteksi dini risiko stunting berdasarkan beberapa faktor yang berkaitan dengan kondisi balita.

Aplikasi mengintegrasikan proses **preprocessing data, perhitungan Z-score antropometri, dan klasifikasi Random Forest** dalam satu sistem.

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

**Programming Language**

* Python

**Machine Learning**

* Scikit-learn
* Random Forest
* Borderline-SMOTE

**Data Processing**

* Pandas
* NumPy

**Model Storage**

* Joblib / Pickle

**Database**

* MySQL

**Application**

* Python Desktop GUI

---

## 📸 Application Preview

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Input Data Balita

![Input Data](screenshots/input_data.png)

### Perhitungan Z-score

![Z-score](screenshots/zscore.png)

### Hasil Prediksi

![Prediction](screenshots/prediction.png)

---

## 📁 Project Structure

```text
SIDERIS/
├── aplikasi desktop/
├── assets/
├── data/
├── model_deployment
├── rfblsmote
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Installation

Clone repository:

```bash
git clone https://github.com/username/SIDERIS.git
cd SIDERIS
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
python app/gui.py
```

---

## 👩‍💻 Developer

**Dianti Alia Rahmah**

Institut Teknologi Sumatera (ITERA)

Program Studi Teknik Biomedis

> Developed as a final-year undergraduate thesis project.

---

## 📌 Disclaimer

This project was developed for academic and research purposes. The original research dataset is not included in this repository to protect respondent privacy.
