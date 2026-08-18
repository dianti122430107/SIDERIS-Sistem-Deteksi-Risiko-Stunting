import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score
import numpy as np
import joblib
import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

from imblearn.over_sampling import BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

vis_folder = "model_visualisasi"
if not os.path.exists(vis_folder):
    os.makedirs(vis_folder)

print("="*80)
print("RANDOM FOREST MODEL DENGAN BORDERLINE-SMOTE (5-FOLD CV + FULL TERMINAL LOG)")
print("="*80)

data = pd.read_csv("data/Data Stunting_RF.csv")
print("\nData berhasil dimuat!")
print(f"   Total data asli: {len(data)} baris")
print(f"   Total fitur     : {len(data.columns)-1} fitur\n")

# PENJELASAN FITUR
print("KETENTUAN FITUR DAN LABEL:")
print("-" * 80)
print("\nFitur Input:")
print("1. bbl (Berat Badan Lahir):")
print("   - 1 = Berat badan lahir > 2.5 kg (NORMAL)")
print("   - 0 = Berat badan lahir < 2.5 kg (RENDAH/BERAT)")

print("\n2. asupan_gizi (FFQ - Food Frequency Questionnaire):")
print("   - 2 = Asupan Gizi Baik")
print("   - 1 = Asupan Gizi Cukup")
print("   - 0 = Asupan Gizi Kurang")

print("\n3. imunisasi (Riwayat Imunisasi):")
print("   - 1 = Imunisasi Lengkap")
print("   - 0 = Imunisasi Tidak Lengkap")

print("\n4. asi_eksklusif (Air Susu Ibu Eksklusif):")
print("   - 1 = ASI Eksklusif (YA)")
print("   - 0 = Tidak ASI Eksklusif (TIDAK)")

print("\nLabel Target (Risiko Stunting):")
print("   - 0 = Risiko RENDAH")
print("   - 1 = Risiko SEDANG")
print("   - 2 = Risiko TINGGI")
print("\n" + "-" * 80)

rename_dict = {
    'BBL': 'bbl',
    'Asupan Gizi': 'asupan_gizi',
    'Imunisasi': 'imunisasi',
    'ASI': 'asi_eksklusif'
}
data = data.rename(columns=rename_dict)

X = data[['bbl', 'asupan_gizi', 'imunisasi', 'asi_eksklusif']]
y = data['Risiko']

print("\nData yang Digunakan:")
print(f"   Fitur yang digunakan: {list(X.columns)}")
print(f"   Total sampel: {len(X)} data")

# ANALISIS DISTRIBUSI ASLI
print(f"\n   Distribusi Risiko Stunting Asli (Sebelum Borderline-SMOTE):")
risk_counts = y.value_counts().sort_index()
for risk_level, count in risk_counts.items():
    risk_label = ["RENDAH", "SEDANG", "TINGGI"][risk_level]
    percentage = (count / len(y)) * 100
    print(f"   - Risiko {risk_label} ({risk_level}): {count} data ({percentage:.1f}%)")

# MODEL DEFINITION
rf_model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42)

