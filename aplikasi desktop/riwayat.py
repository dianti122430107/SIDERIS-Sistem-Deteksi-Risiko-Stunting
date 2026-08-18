import os
import random
import customtkinter as ctk
from PIL import Image

# 1. Pastikan ambil_riwayat_pemeriksaan_by_nama ikut di-import di sini
from database import (
    ambil_semua_data_sideris,
    ambil_data_sideris_by_nama,
    ambil_riwayat_pemeriksaan_by_nama,
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# DATABASE RIWAYAT
DATA_RIWAYAT_GLOBAL = []
DATA_DETAIL_GLOBAL = {}


class RiwayatPage(ctk.CTkFrame):

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.riwayat_rows = []

        # Palet Warna SIDERIS
        self.text_dark = "#0F172A"
        self.text_muted = "#64748B"
        self.table_header_bg = "#E9708D"
        self.bg_main = "#F8FAFC"

        self.configure(fg_color=self.bg_main)

        try:
            self.setup_main_content()
        except Exception as e:
            print("Error saat setup RiwayatPage:", e)

    def setup_main_content(self):
        if self.master:
            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_content = ctk.CTkFrame(
            self, fg_color=self.bg_main, corner_radius=0
        )
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)

        try:
            user_id_aktif = self.controller.current_user_id
            rows = ambil_semua_data_sideris(user_id_aktif)
            self.riwayat_rows = []
            for idx, row in enumerate(rows):
                nama = row[0]
                usia = f"{row[4]} Bulan" if row[4] is not None else "-"
                jk = row[2] or "-"
                tgl = row[3] or "-"
                risiko = row[20] or "Belum Diperiksa"
                self.riwayat_rows.append(
                    (idx + 1, nama, usia, jk, tgl, risiko)
                )
        except Exception as e:
            print("Gagal memuat riwayat dari database:", e)

        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self.main_content,
            text="Riwayat Pemeriksaan",
            font=("Arial", 22, "bold"),
            text_color=self.text_dark,
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 15), padx=5)

        card_tabel = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#F1F5F9",
        )
        card_tabel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        card_tabel.grid_columnconfigure(0, weight=1)
        card_tabel.grid_rowconfigure(0, weight=0)
        card_tabel.grid_rowconfigure(1, weight=1)
        card_tabel.grid_rowconfigure(2, weight=0)

        header_container = ctk.CTkFrame(
            card_tabel,
            fg_color=self.table_header_bg,
            corner_radius=8,
            height=45,
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_container.grid_propagate(False)
        header_container.grid_rowconfigure(0, weight=1)

        header_container.grid_columnconfigure(0, weight=8, uniform="table_cols")
        header_container.grid_columnconfigure(1, weight=22, uniform="table_cols")
        header_container.grid_columnconfigure(2, weight=13, uniform="table_cols")
        header_container.grid_columnconfigure(3, weight=18, uniform="table_cols")
        header_container.grid_columnconfigure(4, weight=18, uniform="table_cols")
        header_container.grid_columnconfigure(5, weight=18, uniform="table_cols")
        header_container.grid_columnconfigure(6, weight=18, uniform="table_cols")

        headers_text = [
            "No",
            "Nama",
            "Usia",
            "Jenis Kelamin",
            "Terakhir Diperiksa",
            "Status Risiko",
            "Aksi",
        ]
        for i, text in enumerate(headers_text):
            stk = "w" if i in [1, 3, 4] else ""
            px = 15 if i in [1, 3, 4] else 0

            lbl = ctk.CTkLabel(
                header_container,
                text=text,
                font=("Helvetica", 12, "bold"),
                text_color="white",
            )
            lbl.grid(row=0, column=i, sticky=stk, padx=px, pady=10)

        self.rows_scroll = ctk.CTkScrollableFrame(
            card_tabel, fg_color="transparent", corner_radius=0
        )
        self.rows_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        self.rows_scroll.grid_columnconfigure(0, weight=8, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(1, weight=22, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(2, weight=13, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(3, weight=18, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(4, weight=18, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(5, weight=18, uniform="table_cols")
        self.rows_scroll.grid_columnconfigure(6, weight=18, uniform="table_cols")

        warna_risiko = {
            "Tinggi": {"bg": "#FEE2E2", "text": "#DC2626"},
            "Sedang": {"bg": "#FFEDD5", "text": "#EA580C"},
            "Rendah": {"bg": "#DCFCE7", "text": "#16A34A"},
        }

        if not self.riwayat_rows:
            lbl_empty = ctk.CTkLabel(
                self.rows_scroll,
                text="✨ Belum ada data pemeriksaan yang diinput.",
                font=("Helvetica", 13),
                text_color=self.text_muted,
            )
            lbl_empty.pack(pady=40, expand=True)
        else:
            for r_idx, (no, nama, usia, jk, tgl, risiko) in enumerate(
                self.riwayat_rows
            ):
                row_pos = r_idx * 2

                ctk.CTkLabel(
                    self.rows_scroll,
                    text=str(no),
                    font=("Arial", 12),
                    text_color=self.text_muted,
                ).grid(row=row_pos, column=0, pady=12, sticky="")

                profile_box = ctk.CTkFrame(
                    self.rows_scroll, fg_color="transparent"
                )
                profile_box.grid(
                    row=row_pos, column=1, sticky="w", padx=15, pady=12
                )
                avatar_emoji = "👧" if jk == "Perempuan" else "👦"
                avatar_bg = "#FCE7F3" if jk == "Perempuan" else "#E0F2FE"
                ctk.CTkLabel(
                    profile_box,
                    text=avatar_emoji,
                    font=("Arial", 13),
                    fg_color=avatar_bg,
                    width=28,
                    height=28,
                    corner_radius=14,
                ).pack(side="left", padx=(0, 10))
                ctk.CTkLabel(
                    profile_box,
                    text=nama,
                    font=("Helvetica", 12, "bold"),
                    text_color=self.text_dark,
                ).pack(side="left")

                ctk.CTkLabel(
                    self.rows_scroll,
                    text=usia,
                    font=("Arial", 12),
                    text_color="#334155",
                ).grid(row=row_pos, column=2, pady=12, sticky="")

                jk_box = ctk.CTkFrame(self.rows_scroll, fg_color="transparent")
                jk_box.grid(row=row_pos, column=3, sticky="w", padx=15, pady=12)
                simbol_jk = "♀" if jk == "Perempuan" else "♂"
                warna_jk = "#DB2777" if jk == "Perempuan" else "#2563EB"
                ctk.CTkLabel(
                    jk_box,
                    text=simbol_jk,
                    font=("Arial", 14, "bold"),
                    text_color=warna_jk,
                ).pack(side="left", padx=(0, 6))
                ctk.CTkLabel(
                    jk_box,
                    text=jk,
                    font=("Arial", 12),
                    text_color="#334155",
                ).pack(side="left")

                tgl_box = ctk.CTkFrame(
                    self.rows_scroll, fg_color="transparent"
                )
                tgl_box.grid(
                    row=row_pos, column=4, sticky="w", padx=15, pady=12
                )
                ctk.CTkLabel(tgl_box, text="📅", font=("Arial", 11)).pack(
                    side="left", padx=(0, 6)
                )
                ctk.CTkLabel(
                    tgl_box,
                    text=tgl,
                    font=("Arial", 12),
                    text_color="#334155",
                ).pack(side="left")

                props = warna_risiko.get(
                    risiko, {"bg": "#E2E8F0", "text": "#64748B"}
                )
                badge_risk = ctk.CTkLabel(
                    self.rows_scroll,
                    text=risiko,
                    font=("Helvetica", 11, "bold"),
                    fg_color=props["bg"],
                    text_color=props["text"],
                    corner_radius=6,
                    width=105,
                    height=25,
                )
                badge_risk.grid(row=row_pos, column=5, pady=12, sticky="")

                action_box = ctk.CTkFrame(
                    self.rows_scroll, fg_color="transparent"
                )
                action_box.grid(row=row_pos, column=6, pady=12, sticky="")
                btn_lihat = ctk.CTkButton(
                    action_box,
                    text="Lihat Detail",
                    font=("Helvetica", 11, "bold"),
                    width=85,
                    height=26,
                    fg_color="white",
                    text_color="#E9708D",
                    border_width=1,
                    border_color="#F9A8D4",
                    hover_color="#FDF2F8",
                    corner_radius=6,
                    command=lambda n=nama, j=jk: self.show_detail(n, j),
                )
                btn_lihat.pack(side="left", padx=(0, 8))

                line_separator = ctk.CTkFrame(
                    self.rows_scroll, fg_color="#F1F5F9", height=1
                )
                line_separator.grid(
                    row=row_pos + 1, column=0, columnspan=7, sticky="ew"
                )

        note_banner = ctk.CTkFrame(
            self.main_content,
            fg_color="#FFF1F2",
            corner_radius=10,
            border_width=1,
            border_color="#FFE4E6",
        )
        note_banner.grid(row=2, column=0, sticky="ew", padx=5, pady=(10, 5))

        lbl_info_icon = ctk.CTkLabel(
            note_banner,
            text="ⓘ",
            font=("Arial", 13, "bold"),
            fg_color="#FDA4AF",
            text_color="#9F1239",
            width=22,
            height=22,
            corner_radius=11,
        )
        lbl_info_icon.pack(side="left", padx=(15, 10), pady=12)

        text_note_box = ctk.CTkFrame(note_banner, fg_color="transparent")
        text_note_box.pack(side="left", fill="both", expand=True, pady=10)
        ctk.CTkLabel(
            text_note_box,
            text="Catatan",
            font=("Helvetica", 12, "bold"),
            text_color="#9F1239",
        ).pack(anchor="w", pady=0)
        ctk.CTkLabel(
            text_note_box,
            text=(
                'Klik tombol "Lihat Detail" untuk melihat riwayat lengkap dan'
                " hasil pemeriksaan balita."
            ),
            font=("Helvetica", 11),
            text_color="#BE123C",
        ).pack(anchor="w", pady=0)

    def show_detail(self, nama, jenis_kelamin):
        # 1. SETUP WINDOW UTAMA POP-UP
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(f"Detail Riwayat - {nama}")
        detail_window.geometry("1200x700")
        detail_window.configure(fg_color="#F8FAFC")

        detail_window.withdraw()
        detail_window.lift()
        detail_window.attributes("-topmost", True)
        detail_window.deiconify()

        detail_window.after(
            100,
            lambda: [
                detail_window.attributes("-topmost", False),
                detail_window.focus_force(),
            ],
        )

        main_scroll = ctk.CTkScrollableFrame(
            detail_window, fg_color="transparent"
        )
        main_scroll.pack(fill="both", expand=True, padx=25, pady=20)

        # 2. AMBIL SEMUA RIWAYAT PEMERIKSAAN DARI DATABASE
        data_pemeriksaan = []
        try:
            user_id_aktif = self.controller.current_user_id
            rows = ambil_riwayat_pemeriksaan_by_nama(user_id_aktif, nama)

            for idx, r in enumerate(rows):
                tgl_pemeriksaan = (
                    r.get("tanggal_pemeriksaan")
                    or r.get("tanggal_periksa")
                    or "-"
                )
                usia_text = (
                    f"{r.get('usia_bulan', '-') or '-'} Bulan"
                    if r.get("usia_bulan") is not None
                    else "-"
                )
                bb_text = (
                    str(r.get("berat_badan", "0"))
                    if r.get("berat_badan") is not None
                    else "0"
                )
                tb_text = (
                    str(r.get("tinggi_badan", "0"))
                    if r.get("tinggi_badan") is not None
                    else "0"
                )
                lk_text = (
                    str(r.get("lingkar_kepala", "0"))
                    if r.get("lingkar_kepala") is not None
                    else "0"
                )
                bbl_text = (
                    str(r.get("berat_badan_lahir", "-"))
                    if r.get("berat_badan_lahir") is not None
                    else "-"
                )
                gizi_text = r.get("asupan_gizi") or "-"
                asi_text = r.get("asi") or "-"
                imun_text = r.get("imunisasi") or "-"
                hasil_text = (
                    r.get("tingkat_risiko") or r.get("bb_u_status") or "-"
                )

                ket = (
                    "Pemeriksaan terakhir"
                    if idx == 0
                    else f"Pemeriksaan ke-{len(rows) - idx}"
                )

                data_pemeriksaan.append(
                    {
                        "tgl": tgl_pemeriksaan,
                        "ket": ket,
                        "usia": usia_text,
                        "bb": bb_text,
                        "bb_tren": "",
                        "tb": tb_text,
                        "tb_tren": "",
                        "lk": lk_text,
                        "bbl": bbl_text,
                        "gizi": gizi_text,
                        "asi": asi_text,
                        "imun": imun_text,
                        "hasil": hasil_text,
                        "tanggal_lahir": r.get("tanggal_lahir") or "-",
                        "jenis_kelamin": r.get("jenis_kelamin")
                        or jenis_kelamin,
                    }
                )
        except Exception as database_error:
            print("Gagal mengambil data detail dari database:", database_error)

        total_periksa = f"{len(data_pemeriksaan)} kali"
        teks_kenaikan_bb = "+0 kg"
        teks_kenaikan_tb = "+0 cm"

        if len(data_pemeriksaan) >= 2:
            try:
                # Perhitungan BB
                bb_s, bb_l = float(data_pemeriksaan[0]["bb"]), float(
                    data_pemeriksaan[1]["bb"]
                )
                selisih_bb = bb_s - bb_l
                teks_kenaikan_bb = (
                    f"+{selisih_bb:.1f} kg ↑"
                    if selisih_bb >= 0
                    else f"{selisih_bb:.1f} kg ↓"
                )
                data_pemeriksaan[0]["bb_tren"] = teks_kenaikan_bb

                # Perhitungan TB
                tb_s, tb_l = float(data_pemeriksaan[0]["tb"]), float(
                    data_pemeriksaan[1]["tb"]
                )
                selisih_tb = tb_s - tb_l
                teks_kenaikan_tb = (
                    f"+{selisih_tb:.1f} cm ↑"
                    if selisih_tb >= 0
                    else f"{selisih_tb:.1f} cm ↓"
                )
                data_pemeriksaan[0]["tb_tren"] = (
                    teks_kenaikan_tb
                )
            except Exception as e:
                print("Gagal hitung tren:", e)

        top_bar = ctk.CTkFrame(main_scroll, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))
        top_bar.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_main_title = ctk.CTkLabel(
            title_box,
            text="Riwayat Pemeriksaan",
            font=("Helvetica", 24, "bold"),
            text_color="#0F172A",
        )
        lbl_main_title.pack(anchor="w")
        lbl_sub_title = ctk.CTkLabel(
            title_box,
            text=f"Berikut adalah riwayat pemeriksaan dan pertumbuhan {nama}.",
            font=("Helvetica", 12),
            text_color="#64748B",
        )
        lbl_sub_title.pack(anchor="w", pady=(2, 0))

        cards_container = ctk.CTkFrame(top_bar, fg_color="transparent")
        cards_container.grid(row=0, column=1, sticky="e")

        def buat_card_indikator(
            parent,
            icon,
            title,
            value,
            subtext,
            icon_bg,
            default_text_color,
        ):
            card = ctk.CTkFrame(
                parent,
                fg_color="white",
                corner_radius=12,
                border_width=1,
                border_color="#F1F5F9",
                width=175,
                height=85,
            )
            card.pack(side="left", padx=6)
            card.grid_propagate(False)

            card.grid_columnconfigure(0, weight=0, minsize=45)
            card.grid_columnconfigure(1, weight=1)
            card.grid_rowconfigure(0, weight=1)

            lbl_icon = ctk.CTkLabel(
                card,
                text=icon,
                font=("Arial", 16),
                fg_color=icon_bg,
                width=32,
                height=32,
                corner_radius=8,
            )
            lbl_icon.grid(row=0, column=0, padx=(12, 5), sticky="w")

            txt_frame = ctk.CTkFrame(card, fg_color="transparent")
            txt_frame.grid(row=0, column=1, sticky="w", padx=(4, 10))

            lbl_title = ctk.CTkLabel(
                txt_frame,
                text=title,
                font=("Helvetica", 11),
                text_color="#64748B",
                anchor="w",
            )
            lbl_title.grid(row=0, column=0, sticky="w", pady=0)

            v_color = (
                "#10B981"
                if "+" in value or "kali" in value
                else default_text_color
            )

            lbl_val = ctk.CTkLabel(
                txt_frame,
                text=value,
                font=("Helvetica", 18, "bold"),
                text_color=v_color,
                anchor="w",
            )
            lbl_val.grid(row=1, column=0, sticky="w", pady=0)

            lbl_sub = ctk.CTkLabel(
                txt_frame,
                text=subtext,
                font=("Helvetica", 10),
                text_color="#64748B",
                anchor="w",
            )
            lbl_sub.grid(row=2, column=0, sticky="w", pady=0)

        buat_card_indikator(
            cards_container,
            "📅",
            "Total Pemeriksaan",
            total_periksa,
            "Pemeriksaan rutin",
            "#EFF6FF",
            "#0F172A",
        )
        buat_card_indikator(
            cards_container,
            "📈",
            "Kenaikan BB",
            teks_kenaikan_bb,
            "Dari bulan lalu",
            "#F0FDF4",
            "#16A34A",
        )
        buat_card_indikator(
            cards_container,
            "👤",
            "Kenaikan TB",
            teks_kenaikan_tb,
            "Dari bulan lalu",
            "#FAF5FF",
            "#7C3AED",
        )

        # 3. PROFILE BAR
        profile_card = ctk.CTkFrame(
            main_scroll,
            fg_color="white",
            corner_radius=14,
            border_width=1,
            border_color="#F1F5F9",
        )
        profile_card.pack(fill="x", pady=(0, 20))

        avatar_emoji = "👧" if jenis_kelamin == "Perempuan" else "👦"
        avatar_bg = "#FCE7F3" if jenis_kelamin == "Perempuan" else "#E0F2FE"
        lbl_avatar_large = ctk.CTkLabel(
            profile_card,
            text=avatar_emoji,
            font=("Arial", 28),
            fg_color=avatar_bg,
            width=56,
            height=56,
            corner_radius=28,
        )
        lbl_avatar_large.pack(side="left", padx=20, pady=15)

        def buat_item_bio(parent, label, value, icon):
            box = ctk.CTkFrame(parent, fg_color="transparent")
            box.pack(side="left", expand=True, fill="x", padx=10)

            lbl_ico = ctk.CTkLabel(
                box, text=icon, font=("Arial", 12), text_color="#94A3B8"
            )
            lbl_ico.pack(side="left", padx=(0, 10))

            detail_box = ctk.CTkFrame(box, fg_color="transparent")
            detail_box.pack(side="left")
            ctk.CTkLabel(
                detail_box,
                text=label,
                font=("Helvetica", 11),
                text_color="#94A3B8",
            ).pack(anchor="w")
            ctk.CTkLabel(
                detail_box,
                text=value,
                font=("Helvetica", 13, "bold"),
                text_color="#1E293B",
            ).pack(anchor="w")

        buat_item_bio(profile_card, "Nama", nama, "👤")
        buat_item_bio(
            profile_card,
            "Jenis Kelamin",
            jenis_kelamin,
            "🚺" if jenis_kelamin == "Perempuan" else "🚹",
        )
        buat_item_bio(
            profile_card,
            "Usia",
            data_pemeriksaan[0]["usia"] if data_pemeriksaan else "-",
            "⏳",
        )
        buat_item_bio(
            profile_card,
            "Tanggal Lahir",
            data_pemeriksaan[0]["tanggal_lahir"] if data_pemeriksaan else "-",
            "🎂",
        )

        # 4. TABEL RIWAYAT SEMUA PEMERIKSAAN
        table_wrapper = ctk.CTkFrame(main_scroll, fg_color="transparent")
        table_wrapper.pack(fill="x", pady=(0, 20))
        table_wrapper.grid_columnconfigure(0, weight=1)

        table_container = ctk.CTkFrame(
            table_wrapper,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#F1F5F9",
        )
        table_container.grid(row=0, column=0, sticky="ew")
        table_container.grid_rowconfigure(0, weight=0, minsize=42)

        lebar_kolom = [14, 10, 10, 10, 10, 10, 12, 12, 12, 12, 4]
        for col_idx, weight in enumerate(lebar_kolom):
            table_container.grid_columnconfigure(
                col_idx, weight=weight, uniform="detail_cols"
            )

        headers_detail = [
            "📅 Tanggal",
            "👶 Usia",
            "⚖️ BB (kg)",
            "📏 TB (cm)",
            "🧠 LK (cm)",
            "🍼 BB Lahir",
            "🥗 Asupan Gizi",
            "🍼 ASI Eksklusif",
            "💉 Imunisasi",
            "📋 Hasil",
            "",
        ]

        for i, h_text in enumerate(headers_detail):
            b_width = 1 if i < len(headers_detail) - 1 else 0
            h_cell = ctk.CTkFrame(
                table_container,
                fg_color="#E9708D",
                corner_radius=0,
                height=42,
                border_width=b_width,
                border_color="white",
            )
            h_cell.grid(row=0, column=i, sticky="ew", pady=(12, 10))
            h_cell.pack_propagate(False)

            lbl_h = ctk.CTkLabel(
                h_cell,
                text=h_text,
                font=("Helvetica", 11, "bold"),
                text_color="white",
                fg_color="transparent",
            )
            lbl_h.pack(expand=True, fill="both")

        if not data_pemeriksaan:
            lbl_no_detail = ctk.CTkLabel(
                table_container,
                text="Tidak ada riwayat detail.",
                font=("Helvetica", 12),
                text_color=self.text_muted,
            )
            lbl_no_detail.grid(row=1, column=0, columnspan=11, pady=20)
        else:
            for r_idx, row_data in enumerate(data_pemeriksaan):
                row_pos = (r_idx * 2) + 1

                table_container.grid_rowconfigure(
                    row_pos, weight=0, minsize=45
                )
                table_container.grid_rowconfigure(
                    row_pos + 1, weight=0, minsize=1
                )

                # Kolom 0: Tanggal
                tgl_frame = ctk.CTkFrame(
                    table_container, fg_color="transparent"
                )
                tgl_frame.grid(
                    row=row_pos, column=0, sticky="w", padx=15, pady=12
                )
                lbl_tgl_atas = ctk.CTkLabel(
                    tgl_frame,
                    text=row_data["tgl"],
                    font=("Helvetica", 11, "bold"),
                    text_color="#1E293B",
                )
                lbl_tgl_atas.pack(anchor="w")
                lbl_tgl_bawah = ctk.CTkLabel(
                    tgl_frame,
                    text=row_data["ket"],
                    font=("Helvetica", 10),
                    text_color="#EF4444" if r_idx == 0 else "#94A3B8",
                )
                lbl_tgl_bawah.pack(anchor="w")

                # Kolom 1: Usia
                ctk.CTkLabel(
                    table_container,
                    text=row_data["usia"],
                    font=("Helvetica", 12),
                    text_color="#1E293B",
                ).grid(row=row_pos, column=1, pady=12)

                # Kolom 2: Berat Badan
                bb_frame = ctk.CTkFrame(
                    table_container, fg_color="transparent"
                )
                bb_frame.grid(row=row_pos, column=2, pady=12)
                tampilan_bb = row_data["bb"].replace(".", ",")
                lbl_bb_angka = ctk.CTkLabel(
                    bb_frame,
                    text=tampilan_bb,
                    font=("Helvetica", 12, "bold"),
                    text_color="#1E293B",
                )
                lbl_bb_angka.pack()
                lbl_bb_tren = ctk.CTkLabel(
                    bb_frame,
                    text=row_data["bb_tren"],
                    font=("Helvetica", 10, "bold"),
                    text_color="#10B981",
                )
                lbl_bb_tren.pack()

                # Kolom 3 sampai 5
                ctk.CTkLabel(
                    table_container,
                    text=row_data["tb"],
                    font=("Helvetica", 12),
                    text_color="#1E293B",
                ).grid(row=row_pos, column=3, pady=12)
                ctk.CTkLabel(
                    table_container,
                    text=row_data["lk"],
                    font=("Helvetica", 12),
                    text_color="#1E293B",
                ).grid(row=row_pos, column=4, pady=12)
                ctk.CTkLabel(
                    table_container,
                    text=row_data["bbl"],
                    font=("Helvetica", 12),
                    text_color="#1E293B",
                ).grid(row=row_pos, column=5, pady=12)

                # Kolom 6: Asupan Gizi
                badge_gizi = ctk.CTkLabel(
                    table_container,
                    text=f"  • {row_data['gizi']}  ",
                    font=("Helvetica", 10, "bold"),
                    text_color="#B45309",
                    fg_color="#FEF3C7",
                    corner_radius=6,
                    height=24,
                )
                badge_gizi.grid(row=row_pos, column=6, pady=12)

                # Kolom 7: ASI Eksklusif
                badge_asi = ctk.CTkLabel(
                    table_container,
                    text=f"  • {row_data['asi']}  ",
                    font=("Helvetica", 10, "bold"),
                    text_color="#DC2626",
                    fg_color="#FEE2E2",
                    corner_radius=6,
                    height=24,
                )
                badge_asi.grid(row=row_pos, column=7, sticky="", pady=12)

                # Kolom 8: Imunisasi
                badge_imun = ctk.CTkLabel(
                    table_container,
                    text=f"  • {row_data['imun']}  ",
                    font=("Helvetica", 10, "bold"),
                    text_color="#DC2626",
                    fg_color="#FEE2E2",
                    corner_radius=6,
                    height=24,
                )
                badge_imun.grid(row=row_pos, column=8, pady=12)

                # Kolom 9: Hasil
                badge_hasil = ctk.CTkLabel(
                    table_container,
                    text=f" 🚨 {row_data['hasil']} ",
                    font=("Helvetica", 10, "bold"),
                    text_color="#DC2626",
                    fg_color="#FEE2E2",
                    corner_radius=6,
                    height=24,
                )
                badge_hasil.grid(row=row_pos, column=9, pady=12)

                # Kolom 10: Titik Tiga
                ctk.CTkLabel(
                    table_container,
                    text="⋮",
                    font=("Arial", 16, "bold"),
                    text_color="#94A3B8",
                ).grid(row=row_pos, column=10, pady=12)

                line_sep = ctk.CTkFrame(
                    table_container, fg_color="#F1F5F9", height=1
                )
                line_sep.grid(
                    row=row_pos + 1,
                    column=0,
                    columnspan=11,
                    sticky="ew",
                    padx=10,
                )

        # 5. FOOTER
        info_banner = ctk.CTkFrame(
            main_scroll,
            fg_color="#EFF6FF",
            corner_radius=10,
            border_width=1,
            border_color="#DBEAFE",
        )
        info_banner.pack(fill="x", pady=(0, 25))

        lbl_info_icon = ctk.CTkLabel(
            info_banner,
            text="ⓘ",
            font=("Arial", 12, "bold"),
            text_color="#1E40AF",
            fg_color="#BFDBFE",
            width=20,
            height=20,
            corner_radius=10,
        )
        lbl_info_icon.pack(side="left", padx=(15, 10), pady=10)

        lbl_info_text = ctk.CTkLabel(
            info_banner,
            text=(
                "Keterangan: Data di atas menunjukkan riwayat pemeriksaan"
                f" pertumbuhan dan kesehatan {nama} dari waktu ke waktu."
            ),
            font=("Helvetica", 11, "bold"),
            text_color="#1E40AF",
        )
        lbl_info_text.pack(side="left", anchor="w")

        footer_bar = ctk.CTkFrame(main_scroll, fg_color="transparent")
        footer_bar.pack(fill="x")

        btn_kembali = ctk.CTkButton(
            footer_bar,
            text="ㄑ  Kembali",
            font=("Helvetica", 12, "bold"),
            fg_color="white",
            text_color="#475569",
            border_width=1,
            border_color="#E2E8F0",
            hover_color="#F8FAFC",
            width=110,
            height=36,
            corner_radius=8,
            command=detail_window.destroy,
        )
        btn_kembali.pack(side="left")

        tips_banner = ctk.CTkFrame(
            footer_bar,
            fg_color="#FAF5FF",
            corner_radius=8,
            border_width=1,
            border_color="#E9D5FF",
        )
        tips_banner.pack(side="right", fill="x", expand=False)

        lbl_tips = ctk.CTkLabel(
            tips_banner,
            text=(
                "⭐ Tips: Lakukan pemeriksaan rutin setiap bulan untuk memantau"
                " tumbuh kembang secara optimal."
            ),
            font=("Helvetica", 11),
            text_color="#6B21A8",
        )
        lbl_tips.pack(padx=20, pady=8)


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1150x680")
    page = RiwayatPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()