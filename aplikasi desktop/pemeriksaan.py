import math
import os
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from database import (
    ambil_biodata_balita,
    ambil_daftar_nama_balita,
    ambil_data_sideris_by_nama,
    update_data_pemeriksaan,
)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from tkcalendar import Calendar, DateEntry

# Setup tema CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).resolve().parent
else:
    DATA_DIR = Path(__file__).resolve().parent


def load_who_standard(filename, x_col):
    try:
        path_file = DATA_DIR / filename
        print(f"Memuat basis data rujukan: {path_file}")

        df = pd.read_csv(path_file, dtype=str)
        df["jk"] = df["jk"].astype(str).str.strip()
        df[x_col] = pd.to_numeric(
            df[x_col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )
        for col in [
            "L",
            "M",
            "S",
            "SD3neg",
            "SD2neg",
            "SD1neg",
            "SD0",
            "SD1",
            "SD2",
            "SD3",
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ".", regex=False),
                    errors="coerce",
                )
        return df
    except Exception as e:
        print(f"🚨 GAGAL memuat file {filename}: {e}")
        return pd.DataFrame()


WHO_BBU = load_who_standard("standar_bbu.csv", "umur")
WHO_TBU = load_who_standard("standar_tbu.csv", "umur")
WHO_LKU = load_who_standard("standar_lku.csv", "umur")
WHO_BBTB = {
    "0_24": load_who_standard("standar_bbtb2th.csv", "tb"),
    "24_60": load_who_standard("standar_bbtb5th.csv", "tb"),
}