# K-FOLD CROSS VALIDATION (5-FOLD) DENGAN BORDERLINE-SMOTE
print("\nMelakukan K-Fold Cross Validation (5-fold) dengan Borderline-SMOTE Pipeline...")
cv_scores = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
try:
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_pipeline = ImbPipeline([
        ('borderline_smote', BorderlineSMOTE(random_state=42, kind='borderline-1')),
        ('classifier', rf_model)
    ])
    
    cv_scores = cross_val_score(cv_pipeline, X, y, cv=kfold, scoring='accuracy')
    
    print("   Akurasi tiap fold:", ["{:.2f}%".format(score*100) for score in cv_scores])
    print("   Rata-rata akurasi CV (5-Fold):", "{:.2f}%".format(cv_scores.mean()*100))
    print("   Standar deviasi CV          :", "{:.4f}".format(cv_scores.std()))
    
    # AKURASI K-FOLD
    plt.figure(figsize=(8, 4.5))
    folds = [f"Fold {i+1}" for i in range(len(cv_scores))]
    plt.plot(folds, cv_scores * 100, marker='o', color='#1f77b4', linewidth=2, label='Akurasi Fold')
    plt.axhline(y=cv_scores.mean() * 100, color='r', linestyle='--', label=f'Rata-rata ({cv_scores.mean()*100:.2f}%)')
    plt.title('Tren Akurasi Per Putaran K-Fold Cross Validation', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Putaran Fold', fontsize=10)
    plt.ylabel('Akurasi (%)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.ylim(0, 105)
    for i, txt in enumerate(cv_scores):
        plt.annotate("{:.2f}%".format(txt*100), (folds[i], (cv_scores[i]*100)+2), ha='center', fontsize=9)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(vis_folder, 'akurasi_kfold.png'), dpi=300)
    plt.close()
except Exception as e:
    print(f"   ERROR pada K-Fold: {str(e)}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nData Split (80% Train, 20% Test):")
print(f"   Training data: {len(X_train)} baris")
print(f"   Testing data : {len(X_test)} baris")

# BORDERLINE-SMOTE PADA DATA TRAIN
print("\nMenerapkan Borderline-SMOTE pada data Training...")
bsmote = BorderlineSMOTE(random_state=42, kind='borderline-1')
X_train_resampled, y_train_resampled = bsmote.fit_resample(X_train, y_train)

print(f"   Distribusi Kelas Training SETELAH Borderline-SMOTE (Sintetis Perbatasan):")
resampled_counts = pd.Series(y_train_resampled).value_counts().sort_index()
for risk_level, count in resampled_counts.items():
    risk_label = ["RENDAH", "SEDANG", "TINGGI"][risk_level]
    print(f"   - Risiko {risk_label} ({risk_level}): {count} data")

# TRAINING MODEL FINAL
print(f"\nTraining Random Forest Model menggunakan data hasil Borderline-SMOTE...")
rf_model.fit(X_train_resampled, y_train_resampled)
print(f"   [OK] Model berhasil dilatih!")

# PREDIKSI
print(f"\nMembuat Prediksi pada Test Data...")
y_pred = rf_model.predict(X_test)
y_pred_proba = rf_model.predict_proba(X_test)

# HASIL PREDIKSI
print(f"\nHASIL PREDIKSI DETAIL:")
print("\n{:<4} {:<5} {:<15} {:<10} {:<15} {:<12} {:<35} {:<12} {:<8}".format(
    'No', 'bbl', 'asupan_gizi', 'imunisasi', 'asi_eksklusif', 'Prediksi', 'Probabilitas (R.Rendah|R.Sedang|R.Tinggi)', 'Aktual', 'Status'))
print("-" * 130)

def get_risk_label(value):
    risk_map = {0: "RENDAH", 1: "SEDANG", 2: "TINGGI"}
    return risk_map.get(value, "UNKNOWN")

for i in range(len(X_test)):
    test_data = X_test.iloc[i]
    pred = y_pred[i]
    prob = y_pred_proba[i]
    actual = y_test.iloc[i]
    is_correct = "OK" if pred == actual else "SALAH"
    prob_text = "{:.0%} | {:.0%} | {:.0%}".format(prob[0], prob[1], prob[2] if len(prob) > 2 else 0)
    
    print("{:<4} {:<5} {:<15} {:<10} {:<15} {:<12} {:<35} {:<12} {:<8}".format(
        i+1, int(test_data['bbl']), int(test_data['asupan_gizi']), int(test_data['imunisasi']), int(test_data['asi_eksklusif']),
        f"RISIKO {get_risk_label(int(pred))}({int(pred)})", prob_text, f"RISIKO {get_risk_label(int(actual))}({int(actual)})", is_correct))

# AKURASI & EVALUASI
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*130)
print("AKURASI MODEL (TEST DATA): {:.2f}%".format(accuracy*100))
print("="*130)

print("\nCLASSIFICATION REPORT (Evaluasi pada data asli di Terminal):")
target_names = ['RISIKO RENDAH (0)', 'RISIKO SEDANG (1)', 'RISIKO TINGGI (2)']
unique_labels = sorted(np.unique(np.concatenate([y_test, y_pred])))
target_names_filtered = [target_names[i] for i in unique_labels]
print(classification_report(y_test, y_pred, labels=unique_labels, target_names=target_names_filtered, zero_division=0))

print("\nCONFUSION MATRIX (Di Terminal):")
cm = confusion_matrix(y_test, y_pred)
print("   Rows = Aktual, Columns = Prediksi")
print("   [Rendah, Sedang, Tinggi]")
for i, row in enumerate(cm):
    risk_name = ["RENDAH", "SEDANG", "TINGGI"][i]
    print(f"   {risk_name}: {row}")

