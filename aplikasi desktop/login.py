import sys

import customtkinter as ctk
from PIL import Image
import os
import sqlite3  # Ditambahkan untuk menghubungkan otentikasi dengan database SIDERIS
import tkinter.messagebox as messagebox  # Ditambahkan untuk pop-up peringatan jika login gagal

# TEMA & WARNA UTAMA APLIKASI
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SiderisApp(ctk.CTk):
    """
    Kelas Utama Aplikasi (Main Window)
    """
    def __init__(self):
        super().__init__()
        
        self.title("SIDERIS - Sistem Deteksi Risiko Stunting")
        self.geometry("1280x800")
        
        # Container Utama (Base Layer)
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for PageClass in (LoginPage, RegisterPage, InfoPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("LoginPage")
        
        self.update_idletasks()
        try:
            self.state('zoomed')
        except:
            pass

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        self.update_idletasks()
        frame.resize_bg()
        frame.tkraise()


class LoginPage(ctk.CTkFrame):
    """
    Halaman Login SIDERIS dengan Layout Split Background (40:60)
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.on_login_success = kwargs.get("on_login_success", None)
        self.controller = kwargs.get("controller", None)
        if len(args) > 0:
            if callable(args[0]):
                self.on_login_success = args[0]
            else:
                self.controller = args[0]
                
        if len(args) > 1 and callable(args[1]):
            self.on_login_success = args[1]

        script_dir = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(script_dir, "assets", "bg_login.png")
        if not os.path.exists(image_path):
            image_path = os.path.abspath(os.path.join(script_dir, "..", "assets", "bg_login.png"))
        if not os.path.exists(image_path):
            image_path = "c:/Users/DIANTI ALIA RAHMAH/Documents/SIDERIS/assets/bg_login.png"
        
        try:
            self.pil_image = Image.open(image_path)
            print(f"Sukses memuat gambar latar dari: {image_path}")
        except Exception as e:
            self.pil_image = None
            print(f"Gagal mendeteksi gambar bg_login.png: {e}")

        self.bg_canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="white")
        self.bg_canvas.pack(fill="both", expand=True)
        
        self.canvas_img_id = None
        self.bind("<Configure>", self.resize_bg)
        
        # FORM LOGIN
        self.login_card = ctk.CTkFrame(self, fg_color="white", corner_radius=25, width=420, height=640)
        self.login_card.place(relx=0.2, rely=0.5, anchor="center")
        self.login_card.grid_propagate(False) 

        # HEADER LOGIN
        header_container = ctk.CTkFrame(self.login_card, fg_color="transparent")
        header_container.pack(fill="x", padx=35, pady=(25, 15))

        brand_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        brand_frame.pack(anchor="w", pady=(0, 20))
        
        logo_login_path = os.path.join(script_dir, "assets", "logo_login.png")
        if not os.path.exists(logo_login_path):
            logo_login_path = os.path.abspath(os.path.join(script_dir, "..", "assets", "logo_login.png"))

        try:
            pil_logo_login = Image.open(logo_login_path)
            self.img_logo_login = ctk.CTkImage(light_image=pil_logo_login, dark_image=pil_logo_login, size=(260, 90))
            self.lbl_logo_top = ctk.CTkLabel(brand_frame, image=self.img_logo_login, text="")
            self.lbl_logo_top.pack(side="left")
        except Exception as e:
            print(f"Gagal memuat logo_login.png: {e}")
        
        self.welcome_label = ctk.CTkLabel(
            header_container, 
            text="Welcome to", 
            font=("Helvetica", 28), 
            text_color="#0F172A",
            anchor="w"
        )
        self.welcome_label.pack(fill="x")

        self.title_sideris = ctk.CTkLabel(
            header_container, 
            text="SIDERIS", 
            font=("Helvetica", 36, "bold"), 
            text_color="#1D559C",
            anchor="w"
        )
        self.title_sideris.pack(fill="x", pady=(0, 8))
        
        self.subtitle_label = ctk.CTkLabel(
            header_container, 
            text="Silakan Masuk untuk Mengakses Data Kesehatan Balita.", 
            font=("Arial", 12), 
            text_color="#64748B", 
            anchor="w",
            justify="left",
            wraplength=330
        )
        self.subtitle_label.pack(fill="x")
        
        # --- FORM INPUT USERNAME ---
        self.username_label = ctk.CTkLabel(self.login_card, text="Nama Lengkap/Username", font=("Helvetica", 13, "bold"), text_color="#1E293B")
        self.username_label.pack(anchor="w", padx=35, pady=(0, 0))
        self.username_entry = ctk.CTkEntry(self.login_card, placeholder_text=" Masukkan Nama Lengkap/Username", width=300, height=42, corner_radius=8, border_color="white")
        self.username_entry.pack(pady=0)

        # --- FORM INPUT KATA SANDI ---
        self.password_label = ctk.CTkLabel(self.login_card, text="Kata Sandi", font=("Helvetica", 13, "bold"), text_color="#1E293B")
        self.password_label.pack(anchor="w", padx=40, pady=(10, 4))

        self.password_frame = ctk.CTkFrame(
            self.login_card, 
            fg_color="#F8FAFC", 
            width=300, 
            height=44, 
            corner_radius=12,
            border_width=0
        )
        self.password_frame.pack(pady=(0, 15))
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(
            self.password_frame, 
            placeholder_text="Masukkan Kata Sandi", 
            placeholder_text_color="#94A3B8",
            show="*", 
            fg_color="transparent", 
            border_width=0, 
            width=215, 
            height=44
        )
        self.password_entry.pack(side="left", padx=(15, 0))

        self.eye_btn = ctk.CTkButton(
            self.password_frame, 
            text=" 👁️", 
            font=("Arial", 16),
            width=24, 
            height=30, 
            fg_color="transparent", 
            hover_color="#E2E8F0", 
            text_color="#64748B", 
            corner_radius=8,
            anchor="center",
            command=self.toggle_password
        )
        self.eye_btn.pack(side="right", padx=(0, 6))
        
        # --- TOMBOL-TOMBOL AKSI ---
        self.login_btn = ctk.CTkButton(
            self.login_card, 
            text="🔑 Masuk", 
            font=("Arial", 14, "bold"), 
            fg_color="#1d559c", 
            hover_color="#154378", 
            width=300, 
            height=45, 
            corner_radius=12, 
            command=self.handle_login
        )
        self.login_btn.pack(pady=(10, 5))
        
        self.or_label = ctk.CTkLabel(self.login_card, text="atau", font=("Arial", 12), text_color="#64748B")
        self.or_label.pack(pady=0)
        
        self.register_btn = ctk.CTkButton(
            self.login_card, 
            text="Belum punya akun? Buat Akun Baru", 
            font=("Arial", 12, "bold"), 
            fg_color="#1d559c", 
            text_color="white", 
            hover_color="#154378", 
            width=300, 
            height=44, 
            corner_radius=12, 
            command=lambda: self.controller.show_frame("RegisterPage")
        )
        self.register_btn.pack(pady=(15, 15))
        
        self.info_btn = ctk.CTkButton(
            self.login_card, text="📋 Informasi SIDERIS", font=("Helvetica", 15, "bold"),
            fg_color="white", text_color="black", hover_color="white",
            border_width=1, border_color="white",
            width=360, height=46, corner_radius=8,
            command=lambda: self.controller.show_frame("InfoPage")
        )
        self.info_btn.pack(pady=(10, 20))

    def resize_bg(self, event=None):
        window_width = event.width if event else self.winfo_width()
        window_height = event.height if event else self.winfo_height()
        
        if window_width > 1 and window_height > 1:
            # 1. Pembagian Rasio Layout 40 : 60
            left_width = int(window_width * 0.40)
            right_width = window_width - left_width

            self.bg_canvas.delete("all")
            
            warna_bg_kiri = "#F1F5F9" 
            warna_bg_kanan = "#F1F5F9"

            self.bg_canvas.create_rectangle(
                0, 0, left_width, window_height, 
                fill=warna_bg_kiri, outline=""
            )
            
            self.bg_canvas.create_rectangle(
                left_width, 0, window_width, window_height, 
                fill=warna_bg_kanan, outline=""
            )

            if self.pil_image:
                resized_pil = self.pil_image.resize((right_width, window_height), Image.Resampling.LANCZOS)
                from PIL import ImageTk
                self.bg_tk_image = ImageTk.PhotoImage(resized_pil)
                
                self.bg_canvas.create_image(
                    left_width, 0, 
                    anchor="nw", image=self.bg_tk_image
                )

    def toggle_password(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.eye_btn.configure(text="🙈", anchor="center")
        else:
            self.password_entry.configure(show="*")
            self.eye_btn.configure(text=" 👁️", anchor="center")
       
    def handle_login(self):
        email_terinput = self.username_entry.get().strip()
        password_terinput = self.password_entry.get().strip()

        print(f"Mencoba login dengan Username/Email: {email_terinput}")

        if email_terinput != "" and password_terinput != "":
            try:
                conn = sqlite3.connect("sideris_database.db")
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT * FROM akun_user WHERE (username = ? OR nama_lengkap = ?) AND password = ?",
                    (email_terinput, email_terinput, password_terinput),
                )
                user_ditemukan = cursor.fetchone()
                conn.close()

                if user_ditemukan:
                    user_id = user_ditemukan[0]
                    user_name = user_ditemukan[1]

                    print(
                        f"Login Sukses! ID: {user_id}, Nama Lengkap: {user_name}"
                    )

                    if self.controller:
                        self.controller.current_user_id = user_id

                    if self.on_login_success:
                        self.on_login_success(user_id)
                    elif self.controller and hasattr(self.controller, "show_frame"):
                        self.controller.show_frame("DashboardPage")
                    else:
                        print("Login sukses! (Mode Standalone tanpa navigasi)")
                else:
                    messagebox.showerror(
                        title="Gagal Masuk",
                        message="Username atau Kata Sandi salah!\nSilakan periksa kembali atau buat akun baru.",
                    )
            except sqlite3.OperationalError as e:
                messagebox.showerror(
                    title="Database Error",
                    message=f"Gagal mengakses database SIDERIS.\nPastikan tabel user sudah terinisialisasi.\nLog: {e}",
                )
        else:
            messagebox.showwarning(
                title="Input Kosong",
                message="Harap isi Username dan Kata Sandi terlebih dahulu!",
            )
            
class RegisterPage(ctk.CTkFrame):
    """
    Halaman Registrasi SIDERIS (Layout Split Screen 40:60 & Header Logo seragam dengan LoginPage)
    """
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.controller = controller
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "assets", "bg_login.png")
        if not os.path.exists(image_path):
            image_path = os.path.abspath(os.path.join(script_dir, "..", "assets", "bg_login.png"))
        if not os.path.exists(image_path):
            image_path = "c:/Users/DIANTI ALIA RAHMAH/Documents/SIDERIS/assets/bg_login.png"
        
        try:
            self.pil_image = Image.open(image_path)
        except Exception as e:
            self.pil_image = None
            print(f"Gagal memuat gambar di RegisterPage: {e}")

        # BACKGROUND
        self.bg_canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="white")
        self.bg_canvas.pack(fill="both", expand=True)
        
        self.canvas_img_id = None
        self.bind("<Configure>", self.resize_bg)

        # FORM REGISTRASI
        self.reg_card = ctk.CTkFrame(
            self, 
            fg_color="white", 
            corner_radius=25, 
            width=420, 
            height=640
        )
        self.reg_card.place(relx=0.2, rely=0.5, anchor="center")
        self.reg_card.grid_propagate(False)

        # HEADER REGISTRASI
        header_container = ctk.CTkFrame(self.reg_card, fg_color="transparent")
        header_container.pack(fill="x", padx=35, pady=(25, 10))

        # 1. Logo_login.png
        brand_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        brand_frame.pack(anchor="w", pady=(0, 20))

        logo_login_path = os.path.join(script_dir, "assets", "logo_login.png")
        if not os.path.exists(logo_login_path):
            logo_login_path = os.path.abspath(os.path.join(script_dir, "..", "assets", "logo_login.png"))

        try:
            pil_logo_login = Image.open(logo_login_path)
            self.img_logo_login = ctk.CTkImage(
                light_image=pil_logo_login, 
                dark_image=pil_logo_login, 
                size=(260, 90)
            )
            self.lbl_logo_top = ctk.CTkLabel(brand_frame, image=self.img_logo_login, text="")
            self.lbl_logo_top.pack(side="left")
        except Exception as e:
            print(f"Gagal memuat logo_login.png di Register: {e}")

        # 2. Judul Registrasi
        self.reg_title = ctk.CTkLabel(
            header_container, 
            text="Buat Akun Baru", 
            font=("Helvetica", 30, "bold"), 
            text_color="#1D559C",
            anchor="w"
        )
        self.reg_title.pack(fill="x", pady=(0, 8))
        
        # 3. Subtitle Deskripsi
        self.subtitle_label = ctk.CTkLabel(
            header_container, 
            text="Silakan daftar untuk membuat akun dan mulai menggunakan Sistem SIDERIS.", 
            font=("Arial", 12), 
            text_color="#64748B", 
            anchor="w",
            justify="left",
            wraplength=330
        )
        self.subtitle_label.pack(fill="x")

        # INPUT REGISTRASI
        self.name_label = ctk.CTkLabel(self.reg_card, text="Nama Lengkap", font=("Helvetica", 13, "bold"), text_color="#1E293B")
        self.name_label.pack(anchor="w", padx=35, pady=(0, 10))
        self.name_entry = ctk.CTkEntry(self.reg_card, placeholder_text="Masukkan Nama Lengkap", width=300, height=42, corner_radius=8, border_color="#CBD5E1")
        self.name_entry.pack(pady=0)
        
        self.username_label = ctk.CTkLabel(self.reg_card, text="Username", font=("Helvetica", 13, "bold"), text_color="#1E293B")
        self.username_label.pack(anchor="w", padx=35, pady=(10, 2))
        self.username_entry = ctk.CTkEntry(self.reg_card, placeholder_text="Masukkan Username", width=300, height=42, corner_radius=8, border_color="#CBD5E1")
        self.username_entry.pack(pady=0)

        self.password_label = ctk.CTkLabel(self.reg_card, text="Kata Sandi", font=("Helvetica", 13, "bold"), text_color="#1E293B")
        self.password_label.pack(anchor="w", padx=35, pady=(10, 2))

        self.password_frame = ctk.CTkFrame(
            self.reg_card, 
            fg_color="#F8FAFC", 
            width=300, 
            height=44, 
            corner_radius=12,
            border_width=0,
        )
        self.password_frame.pack(pady=0)
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(
            self.password_frame, 
            placeholder_text="Masukkan Kata Sandi", 
            placeholder_text_color="#94A3B8",
            show="*", 
            fg_color="transparent", 
            border_width=0, 
            width=215, 
            height=44,
            text_color="#1E293B"
        )
        self.password_entry.pack(side="left", padx=(15, 0))

        self.eye_btn = ctk.CTkButton(
            self.password_frame, 
            text=" 👁️", 
            font=("Arial", 16),
            width=24, 
            height=30, 
            fg_color="transparent", 
            hover_color="#E2E8F0", 
            text_color="#64748B", 
            corner_radius=8,
            anchor="center",
            command=self.toggle_password
        )
        self.eye_btn.pack(side="right", padx=(0, 6))
        
        # Tombol Aksi
        self.register_btn = ctk.CTkButton(
            self.reg_card, 
            text="📝 Daftar Akun", 
            font=("Arial", 14, "bold"), 
            fg_color="#1D559C", 
            hover_color="#154378", 
            width=300, 
            height=45, 
            corner_radius=12, 
            command=self.handle_registration
        )
        self.register_btn.pack(pady=(15, 5))
        
        self.or_label = ctk.CTkLabel(self.reg_card, text="atau", font=("Arial", 12), text_color="#64748B")
        self.or_label.pack(pady=0)
        
        self.back_to_login = ctk.CTkButton(
            self.reg_card, 
            text="Sudah punya akun? Masuk di sini", 
            font=("Arial", 12, "bold"), 
            fg_color="#1D559C", 
            text_color="white", 
            hover_color="#154378", 
            width=300, 
            height=44, 
            corner_radius=12, 
            command=lambda: self.controller.show_frame("LoginPage")
        )
        self.back_to_login.pack(pady=(10, 15))

    def resize_bg(self, event=None):
        window_width = event.width if event else self.winfo_width()
        window_height = event.height if event else self.winfo_height()
        
        if window_width > 1 and window_height > 1:
            left_width = int(window_width * 0.40)
            right_width = window_width - left_width

            self.bg_canvas.delete("all")

            warna_bg_kiri = "#F1F5F9" 
            warna_bg_kanan = "#F1F5F9" 

            self.bg_canvas.create_rectangle(
                0, 0, left_width, window_height, 
                fill=warna_bg_kiri, outline=""
            )

            self.bg_canvas.create_rectangle(
                left_width, 0, window_width, window_height, 
                fill=warna_bg_kanan, outline=""
            )

            if self.pil_image:
                resized_pil = self.pil_image.resize((right_width, window_height), Image.Resampling.LANCZOS)
                from PIL import ImageTk
                self.bg_tk_image = ImageTk.PhotoImage(resized_pil)
                
                self.bg_canvas.create_image(
                    left_width, 0, 
                    anchor="nw", image=self.bg_tk_image
                )

    def toggle_password(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.eye_btn.configure(text="🙈", anchor="center")
        else:
            self.password_entry.configure(show="*")
            self.eye_btn.configure(text=" 👁️", anchor="center")
            
    def handle_registration(self):
        nama_lengkap = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if nama_lengkap == "" or username == "" or password == "":
            messagebox.showwarning(
                title="Pendaftaran Gagal",
                message="Semua kolom data formulir wajib diisi!",
            )
            return

        try:
            if getattr(sys, "frozen", False):
                BASE_DIR = os.path.dirname(sys.executable)
            else:
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))

            DB_PATH = os.path.join(BASE_DIR, "sideris_database.db")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS akun_user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nama_lengkap TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )
                """)

            cursor.execute(
                "SELECT username FROM akun_user WHERE username = ?", (username,)
            )
            if cursor.fetchone():
                messagebox.showerror(
                    title="Username Sudah Ada",
                    message=(
                        "Username tersebut sudah terdaftar! Gunakan username lain."
                    ),
                )
                conn.close()
                return

            cursor.execute(
                "INSERT INTO akun_user (nama_lengkap, username, password) VALUES"
                " (?, ?, ?)",
                (nama_lengkap, username, password),
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                title="Registrasi Berhasil",
                message="Akun SIDERIS Anda berhasil dibuat! Silakan login.",
            )
            self.controller.show_frame("LoginPage")

        except Exception as e:
            messagebox.showerror(
                title="Database Error",
                message=f"Gagal menyimpan data ke database.\nLog: {e}",
            )