class PemeriksaanPage(ctk.CTkFrame):
    """Halaman untuk pemeriksaan balita (input data + FFQ + imunisasi)"""

    def __init__(self, parent, controller=None):
        super().__init__(parent)

        self.bg_grey = "#F8FAFC"
        self.text_dark = "#0F172A"
        self.sidebar_color = "#1E293B"
        self.primary_pink = "#E9708D"

        self.configure(fg_color="#F1F5F9")

        self.data_pemeriksaan_terakhir = None
        self.controller = controller

        self.all_data_dummy = []

        try:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        current_dir = os.path.dirname(os.path.abspath(__file__))
        sideris_frame_dir = os.path.dirname(current_dir)
        self.model_path = os.path.abspath(
            os.path.join(
                sideris_frame_dir, "model_deployment", "rf_stunting_model.pkl"
            )
        )

        try:
            self.model_rf = joblib.load(self.model_path)
            print("Model RF Borderline-SMOTE berhasil dimuat!")
        except Exception as e:
            print("Gagal memuat model ML, menggunakan fallback manual:", e)
            self.model_rf = None

        try:
            self.setup_main_content()
        except Exception as e:
            print("Error saat setup PemeriksaanPage:", e)

    def ambil_data_ffq(self):
        """Fungsi untuk mengambil daftar makanan dari database SIDERIS"""
        try:
            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            db_path = os.path.join(base_dir, "sideris_database.db")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT kategori, nama_makanan FROM tabel_ffq")
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError as e:
            print(f"Error Database: {e}")
            return [("Error", "Gagal memuat data dari basis data")]

    def setup_main_content(self):
        """Setup container utama dengan 3 kolom layout"""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(2, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def set_semua_imunisasi(self, status: bool):
        """Mengubah seluruh status checklist imunisasi sekaligus"""
        for var in self.imun_vars.values():
            var.set(status)

    def setup_ui(self):
        lbl_font = ("Arial", 13, "bold")

        # ==========================================
        # KOLOM 1: DATA DASAR
        # ==========================================
        col1 = ctk.CTkFrame(
            self.main_content, fg_color=self.bg_grey, corner_radius=15
        )
        col1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", ipadx=15)
        col1.grid_columnconfigure(0, weight=1)

        header_box1 = ctk.CTkFrame(col1, fg_color="transparent")
        header_box1.pack(fill="x", padx=10, pady=(5, 15))
        ctk.CTkLabel(
            header_box1,
            text="1",
            font=("Arial", 13, "bold"),
            fg_color="#E9708D",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box1,
            text="Input Data Dasar",
            font=("Helvetica", 16, "bold"),
            text_color="#0F172A",
        ).pack(side="left")

        # 1. NAMA BALITA
        ctk.CTkLabel(
            col1, text="Nama Balita", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)

        nama_box = ctk.CTkFrame(col1, fg_color="transparent")
        nama_box.pack(fill="x", padx=20, pady=(4, 12))

        ctk.CTkLabel(
            nama_box, text=" 👤 ", font=("Arial", 14), text_color="#94A3B8"
        ).pack(side="left", padx=(8, 2))

        user_id_aktif = getattr(self.controller, "current_user_id", None)
        init_names = (
            ambil_daftar_nama_balita(user_id_aktif) if user_id_aktif else []
        )

        self.ent_nama = ctk.CTkComboBox(
            nama_box,
            values=init_names,
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
            dropdown_fg_color="white",
            state="readonly",
            command=self.auto_fill_data_balita,
        )
        self.ent_nama.pack(fill="x", padx=(0, 10))
        self.ent_nama.set("--- Pilih Nama Balita ---")

        # 2. JENIS KELAMIN
        ctk.CTkLabel(
            col1, text="Jenis Kelamin", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)

        jk_frame = ctk.CTkFrame(col1, fg_color="transparent")
        jk_frame.pack(fill="x", padx=20, pady=(4, 12))
        jk_frame.grid_columnconfigure(0, weight=1)
        jk_frame.grid_columnconfigure(1, weight=1)

        self.selected_jk = ctk.StringVar(value="")

        def set_gender(gender):
            self.selected_jk.set(gender)
            if gender == "Laki-Laki":
                self.btn_male.configure(
                    fg_color="#EFF6FF", border_color="#3B82F6", text_color="#1D4ED8"
                )
                self.btn_female.configure(
                    fg_color="white", border_color="#E2E8F0", text_color="#64748B"
                )
            else:
                self.btn_male.configure(
                    fg_color="white", border_color="#E2E8F0", text_color="#64748B"
                )
                self.btn_female.configure(
                    fg_color="#FFF1F2", border_color="#E9708D", text_color="#9F1239"
                )

        self.btn_male = ctk.CTkButton(
            jk_frame,
            text="♂️    Laki-Laki",
            font=("Arial", 12, "bold"),
            fg_color="white",
            text_color="#64748B",
            border_color="#E2E8F0",
            border_width=1.5,
            height=35,
            corner_radius=8,
            command=lambda: set_gender("Laki-Laki"),
            hover=False,
        )
        self.btn_male.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_female = ctk.CTkButton(
            jk_frame,
            text="♀️    Perempuan",
            font=("Arial", 12, "bold"),
            fg_color="white",
            text_color="#64748B",
            border_color="#E2E8F0",
            border_width=1.5,
            height=35,
            corner_radius=8,
            command=lambda: set_gender("Perempuan"),
            hover=False,
        )
        self.btn_female.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # 3. TANGGAL LAHIR & USIA
        tgl_usia_frame = ctk.CTkFrame(col1, fg_color="transparent")
        tgl_usia_frame.pack(fill="x", padx=20, pady=(4, 12))
        tgl_usia_frame.grid_columnconfigure(0, weight=3)
        tgl_usia_frame.grid_columnconfigure(1, weight=2)

        sub_col_tgl = ctk.CTkFrame(tgl_usia_frame, fg_color="transparent")
        sub_col_tgl.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(
            sub_col_tgl, text="Tanggal Lahir", font=lbl_font, text_color="black"
        ).pack(anchor="w")

        cal_lahir_container = ctk.CTkFrame(sub_col_tgl, fg_color="transparent")
        cal_lahir_container.pack(fill="x", pady=(4, 0))

        self.cal_lahir = ctk.CTkEntry(
            cal_lahir_container,
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
            placeholder_text="dd/mm/yyyy",
        )
        self.cal_lahir.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.cal_lahir.insert(0, date.today().strftime("%d/%m/%Y"))

        btn_cal_lahir = ctk.CTkButton(
            cal_lahir_container,
            text="📅",
            width=35,
            height=35,
            fg_color="#F1F5F9",
            text_color="black",
            hover_color="#E2E8F0",
            corner_radius=6,
            command=lambda: self.buka_popup_kalender(self.cal_lahir),
        )
        btn_cal_lahir.pack(side="right")
        self.cal_lahir.bind("<Return>", lambda e: self.update_umur())

        sub_col_usia = ctk.CTkFrame(tgl_usia_frame, fg_color="transparent")
        sub_col_usia.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(
            sub_col_usia, text="Usia", font=lbl_font, text_color="black"
        ).pack(anchor="w")

        self.lbl_usia_auto = ctk.CTkLabel(
            sub_col_usia,
            text="0 Bulan",
            font=("Arial", 13, "bold"),
            text_color="#E9708D",
            fg_color="white",
            corner_radius=8,
            height=34,
        )
        self.lbl_usia_auto.pack(fill="x", pady=(4, 0))

        # TANGGAL PERIKSA
        ctk.CTkLabel(
            col1, text="Tanggal Periksa", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)

        cal_periksa_container = ctk.CTkFrame(col1, fg_color="transparent")
        cal_periksa_container.pack(fill="x", padx=20, pady=(4, 12))

        self.cal_periksa = ctk.CTkEntry(
            cal_periksa_container,
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
            placeholder_text="dd/mm/yyyy",
        )
        self.cal_periksa.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.cal_periksa.insert(0, date.today().strftime("%d/%m/%Y"))

        btn_cal_periksa = ctk.CTkButton(
            cal_periksa_container,
            text="📅",
            width=35,
            height=35,
            fg_color="#F1F5F9",
            text_color="black",
            hover_color="#E2E8F0",
            corner_radius=6,
            command=lambda: self.buka_popup_kalender(self.cal_periksa),
        )
        btn_cal_periksa.pack(side="right")
        self.cal_periksa.bind("<Return>", lambda e: self.update_umur())

        # Berat Badan Lahir
        ctk.CTkLabel(
            col1, text="Berat Badan Lahir (kg)", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)

        bb_lahir_box = ctk.CTkFrame(col1, fg_color="transparent")
        bb_lahir_box.pack(fill="x", padx=20, pady=(4, 12))

        self.selected_bbl = ctk.StringVar(value="")

        self.btn_bbl_under = ctk.CTkButton(
            bb_lahir_box,
            text="< 2,5 kg",
            font=("Inter", 11, "bold"),
            height=35,
            border_width=1,
            fg_color="white",
            border_color="#E2E8F0",
            text_color="#64748B",
            hover_color="#F8FAFC",
            command=lambda: self.set_bbl_selection("< 2,5 kg"),
        )
        self.btn_bbl_under.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_bbl_over = ctk.CTkButton(
            bb_lahir_box,
            text="> 2,5 kg",
            font=("Inter", 11, "bold"),
            height=35,
            border_width=1,
            fg_color="white",
            border_color="#E2E8F0",
            text_color="#64748B",
            hover_color="#F8FAFC",
            command=lambda: self.set_bbl_selection("> 2,5 kg"),
        )
        self.btn_bbl_over.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Berat Badan Sekarang
        ctk.CTkLabel(
            col1, text="Berat Badan Sekarang (kg)", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)
        bb_sekarang_box = ctk.CTkFrame(col1, fg_color="transparent")
        bb_sekarang_box.pack(fill="x", padx=20, pady=(4, 12))
        ctk.CTkLabel(
            bb_sekarang_box, text=" ⚖️ ", font=("Arial", 14), text_color="#94A3B8"
        ).pack(side="left", padx=(8, 2))
        self.ent_bb_sekarang = ctk.CTkEntry(
            bb_sekarang_box,
            placeholder_text="Masukkan berat sekarang (kg)",
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
        )
        self.ent_bb_sekarang.pack(fill="x", padx=(0, 10))

        # Tinggi Badan Sekarang
        ctk.CTkLabel(
            col1,
            text="Tinggi / Panjang Badan (cm)",
            font=lbl_font,
            text_color="black",
        ).pack(anchor="w", padx=20)
        tb_box = ctk.CTkFrame(col1, fg_color="transparent")
        tb_box.pack(fill="x", padx=20, pady=(4, 12))
        ctk.CTkLabel(
            tb_box, text=" 📏 ", font=("Arial", 14), text_color="#94A3B8"
        ).pack(side="left", padx=(8, 2))
        self.ent_tb = ctk.CTkEntry(
            tb_box,
            placeholder_text="Masukkan tinggi badan (cm)",
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
        )
        self.ent_tb.pack(fill="x", padx=(0, 10))

        # Lingkar Kepala
        ctk.CTkLabel(
            col1, text="Lingkar Kepala (cm)", font=lbl_font, text_color="black"
        ).pack(anchor="w", padx=20)
        lk_box = ctk.CTkFrame(col1, fg_color="transparent")
        lk_box.pack(fill="x", padx=20, pady=(4, 12))
        ctk.CTkLabel(
            lk_box, text=" 🧠 ", font=("Arial", 14), text_color="#94A3B8"
        ).pack(side="left", padx=(8, 2))
        self.ent_lk = ctk.CTkEntry(
            lk_box,
            placeholder_text="Masukkan lingkar kepala (cm)",
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CBD5E1",
            height=35,
        )
        self.ent_lk.pack(fill="x", padx=(0, 10))

        # ASI Eksklusif 6 Bulan
        ctk.CTkLabel(
            col1,
            text="ASI Eksklusif 6 Bulan",
            font=lbl_font,
            text_color="black",
        ).pack(anchor="w", padx=20, pady=(4, 0))

        asi_box = ctk.CTkFrame(col1, fg_color="transparent")
        asi_box.pack(fill="x", padx=20, pady=(4, 12))

        self.selected_asi = ctk.StringVar(value="")

        self.btn_asi_yes = ctk.CTkButton(
            asi_box,
            text="Ya",
            font=("Inter", 11, "bold"),
            height=35,
            border_width=1,
            fg_color="white",
            border_color="#E2E8F0",
            text_color="#64748B",
            hover_color="#F8FAFC",
            command=lambda: self.set_asi_selection("Ya"),
        )
        self.btn_asi_yes.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_asi_no = ctk.CTkButton(
            asi_box,
            text="Tidak",
            font=("Inter", 11, "bold"),
            height=35,
            border_width=1,
            fg_color="white",
            border_color="#E2E8F0",
            text_color="#64748B",
            hover_color="#F8FAFC",
            command=lambda: self.set_asi_selection("Tidak"),
        )
        self.btn_asi_no.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # ==========================================
        # KOLOM 2: ASUPAN GIZI & IMUNISASI
        # ==========================================
        col2 = ctk.CTkFrame(self.main_content, fg_color="transparent")
        col2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        col2.grid_columnconfigure(0, weight=1)
        col2.grid_rowconfigure(1, weight=1)
        col2.grid_rowconfigure(3, weight=1)

        card_gizi_putih = ctk.CTkFrame(
            col2, fg_color="white", corner_radius=16, border_width=0
        )
        card_gizi_putih.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=5)
        card_gizi_putih.grid_columnconfigure(0, weight=1)
        card_gizi_putih.grid_rowconfigure(1, weight=1)

        header_box2 = ctk.CTkFrame(card_gizi_putih, fg_color="transparent")
        header_box2.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header_box2,
            text="2",
            font=("Arial", 13, "bold"),
            fg_color="#2563EB",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box2,
            text="Asupan Gizi",
            font=("Helvetica", 16, "bold"),
            text_color=self.text_dark,
        ).pack(side="left")

        ffq_scroll = ctk.CTkScrollableFrame(
            card_gizi_putih, fg_color="transparent", corner_radius=0
        )
        ffq_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))
        ffq_scroll.grid_columnconfigure(0, weight=1)

        self.ffq_vars = {}
        kategori_gizi = {
            "🍚 Karbohidrat": [
                "Nasi",
                "Bubur",
                "Mie/Bihun",
                "Roti",
                "Kentang/Ubi/Singkong",
            ],
            "🍗 Protein Hewani": [
                "Telur",
                "Ayam",
                "Ikan",
                "Daging Sapi/Kambing",
                "Hati Ayam/Sapi",
                "Susu/Susu Formula",
            ],
            "🫘 Protein Nabati": ["Tempe", "Tahu", "Kacang-Kacangan"],
            "🥦 Sayur-Sayuran": ["Sayur Hijau", "Sayur Orange", "Sayur Sup/Bening"],
            "🍊 Buah-Buahan": ["Pisang", "Pepaya/Mangga", "Jeruk", "Buah Lainnya"],
            "🍪 Makanan Selingan": [
                "Biskuit/Biskuit Balita",
                "Snack Kemasan",
                "Permen/Coklat",
                "Minuman Manis",
            ],
        }

        for kat, items in kategori_gizi.items():
            ctk.CTkLabel(
                ffq_scroll,
                text=kat,
                font=("Arial", 13, "bold"),
                text_color="#E9708D",
            ).pack(anchor="w", padx=10, pady=(10, 5))
            for item in items:
                row = ctk.CTkFrame(ffq_scroll, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(
                    row, text=item, font=("Arial", 13), text_color="#334155"
                ).pack(side="left", anchor="w")

                var = ctk.StringVar(value="Tidak Pernah")
                self.ffq_vars[item] = var
                ctk.CTkOptionMenu(
                    row,
                    values=[
                        "Sangat Sering",
                        "Sering",
                        "Biasa",
                        "Kadang-Kadang",
                        "Kurang",
                        "Tidak Pernah",
                    ],
                    variable=var,
                    width=110,
                    height=25,
                ).pack(side="right")

        # KARTU RIWAYAT IMUNISASI
        card_imun_putih = ctk.CTkFrame(
            col2, fg_color="white", corner_radius=16, border_width=0
        )
        card_imun_putih.grid(
            row=3, column=0, sticky="nsew", padx=(0, 5), pady=(15, 5)
        )
        card_imun_putih.grid_columnconfigure(0, weight=1)
        card_imun_putih.grid_rowconfigure(2, weight=1)

        header_box3 = ctk.CTkFrame(card_imun_putih, fg_color="transparent")
        header_box3.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 6))

        ctk.CTkLabel(
            header_box3,
            text="3",
            font=("Arial", 13, "bold"),
            fg_color="#0D9488",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box3,
            text="Riwayat Imunisasi",
            font=("Helvetica", 16, "bold"),
            text_color=self.text_dark,
        ).pack(side="left")

        # Container Tombol Aksi Imunisasi (Lengkap & Reset)
        btn_action_imun = ctk.CTkFrame(card_imun_putih, fg_color="transparent")
        btn_action_imun.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 6))
        btn_action_imun.grid_columnconfigure(0, weight=1)
        btn_action_imun.grid_columnconfigure(1, weight=1)

        btn_lengkap = ctk.CTkButton(
            btn_action_imun,
            text="✅ Lengkap (Centang Semua)",
            font=("Arial", 11, "bold"),
            fg_color="#0D9488",
            hover_color="#0F766E",
            text_color="white",
            height=28,
            corner_radius=6,
            command=lambda: self.set_semua_imunisasi(True),
        )
        btn_lengkap.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        btn_reset_imun = ctk.CTkButton(
            btn_action_imun,
            text="🔄 Reset",
            font=("Arial", 11, "bold"),
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color="#475569",
            height=28,
            corner_radius=6,
            command=lambda: self.set_semua_imunisasi(False),
        )
        btn_reset_imun.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        imun_scroll = ctk.CTkScrollableFrame(
            card_imun_putih, fg_color="transparent", corner_radius=0
        )
        imun_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 15))
        imun_scroll.grid_columnconfigure(0, weight=1)

        self.imun_vars = {}
        vaksins = [
            "Hepatitis B (<24 Jam)",
            "BCG",
            "Polio Tetes 1",
            "DPT-HB-Hib 1",
            "Polio Tetes 2",
            "Rotavirus (RV) 1",
            "PCV 1",
            "DPT-HB-Hib 2",
            "Polio Tetes 3",
            "Rotavirus (RV) 2",
            "PCV 2",
            "DPT-HB-Hib 3",
            "Polio Tetes 4",
            "Polio Suntik (IPV) 1",
            "Rotavirus (RV) 3",
            "Campak-Rubella (MR)",
            "Polio Suntik (IPV) 2",
            "Japanese Encephalitis (JE)",
            "PCV 3",
            "DPT-HB-Hib Lanjutan",
            "Campak Rubella (MR) Lanjutan",
        ]

        for idx, vks in enumerate(vaksins):
            v = ctk.BooleanVar(value=False)
            self.imun_vars[vks] = v
            ctk.CTkCheckBox(
                imun_scroll,
                text=vks,
                variable=v,
                font=("Arial", 11),
                text_color="black",
            ).grid(row=idx, column=0, sticky="w", padx=10, pady=5)

        # ==========================================
        # KOLOM 3: HASIL PEMERIKSAAN & Z-SCORE
        # ==========================================
        col3_master = ctk.CTkFrame(self.main_content, fg_color="transparent")
        col3_master.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        col3_master.grid_columnconfigure(0, weight=1)
        col3_master.grid_rowconfigure(0, weight=3)
        col3_master.grid_rowconfigure(1, weight=3)
        col3_master.grid_rowconfigure(2, weight=4)

        # HASIL PEMERIKSAAN
        card_hasil = ctk.CTkFrame(
            col3_master, fg_color="white", corner_radius=16, border_width=0
        )
        card_hasil.grid(row=0, column=0, padx=5, pady=(5, 10), sticky="nsew")
        card_hasil.grid_columnconfigure(0, weight=1)

        header_box4 = ctk.CTkFrame(card_hasil, fg_color="transparent")
        header_box4.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        ctk.CTkLabel(
            header_box4,
            text="4",
            font=("Arial", 13, "bold"),
            fg_color="#F59E0B",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box4,
            text="Hasil Pemeriksaan",
            font=("Helvetica", 16, "bold"),
            text_color="#0F172A",
        ).pack(side="left")

        card_hasil._next_row = 1

        def buat_sub_card_hasil(parent, title, icon):
            f = ctk.CTkFrame(
                parent,
                fg_color="#F8FAFC",
                corner_radius=12,
                border_width=1,
                border_color="#E2E8F0",
                height=65,
            )
            row_idx = parent._next_row
            f.grid(row=row_idx, column=0, sticky="ew", padx=20, pady=5)
            parent._next_row = row_idx + 1
            f.pack_propagate(False)

            bg_circle = "#FEF3C7" if icon == "🍴" else "#E0F2FE"
            lbl_lingkaran = ctk.CTkLabel(
                f,
                text=icon,
                font=("Arial", 14),
                fg_color=bg_circle,
                text_color="black",
                width=25,
                height=30,
                corner_radius=15,
            )
            lbl_lingkaran.place(x=12, y=13)

            text_container = ctk.CTkFrame(f, fg_color="transparent")
            text_container.pack(
                side="left", fill="both", expand=True, padx=(62, 10), pady=8
            )

            ctk.CTkLabel(
                text_container,
                text=title,
                font=("Helvetica", 11, "bold"),
                text_color="#64748B",
            ).pack(anchor="w", pady=(2, 0))
            lbl_value = ctk.CTkLabel(
                text_container,
                text="-",
                font=("Arial", 14, "bold"),
                text_color="#1E293B",
            )
            lbl_value.pack(anchor="w", pady=(1, 0))
            return lbl_value

        self.res_gizi = buat_sub_card_hasil(card_hasil, "Asupan Gizi (FFQ)", "🍴")
        self.res_imun = buat_sub_card_hasil(card_hasil, "Status Imunisasi", "🛡️")

        self.label_status_imun = ctk.CTkLabel(
            card_hasil,
            text="Status Imunisasi: Belum Dicek",
            font=("Arial", 11, "bold"),
            text_color="#94A3B8",
        )
        self.label_status_imun.grid(
            row=card_hasil._next_row, column=0, pady=(4, 10)
        )

        # NILAI Z-SCORE
        card_zscore = ctk.CTkFrame(
            col3_master, fg_color="white", corner_radius=16, border_width=0
        )
        card_zscore.grid(row=1, column=0, padx=5, pady=(10, 5), sticky="nsew")
        card_zscore.grid_columnconfigure(0, weight=1)
        card_zscore.grid_rowconfigure(1, weight=1)

        header_box5 = ctk.CTkFrame(card_zscore, fg_color="transparent")
        header_box5.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))
        ctk.CTkLabel(
            header_box5,
            text="5",
            font=("Arial", 13, "bold"),
            fg_color="#6366F1",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box5,
            text="Nilai Z-Score",
            font=("Helvetica", 16, "bold"),
            text_color="#0F172A",
        ).pack(side="left")

        z_rows_container = ctk.CTkFrame(card_zscore, fg_color="transparent")
        z_rows_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=2)

        def buat_baris_zscore_modern(parent, nama_indeks, baris_idx):
            f_row = ctk.CTkFrame(
                parent,
                fg_color="#F8FAFC",
                corner_radius=10,
                border_width=1,
                border_color="#E2E8F0",
                height=38,
            )
            f_row.pack(fill="x", pady=4)
            f_row.pack_propagate(False)

            ctk.CTkLabel(
                f_row,
                text=nama_indeks,
                font=("Helvetica", 12, "bold"),
                text_color="#334155",
            ).pack(side="left", padx=15)
            ctk.CTkLabel(
                f_row, text=":", font=("Arial", 12, "bold"), text_color="#475569"
            ).pack(side="left", padx=5)
            lbl_val = ctk.CTkLabel(
                f_row, text="-", font=("Arial", 13, "bold"), text_color="#475569"
            )
            lbl_val.pack(side="left", padx=5)
            return lbl_val

        self.lbl_list_bbtb = buat_baris_zscore_modern(z_rows_container, "BB/TB", 0)
        self.lbl_list_bbu = buat_baris_zscore_modern(z_rows_container, "BB/U", 1)
        self.lbl_list_tbu = buat_baris_zscore_modern(z_rows_container, "TB/U", 2)
        self.lbl_list_lku = buat_baris_zscore_modern(z_rows_container, "LK/U", 3)

        # HASIL PREDIKSI RISIKO
        card_prediksi = ctk.CTkFrame(
            col3_master, fg_color="white", corner_radius=16, border_width=0
        )
        card_prediksi.grid(row=2, column=0, padx=5, pady=(5, 10), sticky="nsew")
        card_prediksi.grid_columnconfigure(0, weight=1)

        header_box6 = ctk.CTkFrame(card_prediksi, fg_color="transparent")
        header_box6.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 6))

        ctk.CTkLabel(
            header_box6,
            text="6",
            font=("Arial", 13, "bold"),
            fg_color="#F43F5E",
            text_color="white",
            width=26,
            height=26,
            corner_radius=13,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            header_box6,
            text="Hasil Prediksi Risiko",
            font=("Helvetica", 16, "bold"),
            text_color="#0F172A",
        ).pack(side="left")

        prediksi_rows_container = ctk.CTkFrame(
            card_prediksi, fg_color="transparent"
        )
        prediksi_rows_container.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=2
        )

        def buat_baris_prediksi_modern(parent, nama_parameter):
            f_row = ctk.CTkFrame(
                parent,
                fg_color="#F8FAFC",
                corner_radius=10,
                border_width=1,
                border_color="#E2E8F0",
                height=38,
            )
            f_row.pack(fill="x", pady=3)
            f_row.pack_propagate(False)

            ctk.CTkLabel(
                f_row,
                text=nama_parameter,
                font=("Helvetica", 12, "bold"),
                text_color="#334155",
            ).pack(side="left", padx=15)
            ctk.CTkLabel(
                f_row, text=":", font=("Arial", 12, "bold"), text_color="#475569"
            ).pack(side="left", padx=5)
            lbl_val = ctk.CTkLabel(
                f_row, text="-", font=("Arial", 13, "bold"), text_color="#475569"
            )
            lbl_val.pack(side="left", padx=5)
            return lbl_val

        self.lbl_pred_kategori = buat_baris_prediksi_modern(
            prediksi_rows_container, "Kategori Risiko"
        )

        btn_container = ctk.CTkFrame(card_prediksi, fg_color="transparent")
        btn_container.grid(row=2, column=0, pady=(10, 15), padx=20, sticky="ew")

        self.btn_periksa = ctk.CTkButton(
            btn_container,
            text="📝    PERIKSA & SIMPAN HASIL",
            command=self.proses_periksa_dan_simpan,
            fg_color="#FF7FA8",
            hover_color="#E9708D",
            height=40,
            font=("Helvetica", 12, "bold"),
            corner_radius=10,
        )
        self.btn_periksa.pack(fill="x", pady=4)

        self.btn_selengkapnya = ctk.CTkButton(
            btn_container,
            text="📊    LIHAT HASIL SELENGKAPNYA",
            command=self.buka_page_hasil_selengkapnya,
            fg_color="#5B8DEF",
            hover_color="#5B8DEF",
            height=40,
            font=("Helvetica", 12, "bold"),
            corner_radius=10,
        )
        self.btn_selengkapnya.pack(fill="x", pady=4)

    def set_bbl_selection(self, pilihan_bbl):
        self.selected_bbl.set(pilihan_bbl)
        if pilihan_bbl == "< 2,5 kg":
            self.btn_bbl_under.configure(
                fg_color="#ECFDF5", border_color="#10B981", text_color="#047857"
            )
            self.btn_bbl_over.configure(
                fg_color="white", border_color="#E2E8F0", text_color="#64748B"
            )
        else:
            self.btn_bbl_under.configure(
                fg_color="white", border_color="#E2E8F0", text_color="#64748B"
            )
            self.btn_bbl_over.configure(
                fg_color="#ECFDF5", border_color="#10B981", text_color="#047857"
            )

    def set_asi_selection(self, pilihan_asi):
        self.selected_asi.set(pilihan_asi)
        if pilihan_asi == "Ya":
            self.btn_asi_yes.configure(
                fg_color="#ECFDF5", border_color="#10B981", text_color="#047857"
            )
            self.btn_asi_no.configure(
                fg_color="white", border_color="#E2E8F0", text_color="#64748B"
            )
        else:
            self.btn_asi_yes.configure(
                fg_color="white", border_color="#E2E8F0", text_color="#64748B"
            )
            self.btn_asi_no.configure(
                fg_color="#FFF1F2", border_color="#F43F5E", text_color="#E11D48"
            )

    def auto_fill_data_balita(self, nama_terpilih):
        """Mencari data balita dan otomatis mengisi Jenis Kelamin & Tanggal Lahir"""
        nama_terpilih = self.ent_nama.get()

        if "Pilih" in nama_terpilih or not nama_terpilih:
            return

        try:
            user_id_aktif = getattr(self.controller, "current_user_id", None)
            biodata = ambil_biodata_balita(user_id_aktif, nama_terpilih)

            if biodata:
                jk_anak = biodata.get("jenis_kelamin", "")
                tgl_lahir_anak = biodata.get("tanggal_lahir", "")

                if jk_anak == "Laki-Laki":
                    self.selected_jk.set("Laki-Laki")
                    self.btn_male.configure(
                        fg_color="#EFF6FF",
                        border_color="#3B82F6",
                        text_color="#1D4ED8",
                    )
                    self.btn_female.configure(
                        fg_color="white",
                        border_color="#E2E8F0",
                        text_color="#64748B",
                    )
                elif jk_anak == "Perempuan":
                    self.selected_jk.set("Perempuan")
                    self.btn_male.configure(
                        fg_color="white",
                        border_color="#E2E8F0",
                        text_color="#64748B",
                    )
                    self.btn_female.configure(
                        fg_color="#FFF1F2",
                        border_color="#E9708D",
                        text_color="#9F1239",
                    )

                if hasattr(self, "cal_lahir"):
                    self.cal_lahir.delete(0, "end")
                    self.cal_lahir.insert(0, str(tgl_lahir_anak))
                    if hasattr(self, "update_umur"):
                        self.update_umur()

                print(f"Berhasil memuat data awal balita: {nama_terpilih}")
            else:
                print("Data balita tidak ditemukan di database untuk user ini.")

        except Exception as e:
            print("Gagal memuat otomatis data indikator ke page pemeriksaan:", e)

    def update_umur(self):
        try:
            tgl_lahir = datetime.strptime(self.cal_lahir.get(), "%d/%m/%Y").date()
            tgl_periksa = datetime.strptime(
                self.cal_periksa.get(), "%d/%m/%Y"
            ).date()
            selisih_hari = (tgl_periksa - tgl_lahir).days
            umur_bulan = max(0, int(selisih_hari / 30.4375))
            self.lbl_usia_auto.configure(text=f"{umur_bulan} Bulan")
            return umur_bulan
        except Exception:
            return 0

    def buka_popup_kalender(self, target_entry):
        popup = ctk.CTkToplevel(self)
        popup.title("Pilih Tanggal")
        popup.geometry("300x320")
        popup.resizable(False, False)

        popup.grab_set()
        popup.attributes("-topmost", True)

        cal = Calendar(
            popup,
            selectbackground="#E9708D",
            selectforeground="white",
            font=("Arial", 10),
            date_pattern="dd/mm/yyyy",
        )
        cal.pack(padx=10, pady=10, fill="both", expand=True)

        def pilih():
            target_entry.delete(0, "end")
            target_entry.insert(0, cal.get_date())
            popup.destroy()
            self.focus_set()
            self.update_umur()

        ctk.CTkButton(
            popup,
            text="Pilih Tanggal",
            fg_color="#E9708D",
            hover_color="#D65D7A",
            font=("Arial", 12, "bold"),
            command=pilih,
        ).pack(pady=(0, 15), padx=20, fill="x")

    def calculate_decimal_age_months(self, birth_date, exam_date):
        try:
            days = (exam_date - birth_date).days
            months = days / 30.4375
            return max(0.0, round(months, 2))
        except Exception:
            return float(self.update_umur())

    def cek_kelengkapan_imunisasi(self, umur_bulan):
        ketentuan = {
            0: ["Hepatitis B (<24 Jam)"],
            1: ["BCG", "Polio Tetes 1"],
            2: ["DPT-HB-Hib 1", "Polio Tetes 2", "Rotavirus (RV) 1", "PCV 1"],
            3: ["DPT-HB-Hib 2", "Polio Tetes 3", "Rotavirus (RV) 2", "PCV 2"],
            4: [
                "DPT-HB-Hib 3",
                "Polio Tetes 4",
                "Polio Suntik (IPV) 1",
                "Rotavirus (RV) 3",
            ],
            9: ["Campak-Rubella (MR)", "Polio Suntik (IPV) 2"],
            10: ["Japanese Encephalitis (JE)"],
            12: ["PCV 3"],
            18: ["DPT-HB-Hib Lanjutan", "Campak Rubella (MR) Lanjutan"],
        }

        vaksin_wajib = []
        for bulan, daftar in ketentuan.items():
            if umur_bulan >= bulan:
                vaksin_wajib.extend(daftar)

        vaksin_kurang = []
        for vks in vaksin_wajib:
            if vks in self.imun_vars:
                if not self.imun_vars[vks].get():
                    vaksin_kurang.append(vks)

        return len(vaksin_kurang) == 0, vaksin_kurang

    def interpolate_standard_row(self, df, target, index_col):
        if target is None or pd.isna(target) or df.empty:
            return None

        df_clean = df.copy()
        if df_clean[index_col].dtype == "object":
            df_clean[index_col] = (
                df_clean[index_col].astype(str).str.replace(",", ".", regex=False)
            )
        df_clean[index_col] = pd.to_numeric(df_clean[index_col], errors="coerce")

        for col in ["L", "M", "S"]:
            if col in df_clean.columns and df_clean[col].dtype == "object":
                df_clean[col] = (
                    df_clean[col].astype(str).str.replace(",", ".", regex=False)
                )
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        df_clean = df_clean.dropna(subset=[index_col])

        if target in df_clean[index_col].values:
            return df_clean[df_clean[index_col] == target].iloc[0]

        df_sorted = df_clean.sort_values(index_col)

        if target < df_sorted[index_col].min():
            return df_sorted.iloc[0]
        if target > df_sorted[index_col].max():
            return df_sorted.iloc[-1]

        lower_df = df_sorted[df_sorted[index_col] <= target].tail(1)
        upper_df = df_sorted[df_sorted[index_col] >= target].head(1)

        if lower_df.empty and upper_df.empty:
            return None
        if lower_df.empty:
            return upper_df.iloc[0]
        if upper_df.empty:
            return lower_df.iloc[0]

        lower_row = lower_df.iloc[0]
        upper_row = upper_df.iloc[0]

        if lower_row[index_col] == upper_row[index_col]:
            return lower_row

        ratio = (target - lower_row[index_col]) / (
            upper_row[index_col] - lower_row[index_col]
        )
        interpolated = lower_row.copy()

        columns_to_interpolate = [
            "L",
            "M",
            "S",
            "SD3neg",
            "SD2neg",
            "SD1neg",
            "SD0",
            "SD1",
            "SD2",
            "SD3",
        ]
        for col in columns_to_interpolate:
            if col in df_clean.columns:
                if col in lower_row and col in upper_row:
                    val_lower = (
                        float(str(lower_row[col]).replace(",", "."))
                        if isinstance(lower_row[col], str)
                        else float(lower_row[col])
                    )
                    val_upper = (
                        float(str(upper_row[col]).replace(",", "."))
                        if isinstance(upper_row[col], str)
                        else float(upper_row[col])
                    )

                    interpolated[col] = val_lower + (val_upper - val_lower) * ratio

        return interpolated

    def load_standard_csv(self, file_path):
        df = pd.read_csv(file_path)
        for col in [
            "tb",
            "umur",
            "L",
            "M",
            "S",
            "SD3neg",
            "SD2neg",
            "SD1neg",
            "SD0",
            "SD1",
            "SD2",
            "SD3",
        ]:
            if col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["L", "M", "S"])
        return df

    def hitung_zscore_lms(self, nilai_riil, row_csv):
        print(repr(row_csv))
        L = float(row_csv["L"])
        M = float(row_csv["M"])
        S = float(row_csv["S"])

        if L == 1.0:
            z_base = (nilai_riil - M) / (M * S)
        elif L != 0:
            z_base = (((nilai_riil / M) ** L) - 1) / (L * S)
        else:
            z_base = math.log(nilai_riil / M) / S

        if z_base < -3.0:
            if L != 0:
                val = 1 + (-3) * L * S
                if val > 0:
                    sd_bawah = M - (M * (val ** (1 / L)))
                else:
                    sd_bawah = M * S
            else:
                sd_bawah = M * S

            if sd_bawah != 0:
                return round(-3.0 + ((nilai_riil - (M - sd_bawah)) / sd_bawah), 2)

        elif z_base > 3.0:
            if L != 0:
                val = 1 + 3 * L * S
                if val > 0:
                    sd_atas = (M * (val ** (1 / L))) - M
                else:
                    sd_atas = M * S
            else:
                sd_atas = M * S

            if sd_atas != 0:
                return round(3.0 + ((nilai_riil - (M + sd_atas)) / sd_atas), 2)

        return round(z_base, 2)

    def kalkulasi_semua_zscore(self, jk, usia, bb, tb, lk):
        err_res = (0.0, "Data Kosong")
        z_bbu, st_bbu = err_res
        z_tbu, st_tbu = err_res
        z_lku, st_lku = err_res
        z_bbtb, st_bbtb = err_res

        try:
            usia = int(usia)
            bb = float(bb)
            tb = float(tb)
            lk = float(lk)
        except (ValueError, TypeError):
            return ((0.0, "Input Tidak Valid"),) * 4

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))

        path_bbu = os.path.join(data_dir, "standar_bbu.csv")
        path_tbu = os.path.join(data_dir, "standar_tbu.csv")
        path_lku = os.path.join(data_dir, "standar_lku.csv")
        path_bbtb_2th = os.path.join(data_dir, "standar_bbtb2th.csv")
        path_bbtb_5th = os.path.join(data_dir, "standar_bbtb5th.csv")

        jk_key = "L" if "LAK" in str(jk).upper() else "P"

        print(f"\n=================== DETAIL KALKULASI Z-SCORE WHO ===================")
        print(f"📌 DATA ANTHROPOMETRI BALITA:")
        print(f"   • JK: {jk} ({jk_key}) | Umur: {usia} Bulan")
        print(f"   • BB: {bb} kg | TB/PB: {tb} cm | LK: {lk} cm")
        print(f"-------------------------------------------------------------------")

        # 1. BB/U
        try:
            df = self.load_standard_csv(path_bbu)
            df_jk = df[df["jk"].astype(str).str.strip().str.upper().str.startswith(jk_key)]
            match = df_jk[df_jk["umur"] == usia]
            match_row = match.iloc[0] if not match.empty else self.interpolate_standard_row(df_jk, usia, "umur")
            if match_row is not None:
                z_bbu = self.hitung_zscore_lms(bb, match_row)
                st_bbu = (
                    "Severely Underweight"
                    if z_bbu < -3.0
                    else "Underweight"
                    if z_bbu < -2.0
                    else "Normal"
                    if z_bbu <= 1.0
                    else "Risk of Overweight"
                )
                print(f"📊 [BB/U]  L: {match_row['L']:<7} | M: {match_row['M']:<7} | S: {match_row['S']:<7} => Z-Score: {z_bbu} ({st_bbu})")
        except Exception as e:
            print("Gagal BB/U:", e)

        # 2. BB/TB
        try:
            if 0 <= usia < 24:
                df = self.load_standard_csv(path_bbtb_2th)
            else:
                df = self.load_standard_csv(path_bbtb_5th)
            df_jk = df[df["jk"].astype(str).str.strip().str.upper().str.startswith(jk_key)]
            if not df_jk.empty:
                tb_hitung = tb
                match_bbtb = self.interpolate_standard_row(df_jk, tb_hitung, "tb")
                if match_bbtb is not None:
                    z_bbtb = self.hitung_zscore_lms(bb, match_bbtb)
                    st_bbtb = (
                        "Severely Wasted"
                        if z_bbtb < -3.0
                        else "Wasted"
                        if z_bbtb < -2.0
                        else "Normal"
                        if z_bbtb <= 1.0
                        else "Possible Risk of Overweight"
                        if z_bbtb <= 2.0
                        else "Overweight"
                        if z_bbtb <= 3.0
                        else "Obese"
                    )
                    print(f"📊 [BB/TB] L: {match_bbtb['L']:<7} | M: {match_bbtb['M']:<7} | S: {match_bbtb['S']:<7} => Z-Score: {z_bbtb} ({st_bbtb})")
        except Exception as e:
            print("Gagal BB/TB:", e)

        # 3. TB/U
        try:
            df = self.load_standard_csv(path_tbu)
            df_jk = df[df["jk"].astype(str).str.strip().str.upper().str.startswith(jk_key)]
            match = df_jk[df_jk["umur"] == usia]
            match_row = match.iloc[0] if not match.empty else self.interpolate_standard_row(df_jk, usia, "umur")
            if match_row is not None:
                z_tbu = self.hitung_zscore_lms(tb, match_row)
                st_tbu = (
                    "Severely Stunted"
                    if z_tbu < -3.0
                    else "Stunted"
                    if z_tbu < -2.0
                    else "Normal"
                    if z_tbu <= 3.0
                    else "Tall"
                )
                print(f"📊 [TB/U]  L: {match_row['L']:<7} | M: {match_row['M']:<7} | S: {match_row['S']:<7} => Z-Score: {z_tbu} ({st_tbu})")
        except Exception as e:
            print("Gagal TB/U:", e)

        # 4. LK/U
        try:
            df = self.load_standard_csv(path_lku)
            df_jk = df[df["jk"].astype(str).str.strip().str.upper().str.startswith(jk_key)]
            match = df_jk[df_jk["umur"] == usia]
            match_row = match.iloc[0] if not match.empty else self.interpolate_standard_row(df_jk, usia, "umur")
            if match_row is not None:
                z_lku = self.hitung_zscore_lms(lk, match_row)
                st_lku = (
                    "Mikrosefali"
                    if z_lku < -3.0
                    else "Normal"
                    if z_lku <= 2.0
                    else "Makrosefali"
                )
                print(f"📊 [LK/U]  L: {match_row['L']:<7} | M: {match_row['M']:<7} | S: {match_row['S']:<7} => Z-Score: {z_lku} ({st_lku})")
        except Exception as e:
            print("Gagal LK/U:", e)

        print(f"===================================================================\n")

        return (
            (z_bbu, st_bbu),
            (z_bbtb, st_bbtb),
            (z_lku, st_lku),
            (z_tbu, st_tbu),
        )

    def proses_periksa_dan_simpan(self):
        """Fungsi utama pemrosesan data medis"""
        nama = self.ent_nama.get()
        bb_lahir = self.selected_bbl.get()
        jk = self.selected_jk.get()

        bb_sekarang_raw = self.ent_bb_sekarang.get()
        tb_raw = self.ent_tb.get()
        lk_raw = self.ent_lk.get()

        usia_bulan = self.update_umur()

        try:
            d1_obj = datetime.strptime(self.cal_lahir.get(), "%d/%m/%Y").date()
            d2_obj = datetime.strptime(self.cal_periksa.get(), "%d/%m/%Y").date()
            usia_bulan_decimal = self.calculate_decimal_age_months(d1_obj, d2_obj)
        except Exception as e:
            print("Gagal konversi desimal usia:", e)
            usia_bulan_decimal = float(usia_bulan)

        if "Pilih" in nama or not nama or not bb_lahir or not jk:
            messagebox.showerror(
                "Error",
                "Nama Balita, Jenis Kelamin, dan Berat Badan Lahir wajib"
                " diisi/dipilih!",
            )
            return

        try:
            bb_sekarang = float(bb_sekarang_raw)
            tb_angka = float(tb_raw)
            lk_angka = float(lk_raw)
        except ValueError:
            messagebox.showerror(
                "Error", "Semua parameter medis wajib diisi dengan angka numerik valid!"
            )
            return

        if not (1.5 <= bb_sekarang <= 30):
            messagebox.showerror(
                "Input Tidak Logis",
                "Berat Badan Sekarang harus di antara 1.5 kg sampai 30 kg!",
            )
            return

        if not (35 <= tb_angka <= 130):
            messagebox.showerror(
                "Input Tidak Logis",
                "Tinggi atau Panjang Badan harus di antara 35 cm sampai 130 cm!",
            )
            return

        if not (30 <= lk_angka <= 60):
            messagebox.showerror(
                "Input Tidak Logis",
                "Lingkar Kepala harus di antara 30 cm sampai 60 cm!",
            )
            return

        # 1. ASUPAN GIZI
        if usia_bulan < 6:
            persentase_gizi = 100.0
            status_gizi = "Baik"
            warna_gizi = "#10B981"
        else:
            bobot_nilai = {
                "Sangat Sering": 5,
                "Sering": 4,
                "Biasa": 3,
                "Kadang-Kadang": 2,
                "Kurang": 1,
                "Tidak Pernah": 0,
            }
            skor_total = sum(
                bobot_nilai.get(v.get(), 0) for v in self.ffq_vars.values()
            )
            persentase_gizi = round((skor_total / 125) * 100, 2)

            if persentase_gizi < 40.0:
                status_gizi = "Kurang"
                warna_gizi = "red"
            elif 40.0 <= persentase_gizi <= 60.0:
                status_gizi = "Cukup"
                warna_gizi = "orange"
            else:
                status_gizi = "Baik"
                warna_gizi = "green"

        self.res_gizi.configure(
            text=f"{status_gizi} ({persentase_gizi}%)", text_color=warna_gizi
        )

        # 2. CEK IMUNISASI
        status_lengkap, vaksin_kurang = self.cek_kelengkapan_imunisasi(usia_bulan)

        if status_lengkap:
            self.res_imun.configure(text="Lengkap", text_color="green")
            self.label_status_imun.configure(text="", text_color="green")
        else:
            self.res_imun.configure(text="Tidak Lengkap", text_color="red")

            chunk_size = 3
            vaksin_chunks = [
                ", ".join(vaksin_kurang[i : i + chunk_size])
                for i in range(0, len(vaksin_kurang), chunk_size)
            ]
            teks_kurang_formatted = "\n".join(vaksin_chunks)

            self.label_status_imun.configure(
                text=f"⚠️ Belum dilakukan:\n{teks_kurang_formatted}",
                text_color="red",
                justify="left",
            )

        # 3. PERHITUNGAN Z-SCORE
        hasil_z = self.kalkulasi_semua_zscore(
            jk, usia_bulan, bb_sekarang, tb_angka, lk_angka
        )
        res_bbu, res_bbtb, res_lku, res_tbu = hasil_z

        val_bbu = f"{float(res_bbu[0]):.2f}"
        val_bbtb = f"{float(res_bbtb[0]):.2f}"
        val_tbu = f"{float(res_tbu[0]):.2f}"
        val_lku = f"{float(res_lku[0]):.2f}"

        try:
            self.lbl_list_bbu.configure(text=f"{val_bbu} ({res_bbu[1]})")
            self.lbl_list_bbtb.configure(text=f"{val_bbtb} ({res_bbtb[1]})")
            self.lbl_list_tbu.configure(text=f"{val_tbu} ({res_tbu[1]})")
            self.lbl_list_lku.configure(text=f"{val_lku} ({res_lku[1]})")
        except Exception as gui_err:
            print("Gagal update teks GUI kanan:", gui_err)

        # 4. PREDIKSI ML
        bbl_encoded = 1 if bb_lahir == "> 2,5 kg" else 0
        gizi_encoded = (
            2 if status_gizi == "Baik" else 1 if status_gizi == "Cukup" else 0
        )
        imun_encoded = 1 if status_lengkap else 0
        asi_encoded = 1 if self.selected_asi.get() == "Ya" else 0

        kat_risiko = "Rendah"
        warna_risiko = "#10B981"

        if self.model_rf is not None:
            try:
                features = pd.DataFrame(
                    [[bbl_encoded, gizi_encoded, imun_encoded, asi_encoded]],
                    columns=["bbl", "asupan_gizi", "imunisasi", "asi_eksklusif"],
                )
                prediksi_code = self.model_rf.predict(features)[0]

                if prediksi_code == 2:
                    kat_risiko = "Tinggi"
                    warna_risiko = "#EF4444"
                elif prediksi_code == 1:
                    kat_risiko = "Sedang"
                    warna_risiko = "#F59E0B"
                else:
                    kat_risiko = "Rendah"
                    warna_risiko = "#10B981"

            except Exception as e:
                print("Fallback manual risiko:", e)
                if res_bbtb[0] < -3.0 or res_tbu[0] < -3.0:
                    kat_risiko = "Tinggi"
                    warna_risiko = "#EF4444"
                else:
                    kat_risiko = "Rendah"
                    warna_risiko = "#10B981"
        else:
            if res_bbtb[0] < -3.0 or res_tbu[0] < -3.0 or res_lku[0] < -3.0:
                kat_risiko = "Tinggi"
                warna_risiko = "#EF4444"
            elif (
                (-3.0 <= res_bbtb[0] < -2.0)
                or (not status_lengkap)
                or (status_gizi == "Kurang")
            ):
                kat_risiko = "Sedang"
                warna_risiko = "#F59E0B"
            else:
                kat_risiko = "Rendah"
                warna_risiko = "#10B981"

        self.lbl_pred_kategori.configure(text=kat_risiko, text_color=warna_risiko)

        # 5. SIMPAN KE DATABASE
        try:
            m = re.search(r"[\d]+(?:[\.,]\d+)?", str(bb_lahir))
            bbl_numeric = (
                float(m.group().replace(",", "."))
                if m
                else (
                    2.6
                    if ">" in str(bb_lahir)
                    else 2.0
                    if "<" in str(bb_lahir)
                    else 2.5
                )
            )
        except Exception:
            bbl_numeric = 2.5

        data_medis = {
            "tanggal_pemeriksaan": self.cal_periksa.get(),
            "usia_bulan": usia_bulan,
            "berat_badan_lahir": bbl_numeric,
            "berat_badan": bb_sekarang,
            "tinggi_badan": tb_angka,
            "lingkar_kepala": lk_angka,
            "asi": self.selected_asi.get(),
            "imunisasi": "Lengkap" if status_lengkap else "Tidak Lengkap",
            "asupan_gizi": status_gizi,
            "zscore": {
                "BB/U": val_bbu,
                "BB/TB": val_bbtb,
                "TB/U": val_tbu,
                "LK/U": val_lku,
            },
            "status_text": {
                "BB/U": res_bbu[1],
                "BB/TB": res_bbtb[1],
                "TB/U": res_tbu[1],
                "LK/U": res_lku[1],
            },
            "tingkat_risiko": kat_risiko,
        }

        try:
            user_id_aktif = getattr(self.controller, "current_user_id", None)
            simpan_ok = update_data_pemeriksaan(user_id_aktif, nama, data_medis)
            if not simpan_ok:
                messagebox.showerror(
                    "Error", "Gagal menyimpan data pemeriksaan ke database."
                )
                return
        except Exception as db_err:
            print(f"[DATABASE ERROR]: {db_err}")

        # 6. NOTIFIKASI
        if status_lengkap:
            messagebox.showinfo(
                "Sukses",
                f"Data Pemeriksaan {nama} berhasil diperiksa & disimpan!",
            )
        else:
            messagebox.showwarning(
                "Peringatan",
                f"Data {nama} disimpan, namun imunisasi belum lengkap untuk usia"
                f" {usia_bulan} bulan!\n\nVaksin yang kurang:"
                f" {', '.join(vaksin_kurang)}",
            )

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        try:
            user_id_aktif = getattr(self.controller, "current_user_id", None)
            list_nama = (
                ambil_daftar_nama_balita(user_id_aktif) if user_id_aktif else []
            )
            self.ent_nama.configure(values=list_nama)
        except Exception as e:
            print("Gagal memperbarui daftar nama ComboBox:", e)

    def buka_page_hasil_selengkapnya(self):
        nama_balita = self.ent_nama.get()

        if "Pilih" in nama_balita or not nama_balita:
            messagebox.showwarning(
                "Peringatan", "Silakan pilih nama balita terlebih dahulu!"
            )
            return

        popup_window = ctk.CTkToplevel(self)
        popup_window.title(
            f"SIDERIS - Dashboard Hasil & Kurva Pertumbuhan: {nama_balita}"
        )
        popup_window.geometry("1250x720")

        popup_window.withdraw()
        popup_window.lift()
        popup_window.attributes("-topmost", True)
        popup_window.deiconify()
        popup_window.after(
            100,
            lambda: [
                popup_window.attributes("-topmost", False),
                popup_window.focus_force(),
            ],
        )

        dashboard_frame = HasilPage(popup_window, controller=self.controller)
        dashboard_frame.pack(fill="both", expand=True)

        popup_window.update_idletasks()

        if dashboard_frame.combo_nama is not None:
            dashboard_frame.combo_nama.configure(values=[nama_balita])
            dashboard_frame.combo_nama.set(nama_balita)
            dashboard_frame.update_tanggal_options(nama_balita)