# FEATURE IMPORTANCE
print("\nFEATURE IMPORTANCE (Tingkat Kepentingan Fitur di Terminal):")
feature_importance = pd.DataFrame({
    'Fitur': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print("   {:<20}: {:>6.2f}%".format(row['Fitur'], row['Importance']*100))

print("RINGKASAN MODEL:")
print("="*80)
print(f"Algoritma         : Random Forest Classifier (50 trees)")
print(f"Total Training    : {len(X_train_resampled)} sampel (Pasca Borderline-SMOTE)")
print(f"Total Testing     : {len(X_test)} sampel")
print(f"Jumlah Fitur      : {X.shape[1]}")
print(f"Jumlah Kelas      : 3 (Risiko Rendah, Sedang, Tinggi)")
print(f"Akurasi Model     : {accuracy*100:.2f}%")
print("="*80 + "\n")


# CONFUSION MATRIX
plt.figure(figsize=(7, 5.5))
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', cbar=False,
            xticklabels=target_names_filtered, yticklabels=target_names_filtered,
            annot_kws={"size": 12, "weight": "bold"})
plt.title(f'Confusion Matrix Risiko Stunting\n(Akurasi Pengujian: {accuracy*100:.2f}%)', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Prediksi Model', fontsize=10, labelpad=10)
plt.ylabel('Aktual Sebenarnya', fontsize=10, labelpad=10)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(os.path.join(vis_folder, 'confusion_matrix.png'), dpi=300)
plt.close()

# CLASSIFICATION REPORT
report_dict = classification_report(y_test, y_pred, labels=unique_labels, target_names=target_names_filtered, output_dict=True, zero_division=0)
report_df = pd.DataFrame(report_dict).iloc[:-1, :-3].T
plt.figure(figsize=(7, 4))
sns.heatmap(report_df, annot=True, fmt='.2f', cmap='Blues', vmin=0.0, vmax=1.0, annot_kws={"size": 11, "weight": "bold"})
plt.title('Classification Report Per Tingkat Risiko', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(vis_folder, 'classification_report.png'), dpi=300)
plt.close()

# FEATURE IMPORTANCE
feature_importance_sorted = feature_importance.sort_values('Importance', ascending=True)
plt.figure(figsize=(8, 4.5))
colors = sns.color_palette('viridis', len(feature_importance_sorted))
bars = plt.barh(feature_importance_sorted['Fitur'], feature_importance_sorted['Importance'] * 100, color=colors, height=0.5)
plt.title('Tingkat Kepentingan Fitur (Feature Importance)', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Tingkat Kontribusi Pengaruh (%)', fontsize=10)
plt.ylabel('Nama Fitur Kontrol', fontsize=10)
plt.xlim(0, max(feature_importance_sorted['Importance'] * 100) + 10)
plt.grid(axis='x', linestyle=':', alpha=0.6)
for bar in bars:
    width = bar.get_width()
    plt.text(width + 1.5, bar.get_y() + bar.get_height()/2, '{:.2f}%'.format(width), va='center', ha='left', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(vis_folder, 'feature_importance.png'), dpi=300)
plt.close()


# SIMPAN MODEL UNTUK DEPLOYMENT
print("="*80)
print("MENYIMPAN MODEL UNTUK DEPLOYMENT APLIKASI DESKTOP")
print("="*80)

model_folder = "model_deployment"
if not os.path.exists(model_folder):
    os.makedirs(model_folder)

joblib.dump(rf_model, os.path.join(model_folder, "rf_stunting_model.pkl"))
print(f"   [OK] Model Random Forest + Borderline-SMOTE disimpan di: {model_folder}/rf_stunting_model.pkl")

with open(os.path.join(model_folder, "feature_names.txt"), 'w') as f:
    f.write(','.join(list(X.columns)))

label_mapping = {0: "RISIKO RENDAH", 1: "RISIKO SEDANG", 2: "RISIKO TINGGI"}
with open(os.path.join(model_folder, "label_mapping.json"), 'w') as f:
    json.dump(label_mapping, f)

model_info = {
    "nama_model": "Random Forest - Stunting Risk Prediction (Borderline-SMOTE Version)",
    "tanggal_dibuat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "algoritma": "Random Forest Classifier",
    "penanganan_imbalance": "Borderline-SMOTE (Kind: Borderline-1)",
    "cross_validation": "5-Fold Stratified dengan Borderline-SMOTE Pipeline",
    "akurasi_cv_mean": f"{cv_scores.mean()*100:.2f}%",
    "akurasi_test": f"{accuracy*100:.2f}%",
}
with open(os.path.join(model_folder, "model_info.json"), 'w') as f:
    json.dump(model_info, f, indent=2)

print("\n" + "="*80)
print("RINGKASAN FILE YANG BERHASIL DISIMPAN:")
print("="*80)
print(f"  📁 Folder Teks & Deployment ('{model_folder}/') : Model .pkl, Metadata .json, Fitur .txt")
print(f"  📁 Folder Gambar Visualisasi ('{vis_folder}/') :")
print(f"     - akurasi_kfold.png          (Tren grafik K-Fold)")
print(f"     - confusion_matrix.png       (Matriks performa prediksi)")
print(f"     - classification_report.png  (Heatmap nilai precision/recall)")
print(f"     - feature_importance.png     (Grafik batang kontribusi fitur)")
print("="*80 + "\n")