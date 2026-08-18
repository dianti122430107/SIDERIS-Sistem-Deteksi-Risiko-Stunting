import customtkinter as ctk
from PIL import Image
import os
import random
from database import ambil_semua_data_sideris

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller=None, user_email=None):
        super().__init__(parent)
        self.controller = controller
        self.user_email = user_email 

        if self.user_email and isinstance(self.user_email, str) and "@" in self.user_email:
            self.username = self.user_email.split("@")[0].capitalize()
        else:
            self.username = "Admin"

        self.configure(fg_color="#F1F5F9")

        self.primary_pink = "#E9708D"
        self.text_dark = "#0F172A"
        self.text_muted = "#64748B"
        self.color_mint = "#E0F2F1"

        self.balita_list = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.setup_main_content()
        self.muat_data_dari_db()

    def setup_main_content(self):

        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text=f"Halo, Selamat Datang Kembali! 👋", 
                     font=("Arial", 28, "bold"), text_color=self.text_dark).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Pantau tumbuh kembang si kecil hari ini.", 
                     font=("Arial", 15), text_color=self.text_muted).pack(anchor="w")

        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_total = self.create_card(
            stats_frame, title="Total Data Balita", value="0", icon="👥", 
            accent_color="#3B82F6", bg_icon_color="#EFF6FF", 
            trend_text="Data Terkini SIDERIS", trend_color="#10B981"
        )
        self.card_total.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.card_risiko = self.create_card(
            stats_frame, title="Balita Berisiko Stunting", value="0", icon="⚠️", 
            accent_color="#EF4444", bg_icon_color="#FEF2F2", 
            trend_text="Evaluasi RF + BL-SMOTE", trend_color="#EF4444"
        )
        self.card_risiko.grid(row=0, column=1, padx=10, sticky="nsew")

        self.card_update = self.create_card(
            stats_frame, title="Data Anak Belum Update", value="0", icon="🕒", 
            accent_color="#F59E0B", bg_icon_color="#FFFBEB", 
            trend_text="Menunggu Pemeriksaan", trend_color="#64748B"
        )
        self.card_update.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        
        info_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        info_frame.pack(fill="both", expand=True)
        
        info_frame.grid_columnconfigure(0, weight=2)
        info_frame.grid_columnconfigure(1, weight=1)

        # 1. DAFTAR BALITA BERISIKO
        self.risk_table = ctk.CTkFrame(
            info_frame, fg_color="white", corner_radius=20, 
            border_width=1, border_color="#E2E8F0"
        )
        self.risk_table.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        table_top_header = ctk.CTkFrame(self.risk_table, fg_color="transparent")
        table_top_header.pack(fill="x", padx=24, pady=15)

        ctk.CTkLabel(table_top_header, text="Daftar Balita Terbaru", font=("Arial", 18, "bold"), text_color=self.text_dark).pack(side="left")

        self.table_grid = ctk.CTkFrame(self.risk_table, fg_color="transparent")
        self.table_grid.pack(fill="both", expand=True, padx=24, pady=(5, 15))

        # 2. PUSAT INFORMASI
        self.info_box = ctk.CTkFrame(info_frame, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        self.info_box.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        
        header_info = ctk.CTkFrame(self.info_box, fg_color="transparent")
        header_info.pack(fill="x", pady=(20, 10), padx=24)
        header_info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_info, text="💡 Pusat Informasi", 
            font=("Arial", 18, "bold"), text_color=self.text_dark
        ).grid(row=0, column=0, sticky="w")

        # BANK DATA
        self.bank_pesan_penting = [
            "Protein hewani (ikan/telur) harus ada di setiap suapan anak untuk cegah stunting.",
            "Berikan ASI Eksklusif selama 6 bulan penuh tanpa tambahan cairan atau makanan lain.",
            "Tepati jadwal imunisasi dasar lengkap ke Posyandu sebelum anak menginjak usia 1 tahun.",
            "Gunakan air bersih dan sabun saat mencuci tangan sebelum menyiapkan MPASI si kecil."
        ]

        self.bank_tips_trick = [
            "Tambahkan sedikit santan atau minyak pada MPASI untuk menambah kalori anak.",
            "Variasikan bentuk dan tekstur MPASI secara bertahap sesuai dengan pertambahan usia anak.",
            "Hindari memberikan gadget saat anak makan agar fokus pada proses mengunyah makanan.",
            "Jika anak melakukan GTM (Gerakan Tutup Mulut), coba tawarkan makan porsi kecil tapi sering."
        ]

        self.bank_pengetahuan = [
            "Stunting bukan hanya soal pendek, tapi juga terhambatnya perkembangan otak anak.",
            "1000 Hari Pertama Kehidupan (HPK) adalah periode emas pertumbuhan organ vital si kecil.",
            "Anak stunting cenderung memiliki sistem kekebalan tubuh yang lebih lemah dan mudah sakit.",
            "Kekurangan gizi kronis sejak dalam kandungan menjadi pemicu utama kondisi stunting."
        ]

        self.bank_rekomendasi = [
            "Konsultasikan dengan dokter anak jika Anda khawatir tentang pertumbuhan anak.",
            "Pastikan anak menerima asupan gizi yang cukup dan bervariasi setiap harinya.",
            "Ajak anak berolahraga secara teratur untuk mendukung pertumbuhan fisiknya.",
            "Lakukan pemeriksaan kesehatan rutin di posyandu untuk memantau perkembangan anak."
        ]

        self.container_items_info = ctk.CTkFrame(self.info_box, fg_color="transparent")
        self.container_items_info.pack(fill="both", expand=True, pady=(0, 20), padx=24)

        def add_info_item(kategori, isi, accent_color, bg_pastel):
            item_card = ctk.CTkFrame(self.container_items_info, fg_color=bg_pastel, corner_radius=14, border_width=1, border_color="#E2E8F0")
            item_card.pack(fill="x", padx=24, pady=5)
            
            badge_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            badge_frame.pack(fill="x", padx=18, pady=(12, 5))
            
            ctk.CTkLabel(badge_frame, text="●", font=("Arial", 9), text_color=accent_color).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(badge_frame, text=kategori, font=("Arial", 11, "bold"), text_color=accent_color).pack(side="left")
            
            teks_isi = ctk.CTkLabel(
                item_card, text=isi, font=("Arial", 12), 
                text_color="#475569", wraplength=280, justify="left"
            )
            teks_isi.pack(padx=(18, 22), pady=(0, 12), anchor="w")

        def refresh_informasi_acak():
            for widget in self.container_items_info.winfo_children():
                widget.destroy()
                
            pesan_terpilih = random.choice(self.bank_pesan_penting)
            tips_terpilih = random.choice(self.bank_tips_trick)
            pengetahuan_terpilih = random.choice(self.bank_pengetahuan)
            rekomendasi_terpilih = random.choice(self.bank_rekomendasi)
            
            add_info_item("PESAN PENTING", pesan_terpilih, "#0D9488", "#F0FDF4")
            add_info_item("TIPS & TRICK", tips_terpilih, "#2563EB", "#EFF6FF")
            add_info_item("PENGETAHUAN", pengetahuan_terpilih, "#7C3AED", "#F5F3FF")
            add_info_item("REKOMENDASI", rekomendasi_terpilih, "#D97706", "#FFFBEB")

        btn_refresh = ctk.CTkButton(
            header_info, text="🔄 Refresh", font=("Arial", 11, "bold"),
            text_color="#2563EB", fg_color="#EFF6FF", hover_color="#DBEAFE",
            width=85, height=28, corner_radius=8,
            command=refresh_informasi_acak
        )
        btn_refresh.grid(row=0, column=1, sticky="e")

        refresh_informasi_acak()

    def render_tabel_balita(self):
        for widget in self.table_grid.winfo_children():
            widget.destroy()

        self.table_grid.grid_columnconfigure(0, weight=3) 
        self.table_grid.grid_columnconfigure(1, weight=2) 
        self.table_grid.grid_columnconfigure(2, weight=2) 
        self.table_grid.grid_columnconfigure(3, weight=2, minsize=100) 
        self.table_grid.grid_columnconfigure(4, weight=3) 

        ctk.CTkLabel(self.table_grid, text="NAMA", font=("Arial", 11, "bold"), text_color=self.text_muted).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self.table_grid, text="USIA", font=("Arial", 11, "bold"), text_color=self.text_muted).grid(row=0, column=1, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self.table_grid, text="JENIS KELAMIN", font=("Arial", 11, "bold"), text_color=self.text_muted).grid(row=0, column=2, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self.table_grid, text="STATUS RISIKO", font=("Arial", 11, "bold"), text_color=self.text_muted).grid(row=0, column=3, pady=(0, 10))
        ctk.CTkLabel(self.table_grid, text="TERAKHIR DIPERIKSA", font=("Arial", 11, "bold"), text_color=self.text_muted).grid(row=0, column=4, sticky="w", pady=(0, 10))

        if not self.balita_list:
            lbl_kosong = ctk.CTkLabel(self.table_grid, text="Belum ada riwayat pemeriksaan data balita.", font=("Arial", 13, "italic"), text_color=self.text_muted)
            lbl_kosong.grid(row=1, column=0, columnspan=5, pady=30)
            return

        data_tampil = self.balita_list[:10]

        current_row = 1
        for name, age, gender, status, date_check in data_tampil:
            if status == "Tinggi":
                color_status, bg_status = "#EF4444", "#FEF2F2"
            elif status == "Sedang":
                color_status, bg_status = "#F59E0B", "#FFFBEB"
            else:
                color_status, bg_status = "#3B82F6", "#EFF6FF"

            avatar = "👧" if gender == "Perempuan" else "👦"
            gender_icon = "♀️" if gender == "Perempuan" else "♂️"

            # Kolom 0: Nama
            name_frame = ctk.CTkFrame(self.table_grid, fg_color="transparent")
            name_frame.grid(row=current_row, column=0, sticky="w", pady=6)
            ctk.CTkLabel(name_frame, text=avatar, font=("Arial", 16)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(name_frame, text=name, font=("Arial", 13, "bold"), text_color=self.text_dark).pack(side="left")

            # Kolom 1: Usia
            ctk.CTkLabel(self.table_grid, text=f"{age} Bulan", font=("Arial", 13), text_color=self.text_dark).grid(row=current_row, column=1, sticky="w", pady=6)

            # Kolom 2: Jenis Kelamin
            gender_frame = ctk.CTkFrame(self.table_grid, fg_color="transparent")
            gender_frame.grid(row=current_row, column=2, sticky="w", pady=6)
            ctk.CTkLabel(gender_frame, text=gender_icon, font=("Arial", 13), text_color=color_status).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(gender_frame, text=gender, font=("Arial", 13), text_color=self.text_dark).pack(side="left")

            # Kolom 3: Status Risiko
            status_badge = ctk.CTkLabel(
                self.table_grid, text=status, font=("Arial", 11, "bold"), text_color=color_status,
                fg_color=bg_status, height=26, width=80, corner_radius=13
            )
            status_badge.grid(row=current_row, column=3, pady=6)

            # Kolom 4: Tanggal Periksa
            date_frame = ctk.CTkFrame(self.table_grid, fg_color="transparent")
            date_frame.grid(row=current_row, column=4, sticky="ew", pady=6)
            ctk.CTkLabel(date_frame, text="📅", font=("Arial", 13)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(date_frame, text=date_check, font=("Arial", 13), text_color=self.text_dark).pack(side="left")

            current_row += 1

    def create_card(self, parent, title, value, icon, accent_color, bg_icon_color, trend_text, trend_color):
        card = ctk.CTkFrame(parent, height=140, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        card.grid_propagate(False)
        
        icon_bg = ctk.CTkLabel(card, text=icon, font=("Arial", 24), text_color=accent_color, fg_color=bg_icon_color, width=30, height=45, corner_radius=325)
        icon_bg.place(x=20, y=25)
        
        ctk.CTkLabel(card, text=title.upper(), font=("Arial", 11, "bold"), text_color="#64748B").place(x=100, y=25)
        
        lbl_value = ctk.CTkLabel(card, text=value, font=("Arial", 38, "bold"), text_color="#0F172A")
        lbl_value.place(x=100, y=48)
        
        if title == "Total Data Balita":
            self.lbl_total_val = lbl_value
        elif title == "Balita Berisiko Stunting":
            self.lbl_risiko_val = lbl_value
        else:
            self.lbl_update_val = lbl_value
        
        ctk.CTkLabel(card, text=trend_text, font=("Arial", 11, "bold"), text_color=trend_color).place(x=100, y=98)
        return card

    def muat_data_dari_db(self):
        try:
            user_id_aktif = self.controller.current_user_id if self.controller else 1
            rows = ambil_semua_data_sideris(user_id_aktif)
            
            self.balita_list = []
            for row in rows:
                nama = row[0]
                usia = row[4] if row[4] is not None else 0
                jenis_kelamin = row[2] or "-"
                risiko = row[20] if row[20] else "Belum Diperiksa"
                tanggal_periksa = row[3] if row[3] else "-"
                self.balita_list.append((nama, usia, jenis_kelamin, risiko, tanggal_periksa))

            total_data = len(self.balita_list)
            total_berisiko = sum(1 for item in self.balita_list if item[3] in ["Sedang", "Tinggi"])
            total_belum_update = sum(1 for row in rows if not row[3])

            self.lbl_total_val.configure(text=str(total_data))
            self.lbl_risiko_val.configure(text=str(total_berisiko))
            self.lbl_update_val.configure(text=str(total_belum_update))
            
            self.render_tabel_balita()
            print(f"Dashboard sukses memuat {total_data} data untuk User ID: {user_id_aktif}")
        except Exception as e:
            print("Gagal memuat dashboard dari database:", e)

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Dashboard Monitoring Stunting")
    root.geometry("1100x700")
    
    app = DashboardPage(root, user_email=None)
    app.pack(fill="both", expand=True)
    
    root.mainloop()