class HasilPage(ctk.CTkFrame):

    def __init__(self, parent, controller=None):
        super().__init__(parent, fg_color="#F8FAFC")
        self.controller = controller

        self.combo_nama = None
        self.combo_tanggal = None

        self.grid_columnconfigure(0, weight=52, uniform="dashboard")
        self.grid_columnconfigure(1, weight=48, uniform="dashboard")
        self.grid_rowconfigure(1, weight=1)

        self.init_header()

        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(
            row=1, column=0, sticky="nsew", padx=(20, 10), pady=(4, 12)
        )

        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_rowconfigure(0, weight=0)
        self.left_container.grid_rowconfigure(1, weight=0)
        self.left_container.grid_rowconfigure(2, weight=0)
        self.left_container.grid_rowconfigure(3, weight=1)

        self.init_left_components()
        self.init_right_side()

        try:
            user_id_aktif = getattr(self.controller, "current_user_id", None)
            nama_list = (
                ambil_daftar_nama_balita(user_id_aktif) if user_id_aktif else []
            )
            if nama_list:
                self.combo_nama.configure(values=nama_list)
                self.combo_nama.set(nama_list[0])
                self.update_tanggal_options(nama_list[0])
            else:
                self.combo_nama.set("")
                self.combo_tanggal.set("")
                self.bersihkan_tampilan_kosong()
        except Exception as e:
            print("Gagal set data awal:", e)
            self.bersihkan_tampilan_kosong()

    def init_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(14, 4)
        )
        ctk.CTkLabel(
            header_frame,
            text="Hasil Pemeriksaan",
            font=("Inter", 20, "bold"),
            text_color="#0F172A",
        ).pack(side="left")
        ctk.CTkLabel(
            header_frame,
            text=(
                "Hasil pemeriksaan dan status pertumbuhan anak berdasarkan standar"
                " WHO."
            ),
            font=("Inter", 12),
            text_color="#64748B",
        ).pack(side="left", padx=12, pady=(4, 0))

    def init_left_components(self):
        top_info_panel = ctk.CTkFrame(
            self.left_container,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0",
        )
        top_info_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_info_panel.grid_columnconfigure((0, 1), weight=50, uniform="top_panel")

        sub_kiri = ctk.CTkFrame(top_info_panel, fg_color="transparent")
        sub_kiri.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        profile_frame = ctk.CTkFrame(sub_kiri, fg_color="transparent")
        profile_frame.pack(fill="x", anchor="n")

        self.profile_avatar = ctk.CTkLabel(
            profile_frame,
            text="👶",
            font=("Inter", 32),
            width=60,
            height=60,
            fg_color="#F1F5F9",
            corner_radius=30,
        )
        self.profile_avatar.pack(side="left", padx=(0, 12))

        txt_meta_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        txt_meta_frame.pack(side="left", fill="both", expand=True)

        title_container = ctk.CTkFrame(txt_meta_frame, fg_color="transparent")
        title_container.pack(fill="x", anchor="w", pady=(2, 2))

        self.lbl_nama_header = ctk.CTkLabel(
            title_container, text="-", font=("Inter", 20, "bold"), text_color="#0F172A"
        )
        self.lbl_nama_header.pack(side="left")
        self.lbl_gender_tag = ctk.CTkLabel(
            title_container,
            text="-",
            font=("Inter", 10, "bold"),
            text_color="#475569",
            fg_color="#F1F5F9",
            corner_radius=10,
            padx=8,
            pady=2,
        )
        self.lbl_gender_tag.pack(side="left", padx=8)

        form_frame = ctk.CTkFrame(sub_kiri, fg_color="transparent")
        form_frame.pack(fill="x", anchor="s", pady=(16, 0))

        self.combo_nama = ctk.CTkComboBox(form_frame, values=[])

        group_tgl = ctk.CTkFrame(form_frame, fg_color="transparent")
        group_tgl.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(
            group_tgl,
            text="Tanggal Periksa",
            font=("Inter", 11, "bold"),
            text_color="#64748B",
        ).pack(anchor="w", pady=(0, 4))
        self.combo_tanggal = ctk.CTkComboBox(
            group_tgl,
            values=[],
            command=self.update_tampilan,
            height=32,
            font=("Inter", 12),
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            corner_radius=8,
        )
        self.combo_tanggal.pack(fill="x")

        sub_kanan = ctk.CTkFrame(top_info_panel, fg_color="transparent")
        sub_kanan.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        sub_kanan.grid_columnconfigure((0, 1), weight=1, uniform="sub_cards")
        sub_kanan.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform="sub_cards")

        def create_top_metric_card(
            parent, title, value_holder_name, icon, bg_color, r, c
        ):
            card = ctk.CTkFrame(parent, fg_color="transparent")
            card.grid(row=r, column=c, sticky="nsew", padx=4, pady=0)
            ctk.CTkLabel(
                card,
                text=icon,
                font=("Inter", 12),
                width=32,
                height=32,
                fg_color=bg_color,
                corner_radius=8,
            ).pack(side="left", padx=(0, 10))
            info_sub = ctk.CTkFrame(card, fg_color="transparent")
            info_sub.pack(side="left", anchor="center")
            ctk.CTkLabel(
                info_sub,
                text=title,
                font=("Inter", 11),
                text_color="#64748B",
                anchor="w",
            ).pack(anchor="w", pady=(0, 1))
            val_lbl = ctk.CTkLabel(
                info_sub,
                text="-",
                font=("Inter", 13, "bold"),
                text_color="#0F172A",
                anchor="w",
            )
            val_lbl.pack(anchor="w", pady=0)
            setattr(self, value_holder_name, val_lbl)

        create_top_metric_card(
            sub_kanan, "Berat Badan", "lbl_bb", "⚖️", "#EFF6FF", 0, 0
        )
        create_top_metric_card(
            sub_kanan, "Tinggi Badan", "lbl_tb", "📏", "#FFFBEB", 1, 0
        )
        create_top_metric_card(
            sub_kanan, "Lingkar Kepala", "lbl_lk", "🧠", "#ECFDF5", 2, 0
        )
        create_top_metric_card(
            sub_kanan, "Usia", "lbl_usia", "👶", "#EFF6FF", 3, 0
        )
        create_top_metric_card(
            sub_kanan, "Berat Badan Lahir", "lbl_bbl", "⏲️", "#F0FDF4", 0, 1
        )
        create_top_metric_card(
            sub_kanan, "Riwayat Imunisasi", "lbl_imunisasi", "💉", "#FFF1F2", 1, 1
        )
        create_top_metric_card(
            sub_kanan, "Asupan Gizi", "lbl_gizi", "🥦", "#F3E8FF", 2, 1
        )
        create_top_metric_card(
            sub_kanan, "ASI Eksklusif", "lbl_asi", "🍼", "#E0F2FE", 3, 1
        )

        self.init_zscore_table(self.left_container)

        bottom_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, sticky="nsew")
        bottom_frame.grid_rowconfigure(0, weight=1)

        bottom_frame.grid_columnconfigure(0, weight=35, uniform="bottom_split")
        bottom_frame.grid_columnconfigure(1, weight=65, uniform="bottom_split")

        card_hasil = ctk.CTkFrame(
            bottom_frame,
            fg_color="#FFF1F2",
            corner_radius=12,
            border_width=1,
            border_color="#FFE4E6",
        )
        card_hasil.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(
            card_hasil,
            text="📋 Hasil Pemeriksaan",
            font=("Inter", 13, "bold"),
            text_color="#9F1239",
        ).pack(anchor="w", padx=14, pady=(12, 8))

        detail_grid = ctk.CTkFrame(card_hasil, fg_color="transparent")
        detail_grid.pack(fill="x", padx=14)
        detail_grid.grid_columnconfigure(0, weight=0, minsize=90)
        ctk.CTkLabel(
            detail_grid,
            text="Tingkat Risiko",
            font=("Inter", 11),
            text_color="#475569",
        ).grid(row=1, column=0, sticky="w", pady=3)
        self.lbl_badge_risk = ctk.CTkLabel(
            detail_grid,
            text="-",
            fg_color="#F1F5F9",
            text_color="#475569",
            font=("Inter", 10, "bold"),
            corner_radius=6,
            height=22,
            width=80,
        )
        self.lbl_badge_risk.grid(row=1, column=1, sticky="w", pady=3)

        card_saran = ctk.CTkFrame(
            bottom_frame,
            fg_color="#F0FDF4",
            corner_radius=12,
            border_width=1,
            border_color="#DCFCE7",
        )
        card_saran.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(
            card_saran,
            text="✅ Saran Intervensi",
            font=("Inter", 13, "bold"),
            text_color="#166534",
        ).pack(anchor="w", padx=16, pady=(12, 6))
        self.saran_container = ctk.CTkFrame(card_saran, fg_color="transparent")
        self.saran_container.pack(fill="x", padx=16, pady=(0, 10))

    def init_zscore_table(self, master):
        table_frame = ctk.CTkFrame(
            master,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0",
        )
        table_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        table_frame.grid_columnconfigure(0, weight=35)
        table_frame.grid_columnconfigure(1, weight=13)
        table_frame.grid_columnconfigure(2, weight=15)
        table_frame.grid_columnconfigure(3, weight=37)

        header_title_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_title_frame.grid(
            row=0, column=0, columnspan=4, sticky="nw", padx=16, pady=(5, 6)
        )

        title_txt_container = ctk.CTkFrame(
            header_title_frame, fg_color="transparent"
        )
        title_txt_container.pack(side="left")

        lbl_atas = ctk.CTkLabel(
            title_txt_container,
            text="Status Pertumbuhan (Antropometri)",
            font=("Inter", 14, "bold"),
            text_color="#0F172A",
        )
        lbl_atas.grid(row=0, column=0, sticky="w", pady=(6, 0))

        lbl_bawah = ctk.CTkLabel(
            title_txt_container,
            text="Penilaian berdasarkan standar WHO (Z-Score)",
            font=("Inter", 11),
            text_color="#64748B",
        )
        lbl_bawah.grid(row=1, column=0, sticky="w", pady=0)

        headers = ["Indikator", "Z-Score", "Kategori", "Interpretasi"]
        for i, h in enumerate(headers):
            if i in [1, 2]:
                lbl = ctk.CTkLabel(
                    table_frame,
                    text=h,
                    font=("Inter", 11, "bold"),
                    text_color="#64748B",
                )
                lbl.grid(row=1, column=i, padx=4, pady=(4, 8))
            else:
                lbl = ctk.CTkLabel(
                    table_frame,
                    text=h,
                    font=("Inter", 11, "bold"),
                    text_color="#64748B",
                )
                lbl.grid(
                    row=1,
                    column=i,
                    padx=16 if i == 0 else 4,
                    pady=(4, 8),
                    sticky="w",
                )

        self.table_rows = {}
        urutan = [
            ("BB/U", "Berat Badan/Umur", "🎛️", "#EFF6FF"),
            ("TB/U", "Tinggi Badan/Umur", "📐", "#EFF6FF"),
            ("BB/TB", "Berat Badan/Tinggi Badan", "🧬", "#E0F2FE"),
            ("LK/U", "Lingkar Kepala/Umur", "🧠", "#E0F2FE"),
        ]

        for idx, (key, title, icon_char, icon_bg) in enumerate(urutan):
            row_num = idx + 2
            table_frame.grid_rowconfigure(row_num, weight=0)

            indicator_cell = ctk.CTkFrame(table_frame, fg_color="transparent")
            indicator_cell.grid(row=row_num, column=0, padx=16, pady=6, sticky="w")

            item_icon = ctk.CTkLabel(
                indicator_cell,
                text=icon_char,
                font=("Inter", 10),
                width=22,
                height=22,
                fg_color=icon_bg,
                corner_radius=5,
            )
            item_icon.pack(side="left", padx=(0, 10))

            lbl_t = ctk.CTkLabel(
                indicator_cell,
                text=title,
                font=("Inter", 11, "bold"),
                text_color="#1E293B",
                pady=0,
            )
            lbl_t.pack(side="left", anchor="center", pady=0)

            z_lbl = ctk.CTkLabel(
                table_frame,
                text="-",
                font=("Inter", 12, "bold"),
                text_color="#0F172A",
            )
            z_lbl.grid(row=row_num, column=1, padx=4, pady=6)

            k_lbl = ctk.CTkLabel(
                table_frame,
                text="-",
                corner_radius=6,
                font=("Inter", 9, "bold"),
                width=80,
                height=18,
            )
            k_lbl.grid(row=row_num, column=2, padx=4, pady=6)

            i_lbl = ctk.CTkLabel(
                table_frame,
                text="-",
                font=("Inter", 11),
                text_color="#334155",
                justify="left",
            )
            i_lbl.grid(row=row_num, column=3, padx=4, pady=6, sticky="w")

            self.table_rows[key] = {"z": z_lbl, "k": k_lbl, "i": i_lbl}

    def init_right_side(self):
        right_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0",
        )
        right_container.grid(
            row=1, column=1, sticky="nsew", padx=(10, 20), pady=(4, 12)
        )

        ctk.CTkLabel(
            right_container,
            text="📊 Grafik Pertumbuhan (WHO)",
            font=("Inter", 14, "bold"),
            text_color="#0F172A",
        ).pack(pady=(12, 4))

        self.fig_container = ctk.CTkFrame(right_container, fg_color="transparent")
        self.fig_container.pack(fill="both", expand=True, padx=12, pady=4)

        legend_parent = ctk.CTkFrame(
            right_container,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
        )
        legend_parent.pack(fill="x", padx=14, pady=(4, 14))

        ctk.CTkLabel(
            legend_parent,
            text="Keterangan Ambang Batas (Z-score WHO)",
            font=("Inter", 11, "bold"),
            text_color="#1E3A8A",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(8, 6))

        legend_parent.grid_columnconfigure(
            (0, 1, 2, 3), weight=25, uniform="legend_cols"
        )

        def add_legend_item(parent, color, text_top, text_bottom, r, c):
            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            item_frame.grid(row=r, column=c, sticky="new", padx=4, pady=0)

            dot = ctk.CTkLabel(
                item_frame, text="●", font=("Inter", 10), text_color=color
            )
            dot.pack(side="left", anchor="w", padx=(2, 4))

            sd_lbl = ctk.CTkLabel(
                item_frame,
                text=text_top,
                font=("Inter", 9, "bold"),
                text_color="#1E293B",
                width=42,
                anchor="w",
            )
            sd_lbl.pack(side="left", anchor="w")

            desc_lbl = ctk.CTkLabel(
                item_frame,
                text=text_bottom,
                font=("Inter", 9),
                text_color="#64748B",
                justify="left",
                anchor="w",
            )
            desc_lbl.pack(side="left", fill="x", expand=True, anchor="w")

        def add_section_header(parent, text, r):
            header = ctk.CTkLabel(
                parent,
                text=text,
                font=("Inter", 9, "bold"),
                text_color="#1E40AF",
                anchor="w",
            )
            header.grid(
                row=r, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 2)
            )

        add_section_header(
            legend_parent,
            "1. Berat Badan menurut Umur (BB/U) anak usia 0 - 60 bulan",
            r=1,
        )
        add_legend_item(legend_parent, "#DC2626", "< -3 SD", "Sangat Kurang", 2, 0)
        add_legend_item(legend_parent, "#EA580C", "-3 s.d. < -2 SD", "Kurang", 2, 1)
        add_legend_item(legend_parent, "#16A34A", "-2 s.d. +1 SD", "Normal", 2, 2)
        add_legend_item(
            legend_parent, "#2563EB", "> +1 SD", "Risiko BB Lebih", 2, 3
        )

        add_section_header(
            legend_parent,
            "2. Tinggi Badan menurut Umur (TB/U) anak usia 0 - 60 bulan",
            r=3,
        )
        add_legend_item(legend_parent, "#DC2626", "< -3 SD", "Sangat Pendek", 4, 0)
        add_legend_item(legend_parent, "#EA580C", "-3 s.d. < -2 SD", "Pendek", 4, 1)
        add_legend_item(legend_parent, "#16A34A", "-2 s.d. +3 SD", "Normal", 4, 2)
        add_legend_item(legend_parent, "#2563EB", "> +3 SD", "Tinggi", 4, 3)

        add_section_header(
            legend_parent,
            "3. Berat Badan menurut Tinggi Badan (BB/TB) anak usia 0 - 60 bulan",
            r=5,
        )
        add_legend_item(legend_parent, "#DC2626", "< -3 SD", "Gizi Buruk", 6, 0)
        add_legend_item(
            legend_parent, "#EA580C", "-3 s.d. < -2 SD", "Gizi Kurang", 6, 1
        )
        add_legend_item(legend_parent, "#16A34A", "-2 s.d. +1 SD", "Gizi Baik", 6, 2)
        add_legend_item(
            legend_parent, "#2563EB", "> +1 s.d. +2 SD", "Risiko Gizi Lebih", 7, 0
        )
        add_legend_item(
            legend_parent, "#7C3AED", "> +2 s.d. +3 SD", "Gizi Lebih", 7, 1
        )
        add_legend_item(legend_parent, "#F43F5E", "> +3 SD", "Obesitas", 7, 2)

        add_section_header(
            legend_parent,
            "4. Lingkar Kepala menurut Umur (LK/U) anak usia 0 - 60 bulan",
            r=8,
        )
        add_legend_item(legend_parent, "#DC2626", "< -3 SD", "Mikrosefali", 9, 0)
        add_legend_item(
            legend_parent, "#16A34A", "≥ -3 s.d. ≤ +2 SD", "Normal", 9, 1
        )
        add_legend_item(legend_parent, "#2563EB", "> +2 SD", "Makrosefali", 9, 2)

    def load_data_for_nama_tgl(self, nama, tgl):
        user_id_aktif = getattr(self.controller, "current_user_id", None)
        if not nama or not tgl:
            return None

        row = ambil_data_sideris_by_nama(user_id_aktif, nama)
        if not row:
            return None

        tgl_db = row.get("tanggal_pemeriksaan") or row.get("tanggal_periksa")
        if tgl_db != tgl:
            return None

        return {
            "nama": row.get("nama"),
            "tanggal_lahir": row.get("tanggal_lahir"),
            "gender": row.get("jenis_kelamin") or row.get("gender"),
            "tanggal_periksa": tgl_db,
            "usia": (
                f"{row.get('usia_bulan')} Bulan"
                if row.get("usia_bulan") is not None
                else "-"
            ),
            "berat_badan": (
                f"{row.get('berat_badan')} kg"
                if row.get("berat_badan") is not None
                else "-"
            ),
            "tinggi_badan": (
                f"{row.get('tinggi_badan')} cm"
                if row.get("tinggi_badan") is not None
                else "-"
            ),
            "lingkar_kepala": (
                f"{row.get('lingkar_kepala')} cm"
                if row.get("lingkar_kepala") is not None
                else "-"
            ),
            "bbl": (
                f"{row.get('berat_badan_lahir')} kg"
                if row.get("berat_badan_lahir") is not None
                else "-"
            ),
            "asi_eksklusif": row.get("asi") or "-",
            "imunisasi": row.get("imunisasi") or "-",
            "asupan_gizi": row.get("asupan_gizi") or "-",
            "zscore": {
                "BB/U": (
                    row.get("bb_u_zscore")
                    if row.get("bb_u_zscore") is not None
                    else 0.0
                ),
                "TB/U": (
                    row.get("tb_u_zscore")
                    if row.get("tb_u_zscore") is not None
                    else 0.0
                ),
                "BB/TB": (
                    row.get("bb_tb_zscore")
                    if row.get("bb_tb_zscore") is not None
                    else 0.0
                ),
                "LK/U": (
                    row.get("lk_u_zscore")
                    if row.get("lk_u_zscore") is not None
                    else 0.0
                ),
            },
            "status_text": {
                "BB/U": row.get("bb_u_status") or "-",
                "TB/U": row.get("tb_u_status") or "-",
                "BB/TB": row.get("bb_tb_status") or "-",
                "LK/U": row.get("lk_u_status") or "-",
            },
        }

    def update_tanggal_options(self, nama):
        user_id_aktif = getattr(self.controller, "current_user_id", None)
        row = ambil_data_sideris_by_nama(user_id_aktif, nama)
        tgl_db = row.get("tanggal_pemeriksaan") or row.get("tanggal_periksa")
        if row and tgl_db:
            self.combo_tanggal.configure(values=[tgl_db])
            self.combo_tanggal.set(tgl_db)
            self.update_tampilan(tgl_db)
        else:
            self.combo_tanggal.configure(values=[])
            self.combo_tanggal.set("")

    def update_tampilan(self, tgl):
        nama = self.combo_nama.get()
        data = self.load_data_for_nama_tgl(nama, tgl)
        if not data:
            self.bersihkan_tampilan_kosong()
            return

        self.lbl_usia.configure(text=str(data.get("usia", "-")))
        self.lbl_bb.configure(text=str(data.get("berat_badan", "-")))
        self.lbl_tb.configure(text=str(data.get("tinggi_badan", "-")))
        self.lbl_lk.configure(text=str(data.get("lingkar_kepala", "-")))

        try:
            bbl_raw = str(data.get("bbl", "0"))
            bbl_angka = (
                float(bbl_raw.split()[0]) if " " in bbl_raw else float(bbl_raw)
            )
            status_bbl = ">2,5 kg" if bbl_angka >= 2.5 else "<2,5 kg"
        except Exception:
            status_bbl = "-"
        self.lbl_bbl.configure(text=status_bbl)

        status_asi = str(data.get("asi_eksklusif", "-"))
        if status_asi.lower() in ["ya", "yes", "true"]:
            tampilan_asi = "Ya"
        elif status_asi.lower() in ["tidak", "no", "false"]:
            tampilan_asi = "Tidak"
        else:
            tampilan_asi = status_asi
        self.lbl_asi.configure(text=tampilan_asi)

        self.lbl_imunisasi.configure(text=data.get("imunisasi", "Lengkap"))
        self.lbl_gizi.configure(text=data.get("asupan_gizi", "Baik"))

        self.lbl_nama_header.configure(text=nama)

        if data.get("gender") == "Laki-Laki":
            self.profile_avatar.configure(text="👦", fg_color="#EFF6FF")
            self.lbl_gender_tag.configure(
                text="Laki-Laki", text_color="#1E40AF", fg_color="#DBEAFE"
            )
        else:
            self.profile_avatar.configure(text="👧", fg_color="#FCE7F3")
            self.lbl_gender_tag.configure(
                text="Perempuan", text_color="#DB2777", fg_color="#FFF1F2"
            )

        warna_map = {
            "Normal": "#DCFCE7",
            "Severely Stunted": "#FFE4E6",
            "Stunted": "#FFE4E6",
            "Tinggi": "#DBEAFE",
            "Severely Underweight": "#FFE4E6",
            "Underweight": "#FEF3C7",
            "Risk of Overweight": "#FFE4E6",
            "Severely Wasted": "#FFE4E6",
            "Wasted": "#FFE4E6",
            "Risiko Gizi Lebih": "#FEF3C7",
            "Overweight": "#FFE4E6",
            "Obesitas": "#FFE4E6",
            "Mikrosefali": "#FEF3C7",
            "Makrosefali": "#FFE4E6",
        }
        text_map = {
            "Normal": "#16A34A",
            "Severely Stunted": "#B91C1C",
            "Stunted": "#E11D48",
            "Tinggi": "#1E40AF",
            "Severely Underweight": "#B91C1C",
            "Underweight": "#D97706",
            "Risk of Overweight": "#E11D48",
            "Severely Wasted": "#B91C1C",
            "Wasted": "#E11D48",
            "Risiko Gizi Lebih": "#D97706",
            "Overweight": "#E11D48",
            "Obesitas": "#B91C1C",
            "Mikrosefali": "#D97706",
            "Makrosefali": "#B91C1C",
        }
        interp_map = {
            "Normal": "Sesuai standar pertumbuhan.",
            "Severely Stunted": "Tinggi badan sangat pendek.",
            "Stunted": "Tinggi badan pendek.",
            "Tinggi": "Tinggi badan di atas normal.",
            "Severely Underweight": "Berat badan sangat kurang.",
            "Underweight": "Berat badan kurang.",
            "Risk of Overweight": "Berisiko berat badan lebih.",
            "Severely Wasted": "Gizi buruk.",
            "Wasted": "Gizi kurang.",
            "Risiko Gizi Lebih": "Berisiko gizi lebih.",
            "Overweight": "Mengalami gizi lebih.",
            "Obesitas": "Mengalami obesitas.",
            "Mikrosefali": "Lingkar kepala lebih kecil dari normal.",
            "Makrosefali": "Lingkar kepala lebih besar dari normal.",
        }

        for k, widgets in self.table_rows.items():
            z_val = data["zscore"].get(k, 0.0)
            kat = data["status_text"].get(k, "Normal")

            widgets["z"].configure(
                text=(
                    f"{z_val:+.2f}"
                    if isinstance(z_val, (int, float)) and z_val > 0
                    else f"{z_val}"
                )
            )
            widgets["k"].configure(
                text=kat,
                fg_color=warna_map.get(kat, "#E2E8F0"),
                text_color=text_map.get(kat, "#1E293B"),
            )
            widgets["i"].configure(
                text=interp_map.get(kat, "Sesuai standar pertumbuhan.")
            )

        status_bbtb = data["status_text"].get("BB/TB", "Normal")
        status_tbu = data["status_text"].get("TB/U", "Normal")
        status_bbu = data["status_text"].get("BB/U", "Normal")
        status_lku = data["status_text"].get("LK/U", "Normal")

        masalah_list = []
        badge_list = []

        if any(
            x in status_bbtb
            for x in ["Wasted", "Wasting", "Kurus", "Gizi Kurang", "Gizi Buruk"]
        ):
            masalah_list.append("Wasting (Gizi Kurang/Buruk)")
            badge_list.append(status_bbtb)
        if any(x in status_tbu for x in ["Stunted", "Stunting", "Pendek"]):
            masalah_list.append("Stunting")
            badge_list.append(status_tbu)
        if any(
            x in status_bbu for x in ["Underweight", "Kurang", "BB Kurang"]
        ):
            masalah_list.append("Underweight (Berat Badan Kurang)")
            badge_list.append(status_bbu)
        if any(
            x in status_lku
            for x in ["Mikrosefali", "Mikrosfali", "Makrosefali"]
        ):
            masalah_list.append(status_lku)
            badge_list.append(status_lku)

        badge_text = badge_list[0] if masalah_list else "Normal"

        if badge_text == "Normal" or "Tall" in badge_text or "Tinggi" in badge_text:
            tingkat_risiko = "Rendah"
        elif any(
            x in badge_text
            for x in [
                "Underweight",
                "Kurang",
                "Mikrosefali",
                "Mikrosfali",
                "Makrosefali",
                "Overweight",
                "Risiko Gizi Lebih",
                "Obesitas",
                "Risk",
            ]
        ):
            tingkat_risiko = "Sedang"
        else:
            tingkat_risiko = "Tinggi"

        self.terapkan_warna_badge(self.lbl_badge_risk, tingkat_risiko)

        for w in self.saran_container.winfo_children():
            w.destroy()

        saran_items = []
        if tingkat_risiko == "Tinggi":
            saran_items.append(
                "🔴  Pemantauan intensif, konsultasi dokter anak,"
                " dan rujukan segera ke fasilita kesehatan."
            )
        elif tingkat_risiko == "Sedang":
            saran_items.append(
                "🟡 Pemantauan berkala dan konsultasi ke dokter anak"
            )
        else:
            saran_items.append(
                "🟢 Pertahankan pola hidup sehat dan"
                " pemantauan rutin."
            )

        if any(x in status_bbu for x in ["Underweight", "Kurang"]):
            saran_items.append(
                "⚖️ Konsultasikan segera ke dokter spesialis anak atau ahli gizi\n"
                " di faskes untuk evaluasi target kenaikan berat badan."
            )
        elif (
            "Overweight" in status_bbu
            or "Risiko Gizi Lebih" in status_bbu
            or "Obesitas" in status_bbu
        ):
            saran_items.append(
                "⚖️ Konsultasikan ke tenaga kesehatan/dokter anak untuk evaluasi\n"
                " pola asupan kalori dan pemantauan status gizi berlebih."
            )

        if any(x in status_tbu for x in ["Stunted", "Stunting", "Pendek"]):
            saran_items.append(
                "📐 Rujuk dan konsultasikan ke dokter spesialis anak/Puskesmas\n"
                " guna penanganan serta tata laksana stunting secara komprehensif."
            )
            saran_items.append(
                "📐 Lakukan pemeriksaan berkala bersama tenaga kesehatan di faskes\n"
                " untuk intervensi nutrisi dan stimulasi pertumbuhan tinggi badan."
            )

        if any(x in status_bbtb for x in ["Wasted", "Wasting", "Kurus", "Buruk"]):
            saran_items.append(
                "🧬 Segera periksakan ke dokter anak atau fasilitas kesehatan terdekat\n"
                " untuk mendapatkan program terapi gizi/PMT pemulihan."
            )
        elif any(
            x in status_bbtb for x in ["Risiko Gizi Lebih", "Obesitas", "Overweight"]
        ):
            saran_items.append(
                "🧬 Konsultasikan manajemen berat badan anak\n"
                " dengan dokter spesialis anak atau nutrisionis."
            )

        if any(
            x in status_lku for x in ["Mikrosefali", "Mikrosfali", "Makrosefali"]
        ):
            saran_items.append(
                "🧠 Segera lakukan konsultasi dan rujukan ke dokter spesialis anak\n"
                " untuk pemeriksaan perkembangan otak dan saraf secara menyeluruh."
            )

        for s in saran_items:
            item_row = ctk.CTkFrame(self.saran_container, fg_color="transparent")
            item_row.pack(anchor="w", fill="x", pady=2)
            txt_saran = ctk.CTkLabel(
                item_row,
                text=s,
                font=("Inter", 11),
                text_color="#14532D",
                justify="left",
                anchor="w",
            )
            txt_saran.pack(side="left", fill="x", expand=True, anchor="w")

        self.draw_graphs(data)

    def bersihkan_tampilan_kosong(self):
        self.lbl_nama_header.configure(text="-")
        self.lbl_gender_tag.configure(
            text="-", text_color="#475569", fg_color="#F1F5F9"
        )
        self.profile_avatar.configure(text="👶", fg_color="#F1F5F9")

        for lbl_attr in [
            "lbl_usia",
            "lbl_bb",
            "lbl_tb",
            "lbl_lk",
            "lbl_bbl",
            "lbl_asi",
            "lbl_imunisasi",
            "lbl_gizi",
        ]:
            if hasattr(self, lbl_attr):
                getattr(self, lbl_attr).configure(text="-")

        for k, widgets in self.table_rows.items():
            widgets["z"].configure(text="-")
            widgets["k"].configure(
                text="-", fg_color="#F1F5F9", text_color="#475569"
            )
            widgets["i"].configure(text="-")

        self.lbl_badge_risk.configure(
            text="-", fg_color="#F1F5F9", text_color="#475569"
        )

        for w in self.saran_container.winfo_children():
            w.destroy()
        for w in self.fig_container.winfo_children():
            w.destroy()

    def terapkan_warna_badge(self, widget_badge, teks_status):
        status_clean = teks_status.lower()
        if any(
            keyword in status_clean
            for keyword in ["tinggi", "wasting", "stunting", "buruk", "kurang"]
        ):
            bg_color = "#FFE4E6"
            text_color = "#9F1239"
        elif any(
            keyword in status_clean
            for keyword in [
                "sedang",
                "underweight",
                "mikrosfali",
                "makrosfali",
                "mikrosefali",
            ]
        ):
            bg_color = "#FEF3C7"
            text_color = "#92400E"
        else:
            bg_color = "#DCFCE7"
            text_color = "#166534"
        widget_badge.configure(
            text=teks_status, fg_color=bg_color, text_color=text_color
        )

    def draw_graphs(self, data):
        for w in self.fig_container.winfo_children():
            w.destroy()

        if not data:
            return

        import matplotlib

        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from scipy.interpolate import pchip_interpolate

        # 1. Parsing Data Pasien
        gender_raw = str(data.get("gender", "")).strip().upper()
        is_male = ("LAKI" in gender_raw) or (gender_raw == "L") or ("MALE" in gender_raw)

        def parse_number(val, is_int=False):
            try:
                s = str(val).strip().replace(",", ".")
                clean_str = s.split()[0] if " " in s else s
                return int(float(clean_str)) if is_int else float(clean_str)
            except Exception:
                return 0.0

        usia_val = parse_number(data.get("usia", "0"), is_int=True)
        berat_aktual = parse_number(data.get("berat_badan", "0"))
        tinggi_aktual = parse_number(data.get("tinggi_badan", "0"))
        lk_aktual = parse_number(data.get("lingkar_kepala", "0"))

        # 2. DATASET LENGKAP WHO
        m_pts = np.array(
            [0, 2, 4, 6, 9, 12, 18, 24, 30, 36, 42, 48, 54, 60], dtype=float
        )

        bbu_boys = {
            "-3": [2.1, 3.8, 4.9, 5.7, 6.7, 7.5, 8.6, 9.5, 10.4, 11.2, 12.0, 12.7, 13.4, 14.1],
            "-2": [2.5, 4.3, 5.6, 6.4, 7.5, 8.4, 9.6, 10.6, 11.5, 12.4, 13.3, 14.1, 14.9, 15.7],
            "-1": [2.9, 4.9, 6.2, 7.1, 8.3, 9.3, 10.6, 11.7, 12.7, 13.7, 14.7, 15.6, 16.5, 17.5],
            "0":  [3.3, 5.6, 7.0, 7.9, 9.2, 10.2, 11.7, 12.9, 14.0, 15.1, 16.2, 17.2, 18.2, 19.2],
            "+1": [3.9, 6.3, 7.8, 8.8, 10.2, 11.3, 12.9, 14.3, 15.5, 16.7, 17.9, 19.1, 20.2, 21.4],
            "+2": [4.4, 7.1, 8.7, 9.8, 11.3, 12.5, 14.3, 15.9, 17.3, 18.7, 20.0, 21.4, 22.7, 24.1],
            "+3": [5.0, 8.0, 9.7, 10.9, 12.6, 13.9, 15.9, 17.7, 19.3, 20.9, 22.4, 23.9, 25.5, 27.1],
        }
        tbu_boys = {
            "-3": [44.2, 52.4, 57.8, 61.2, 65.2, 68.6, 74.0, 78.0, 82.2, 86.0, 89.6, 93.0, 96.2, 99.1],
            "-2": [46.1, 54.4, 59.8, 63.3, 67.5, 71.0, 76.5, 80.7, 85.1, 89.1, 92.8, 96.3, 99.6, 102.7],
            "-1": [48.0, 56.4, 61.8, 65.5, 69.7, 73.4, 79.1, 83.5, 88.0, 92.1, 96.0, 99.6, 103.0, 106.3],
            "0":  [49.9, 58.4, 63.9, 67.6, 72.0, 75.7, 81.6, 86.3, 90.9, 95.2, 99.2, 102.9, 106.4, 109.8],
            "+1": [51.8, 60.4, 65.9, 69.8, 74.2, 78.1, 84.2, 89.1, 93.8, 98.2, 102.4, 106.2, 109.8, 113.3],
            "+2": [53.7, 62.4, 68.0, 71.9, 76.5, 80.5, 86.7, 91.9, 96.7, 101.3, 105.6, 109.5, 113.2, 116.8],
            "+3": [55.6, 64.4, 70.1, 74.0, 78.7, 82.9, 89.3, 94.7, 99.7, 104.3, 108.8, 112.8, 116.6, 120.3],
        }
        lku_boys = {
            "-3": [31.9, 36.8, 39.5, 41.0, 42.6, 43.6, 45.0, 45.9, 46.6, 47.2, 47.7, 48.1, 48.4, 48.7],
            "-2": [33.1, 38.0, 40.7, 42.2, 43.8, 44.8, 46.2, 47.2, 47.9, 48.5, 49.0, 49.4, 49.8, 50.1],
            "-1": [34.3, 39.2, 41.9, 43.4, 45.0, 46.0, 47.4, 48.4, 49.1, 49.8, 50.3, 50.7, 51.1, 51.5],
            "0":  [35.5, 40.5, 43.1, 44.6, 46.2, 47.2, 48.6, 49.6, 50.4, 51.0, 51.6, 52.0, 52.5, 52.8],
            "+1": [36.7, 41.7, 44.3, 45.8, 47.4, 48.4, 49.8, 50.8, 51.6, 52.3, 52.8, 53.3, 53.8, 54.2],
            "+2": [37.9, 42.9, 45.5, 47.0, 48.6, 49.6, 51.0, 52.0, 52.8, 53.5, 54.1, 54.6, 55.1, 55.5],
            "+3": [39.1, 44.1, 46.7, 48.2, 49.8, 50.8, 52.2, 53.2, 54.1, 54.8, 55.4, 55.9, 56.4, 56.9],
        }

        bbu_girls = {
            "-3": [2.0, 3.4, 4.4, 5.1, 6.0, 6.7, 7.7, 8.5, 9.3, 10.1, 10.8, 11.5, 12.2, 12.8],
            "-2": [2.4, 3.9, 5.0, 5.7, 6.7, 7.5, 8.6, 9.5, 10.4, 11.2, 12.0, 12.8, 13.5, 14.2],
            "-1": [2.8, 4.4, 5.6, 6.4, 7.5, 8.4, 9.6, 10.6, 11.6, 12.5, 13.4, 14.2, 15.0, 15.8],
            "0":  [3.2, 5.1, 6.4, 7.3, 8.5, 9.5, 10.8, 11.9, 12.9, 13.9, 14.9, 15.8, 16.7, 17.6],
            "+1": [3.7, 5.8, 7.2, 8.2, 9.6, 10.7, 12.2, 13.4, 14.5, 15.6, 16.6, 17.7, 18.7, 19.7],
            "+2": [4.2, 6.5, 8.1, 9.3, 10.8, 12.0, 13.7, 15.1, 16.3, 17.5, 18.7, 19.8, 21.0, 22.1],
            "+3": [4.8, 7.4, 9.1, 10.4, 12.1, 13.4, 15.4, 16.9, 18.3, 19.7, 21.0, 22.3, 23.6, 24.9],
        }
        tbu_girls = {
            "-3": [43.6, 51.0, 56.2, 59.6, 63.5, 66.8, 72.3, 76.4, 80.6, 84.4, 88.0, 91.4, 94.6, 97.6],
            "-2": [45.4, 53.0, 58.2, 61.7, 65.7, 69.2, 74.8, 79.1, 83.4, 87.4, 91.1, 94.6, 97.9, 101.0],
            "-1": [47.3, 55.0, 60.2, 63.8, 68.0, 71.6, 77.4, 81.8, 86.2, 90.3, 94.2, 97.8, 101.2, 104.4],
            "0":  [49.1, 57.1, 62.3, 66.0, 70.3, 74.0, 80.0, 84.6, 89.1, 93.3, 97.3, 101.0, 104.5, 107.8],
            "+1": [51.0, 59.1, 64.4, 68.2, 72.6, 76.4, 82.6, 87.4, 92.0, 96.3, 100.4, 104.2, 107.8, 111.2],
            "+2": [52.9, 61.1, 66.5, 70.4, 74.9, 78.9, 85.2, 90.2, 94.9, 99.3, 103.5, 107.4, 111.1, 114.6],
            "+3": [54.7, 63.2, 68.6, 72.6, 77.2, 81.4, 87.8, 93.0, 97.8, 102.3, 106.6, 110.6, 114.4, 118.0],
        }
        lku_girls = {
            "-3": [31.2, 35.8, 38.4, 39.8, 41.3, 42.3, 43.7, 44.7, 45.4, 46.0, 46.5, 46.9, 47.3, 47.6],
            "-2": [32.4, 37.0, 39.6, 41.0, 42.5, 43.5, 44.9, 45.9, 46.6, 47.3, 47.8, 48.2, 48.6, 49.0],
            "-1": [33.6, 38.2, 40.8, 42.2, 43.7, 44.7, 46.1, 47.1, 47.9, 48.5, 49.1, 49.5, 49.9, 50.3],
            "0":  [34.8, 39.4, 42.0, 43.4, 44.9, 45.9, 47.3, 48.3, 49.1, 49.7, 50.3, 50.7, 51.2, 51.5],
            "+1": [36.0, 40.6, 43.2, 44.6, 46.1, 47.1, 48.5, 49.5, 50.3, 51.0, 51.5, 52.0, 52.5, 52.8],
            "+2": [37.2, 41.8, 44.4, 45.8, 47.3, 48.3, 49.7, 50.7, 51.5, 52.2, 52.8, 53.3, 53.8, 54.1],
            "+3": [38.4, 43.0, 45.6, 47.0, 48.5, 49.5, 50.9, 51.9, 52.7, 53.4, 54.0, 54.5, 55.0, 55.4],
        }

        wfl_len = np.array(
            [45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110],
            dtype=float,
        )
        wfl_data = {
            "-3": [1.9, 2.4, 3.2, 4.2, 5.3, 6.3, 7.3, 8.3, 9.4, 10.5, 11.6, 12.7, 13.8, 14.9],
            "-2": [2.1, 2.7, 3.6, 4.6, 5.8, 6.9, 8.0, 9.0, 10.1, 11.3, 12.4, 13.6, 14.8, 16.0],
            "-1": [2.3, 3.0, 4.0, 5.1, 6.3, 7.5, 8.6, 9.7, 10.9, 12.1, 13.3, 14.6, 15.9, 17.2],
            "0":  [2.5, 3.3, 4.4, 5.6, 6.9, 8.1, 9.3, 10.5, 11.7, 13.0, 14.3, 15.6, 17.0, 18.5],
            "+1": [2.8, 3.7, 4.9, 6.1, 7.5, 8.8, 10.1, 11.4, 12.7, 14.0, 15.4, 16.8, 18.3, 19.9],
            "+2": [3.1, 4.1, 5.4, 6.7, 8.2, 9.6, 11.0, 12.3, 13.7, 15.1, 16.6, 18.1, 19.7, 21.5],
            "+3": [3.4, 4.5, 5.9, 7.4, 9.0, 10.5, 12.0, 13.4, 14.9, 16.4, 18.0, 19.6, 21.3, 23.3],
        }

        wfh_len = np.array(
            [65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120], dtype=float
        )
        wfh_data = {
            "-3": [5.6, 6.6, 7.6, 8.6, 9.6, 10.6, 11.6, 12.7, 13.8, 15.0, 16.2, 17.5],
            "-2": [6.1, 7.2, 8.2, 9.3, 10.4, 11.4, 12.5, 13.6, 14.8, 16.0, 17.3, 18.7],
            "-1": [6.6, 7.8, 8.9, 10.0, 11.1, 12.3, 13.4, 14.6, 15.8, 17.1, 18.5, 20.0],
            "0":  [7.2, 8.4, 9.6, 10.8, 12.0, 13.2, 14.4, 15.7, 17.0, 18.4, 19.8, 21.4],
            "+1": [7.9, 9.2, 10.5, 11.7, 13.0, 14.3, 15.6, 16.9, 18.3, 19.8, 21.3, 23.0],
            "+2": [8.7, 10.0, 11.4, 12.7, 14.1, 15.4, 16.8, 18.3, 19.8, 21.3, 23.0, 24.8],
            "+3": [9.5, 11.0, 12.4, 13.8, 15.3, 16.7, 18.2, 19.7, 21.3, 23.0, 24.8, 26.8],
        }

        ds_bbu = bbu_boys if is_male else bbu_girls
        ds_tbu = tbu_boys if is_male else tbu_girls
        ds_lku = lku_boys if is_male else lku_girls

        # 3. Inisialisasi Canvas
        plt.close("all")
        fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), dpi=100)
        fig.patch.set_facecolor("white")

        titles = [
            "Weight-for-length" if usia_val < 24 else "Weight-for-height",
            "Weight-for-age",
            "HC-for-age",
            "Length/height-for-age",
        ]
        z_keys = ["BB/TB", "BB/U", "LK/U", "TB/U"]

        c_black = "#263238"
        c_red = "#E53935"
        c_gold = "#D97706"
        c_green = "#16A34A"

        for i, ax in enumerate(axes.flat):
            key = z_keys[i]
            z_val = parse_number(data.get("zscore", {}).get(key, 0.0))

            if key == "BB/U":
                xlabel, ylabel = "Usia (bulan)", "Berat Badan (kg)"
                y_aktual, plot_x = berat_aktual, usia_val
                x_ticks = [0, 10, 24, 30, 40, 50, 60]
                xlim_range = (0, 60)
                ylim_range = (2, 30)

                x_dense = np.linspace(0, 60, 200)
                curves = {
                    sd: pchip_interpolate(m_pts, ds_bbu[sd], x_dense)
                    for sd in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
                }

            elif key == "TB/U":
                xlabel, ylabel = "Usia (bulan)", "Tinggi Badan (cm)"
                y_aktual, plot_x = tinggi_aktual, usia_val
                x_ticks = [0, 12, 24, 36, 48, 60]
                xlim_range = (0, 60)
                ylim_range = (40, 130)

                x_dense = np.linspace(0, 60, 200)
                curves = {
                    sd: pchip_interpolate(m_pts, ds_tbu[sd], x_dense)
                    for sd in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
                }

            elif key == "LK/U":
                xlabel, ylabel = "Usia (bulan)", "Lingkar Kepala (cm)"
                y_aktual, plot_x = lk_aktual, usia_val
                x_ticks = [0, 10, 20, 30, 40, 50, 60]
                xlim_range = (0, 60)
                ylim_range = (28, 60)

                x_dense = np.linspace(0, 60, 200)
                curves = {
                    sd: pchip_interpolate(m_pts, ds_lku[sd], x_dense)
                    for sd in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
                }

            else:  # BB/TB
                y_aktual, plot_x = berat_aktual, tinggi_aktual
                ylabel = "Weight (kg)" if usia_val < 24 else "Berat Badan (kg)"

                if usia_val < 24:
                    xlabel = "Length (cm)"
                    x_ticks = [50, 60, 70, 80, 90, 100, 110]
                    xlim_range = (45, 110)
                    ylim_range = (0, 26)
                    x_dense = np.linspace(45, 110, 200)
                    curves = {
                        sd: pchip_interpolate(wfl_len, wfl_data[sd], x_dense)
                        for sd in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
                    }
                else:
                    xlabel = "Tinggi Badan (cm)"
                    x_ticks = [65, 75, 85, 95, 105, 115, 120]
                    xlim_range = (65, 120)
                    ylim_range = (4, 32)
                    x_dense = np.linspace(65, 120, 200)
                    curves = {
                        sd: pchip_interpolate(wfh_len, wfh_data[sd], x_dense)
                        for sd in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
                    }

            # 4. Plot Garis Kurva
            ax.plot(x_dense, curves["+3"], color=c_black, linewidth=1.1, zorder=3)
            ax.plot(x_dense, curves["+2"], color=c_red, linewidth=1.0, zorder=3)
            ax.plot(x_dense, curves["+1"], color=c_gold, linewidth=1.0, zorder=3)
            ax.plot(x_dense, curves["0"], color=c_green, linewidth=1.3, zorder=4)
            ax.plot(x_dense, curves["-1"], color=c_gold, linewidth=1.0, zorder=3)
            ax.plot(x_dense, curves["-2"], color=c_red, linewidth=1.0, zorder=3)
            ax.plot(x_dense, curves["-3"], color=c_black, linewidth=1.1, zorder=3)

            # Garis Bantu Pasien
            ax.axvline(
                x=plot_x,
                color="#E11D48",
                linestyle="--",
                linewidth=0.85,
                alpha=0.85,
                zorder=5,
            )
            ax.axhline(
                y=y_aktual,
                color="#E11D48",
                linestyle="--",
                linewidth=0.85,
                alpha=0.85,
                zorder=5,
            )

            # Titik Aktual Pasien
            ax.plot(
                plot_x,
                y_aktual,
                marker="o",
                markerfacecolor="white",
                markeredgecolor="#2563EB",
                markersize=5.8,
                markeredgewidth=1.8,
                zorder=20,
            )

            # Badge Box Nilai Z-Score
            ax.text(
                0.03,
                0.92,
                f"z-score: {z_val:+.2f}",
                transform=ax.transAxes,
                fontsize=6.8,
                bbox=dict(
                    boxstyle="square,pad=0.25",
                    fc="white",
                    ec="#CBD5E1",
                    lw=0.5,
                    alpha=0.9,
                ),
                va="top",
                ha="left",
                zorder=25,
            )

            ax.set_title(
                titles[i], fontsize=9.2, pad=4, fontweight="bold", color="#0F172A"
            )
            ax.set_xlabel(xlabel, fontsize=7.2, color="#475569")
            ax.set_ylabel(ylabel, fontsize=7.2, color="#475569")
            ax.set_xlim(xlim_range)
            ax.set_ylim(ylim_range)
            ax.set_xticks(x_ticks)

            ax.tick_params(
                labelsize=6.8,
                colors="#0F172A",
                direction="in",
                length=3.2,
                width=0.7,
                which="both",
                pad=3,
            )
            ax.grid(True, alpha=0.18, linestyle="-", color="#E2E8F0")

            # Label SD di Sisi Kanan
            y_min, y_max = ylim_range

            def get_norm(val):
                return (val - y_min) / (y_max - y_min)

            labels_sd = [
                (get_norm(curves["+3"][-1]), "+3 SD", c_black),
                (get_norm(curves["+2"][-1]), "+2 SD", c_red),
                (get_norm(curves["+1"][-1]), "+1 SD", c_gold),
                (get_norm(curves["0"][-1]), "Median", c_green),
                (get_norm(curves["-1"][-1]), "-1 SD", c_gold),
                (get_norm(curves["-2"][-1]), "-2 SD", c_red),
                (get_norm(curves["-3"][-1]), "-3 SD", c_black),
            ]

            for y_pos_norm, text_sd, color_sd in labels_sd:
                if 0.0 <= y_pos_norm <= 1.0:
                    ax.text(
                        0.985,
                        y_pos_norm,
                        text_sd,
                        transform=ax.transAxes,
                        color=color_sd,
                        fontsize=5.6,
                        ha="right",
                        va="center",
                        fontweight="bold",
                        zorder=22,
                    )

        # 5. Layout & Render ke Tkinter Canvas
        fig.subplots_adjust(
            left=0.08, right=0.97, top=0.93, bottom=0.09, hspace=0.36, wspace=0.26
        )

        canvas = FigureCanvasTkAgg(fig, master=self.fig_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close(fig)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("SIDERIS - Modul Pemeriksaan")
    app.geometry("1300x800")
    page = PemeriksaanPage(app)
    page.pack(fill="both", expand=True)
    app.mainloop()