class InfoPage(ctk.CTkFrame):
    """
    Halaman Card Informasi SIDERIS (Gaya Dashboard Grid Sesuai Gambar)
    """
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.controller = controller

        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "assets", "bg_informasi.png")
        if not os.path.exists(image_path):
            image_path = os.path.abspath(os.path.join(script_dir, "..", "assets", "bg_informasi.png"))
        if not os.path.exists(image_path):
            image_path = "c:/Users/DIANTI ALIA RAHMAH/Documents/SIDERIS/assets/bg_informasi.png"
        
        try:
            self.pil_image = Image.open(image_path)
            print(f"Sukses memuat bg_informasi.png dari: {image_path}")
        except Exception as e:
            self.pil_image = None
            print(f"Gagal memuat bg_informasi.png: {e}")

        self.bg_canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="#F1F5F9")
        self.bg_canvas.pack(fill="both", expand=True)
        
        self.bg_canvas.bind("<Configure>", self.resize_bg)
        
        self.info_card = ctk.CTkFrame(
            self, 
            fg_color="white", 
            corner_radius=25, 
            width=700, 
            height=660,
            border_width=1,
            border_color="#CBD5E1"
        )
        self.info_card.place(relx=0.5, rely=0.5, anchor="center")
        self.info_card.pack_propagate(False)

        self.info_icon = ctk.CTkLabel(self.info_card, text="🛡️", font=("Arial", 32), anchor="center")
        self.info_icon.pack(pady=(20, 2))
        
        self.info_title = ctk.CTkLabel(self.info_card, text="Tentang SIDERIS", font=("Helvetica", 26, "bold"), text_color="#1d559c")
        self.info_title.pack(pady=(0, 10))

        self.desc_box = ctk.CTkFrame(self.info_card, fg_color="#EFF6FF", corner_radius=15, border_width=1, border_color="#BFDBFE")
        self.desc_box.pack(fill="x", padx=40, pady=5)
        
        desc_text = (
            "SIDERIS (Sistem Deteksi Risiko Stunting) adalah platform digital yang dirancang khusus "
            "untuk membantu tenaga kesehatan dan orang tua dalam memantau tumbuh kembang anak serta "
            "mendeteksi risiko stunting sejak dini secara cepat, akurat, dan terintegrasi."
        )
        self.desc_label = ctk.CTkLabel(self.desc_box, text=desc_text, font=("Arial", 11), text_color="#1E3A8A", justify="left", wraplength=580)
        self.desc_label.pack(padx=20, pady=12)

        self.features_title = ctk.CTkLabel(self.info_card, text="───  Fitur Utama  ───", font=("Helvetica", 13, "bold"), text_color="#1d559c")
        self.features_title.pack(pady=10)

        self.grid_container = ctk.CTkFrame(self.info_card, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=35)
        
        for i in range(3): self.grid_container.grid_columnconfigure(i, weight=1, uniform="group1")
        for i in range(2): self.grid_container.grid_rowconfigure(i, weight=1, uniform="group2")
        
        features_data = [
            ("Perhitungan\nZ-Score Otomatis", "Menghitung Z-Score TB/U, BB/U, dan BB/TB sesuai standar WHO.", "📊"),
            ("Pelacakan Riwayat\nImunisasi Anak", "Mencatat dan memantau riwayat imunisasi anak secara lengkap.", "💉"),
            ("Kuesioner Frekuensi\nMakanan (FFQ)", "Mengumpulkan data pola makan anak untuk menilai asupan gizi.", "📋"),
            ("Deteksi Dini\nRisiko Stunting", "Memberikan hasil deteksi risiko stunting berbasis antropometri.", "🛡️"),
            ("Riwayat Pemeriksaan\nTerintegrasi", "Menyimpan riwayat pemeriksaan anak secara digital.", "🕒"),
            ("Manajemen Data\nAman & Terpercaya", "Data tersimpan dengan aman dan terjaga kerahasiaannya.", "👥")
        ]
        
        idx = 0
        for row in range(2):
            for col in range(3):
                title, desc, icon = features_data[idx]
                
                card = ctk.CTkFrame(self.grid_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0")
                card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                icon_lbl = ctk.CTkLabel(card, text=icon, font=("Arial", 20), fg_color="#F0F4F8", width=34, height=34, corner_radius=17)
                icon_lbl.pack(pady=(8, 2))
                
                tit_lbl = ctk.CTkLabel(card, text=title, font=("Helvetica", 10, "bold"), text_color="#1E3A8A", justify="center")
                tit_lbl.pack(pady=2)
                
                desc_lbl = ctk.CTkLabel(card, text=desc, font=("Arial", 9), text_color="#64748B", justify="center", wraplength=170)
                desc_lbl.pack(padx=6, pady=(2, 8))
                
                idx += 1

        self.footer_banner = ctk.CTkFrame(self.info_card, fg_color="#F8FAFC", corner_radius=12, border_width=1, border_color="#E2E8F0")
        self.footer_banner.pack(fill="x", padx=40, pady=(8, 12))
        
        footer_text = "🛡️  SIDERIS berkomitmen untuk menjaga keamanan data pengguna dan mendukung pencegahan stunting."
        self.footer_label = ctk.CTkLabel(self.footer_banner, text=footer_text, font=("Arial", 10), text_color="#475569", justify="center", wraplength=580)
        self.footer_label.pack(padx=15, pady=8)

        self.back_btn = ctk.CTkButton(
            self.info_card, text="📥 Kembali ke Login", font=("Arial", 13, "bold"), 
            fg_color="#1d559c", hover_color="#154378", width=600, height=42, corner_radius=10,
            command=lambda: self.controller.show_frame("LoginPage")
        )
        self.back_btn.pack(pady=(0, 18))

        self.after(100, self.resize_bg)

    def resize_bg(self, event=None):
        window_width = event.width if event else self.bg_canvas.winfo_width()
        window_height = event.height if event else self.bg_canvas.winfo_height()
        
        if window_width > 10 and window_height > 10:
            self.bg_canvas.delete("all")
            
            if self.pil_image:
                resized_pil = self.pil_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
                from PIL import ImageTk
                self.bg_tk_image = ImageTk.PhotoImage(resized_pil)
                
                self.bg_canvas.create_image(
                    0, 0, 
                    anchor="nw", image=self.bg_tk_image
                )
            else:
                self.bg_canvas.create_rectangle(
                    0, 0, window_width, window_height,
                    fill="#F1F5F9", outline=""
                )

            self.info_card.lift()

if __name__ == "__main__":
    app = SiderisApp()
    app.mainloop()