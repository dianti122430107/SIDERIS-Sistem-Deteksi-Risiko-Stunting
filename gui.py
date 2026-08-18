import sqlite3
import os 
import tkinter.messagebox as messagebox
from PIL import Image 
import customtkinter as ctk
from database import init_database

from login import LoginPage, RegisterPage, InfoPage 

class SiderisApp(ctk.CTk):
    """Kelas utama aplikasi SIDERIS yang manage UI dan routing halaman"""
    def __init__(self):
        super().__init__()
        self.current_user_id = None
        self.title("SIDERIS - Sistem Deteksi Risiko Stunting")
        self.geometry("1280x800")
        self.configure(fg_color="#F1F5F9")
        init_database()
        
        self.sidebar_color = "#DFF4FF"     
        self.primary_pink = "#FF7FA8"       
        self.text_dark = "#355070"         
        self.text_active = "#FFFFFF"        
        self.hover_color = "#FF7FA8"
        
        self.sidebar = None
        self.konten_frame = None
        self.halaman_aktif = None
        self.halaman_login_frame = None
        self.user_email = None

        self.tampilkan_login()

        self.update_idletasks()
        self.after(0, lambda: self.state('zoomed'))

    def tampilkan_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.sidebar = None
        self.konten_frame = None
        self.halaman_aktif = None
        self.user_email = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.halaman_login_frame = LoginPage(self, self, on_login_success=self.tampilkan_utama)
        self.halaman_login_frame.pack(fill="both", expand=True)

    def show_frame(self, nama_halaman):
        """Fungsi perantara untuk merespon perintah pindah halaman dari LoginPage/RegisterPage/InfoPage"""
        halaman_lama = self.halaman_login_frame
            
        if nama_halaman == "LoginPage":
            self.halaman_login_frame = LoginPage(self, self, on_login_success=self.tampilkan_utama)
        elif nama_halaman == "RegisterPage":
            self.halaman_login_frame = RegisterPage(self, controller=self)
        elif nama_halaman == "InfoPage":
            self.halaman_login_frame = InfoPage(self, controller=self)
            
        self.halaman_login_frame.pack(fill="both", expand=True)
        
        if halaman_lama:
            halaman_lama.destroy()
            
        self.update_idletasks()
        if hasattr(self.halaman_login_frame, "resize_bg"):
            self.halaman_login_frame.resize_bg()

    def tampilkan_utama(self, user_id):
        self.current_user_id = user_id
        self.user_email = "User"
        
        if self.halaman_login_frame:
            self.halaman_login_frame.destroy()
            self.halaman_login_frame = None

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
        self.buat_sidebar()
        
        self.konten_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.konten_frame.grid(row=0, column=1, sticky="nsew", padx=(10,20), pady=20)
        self.konten_frame.grid_rowconfigure(0, weight=1)
        self.konten_frame.grid_columnconfigure(0, weight=1)
        
        self.pindah_halaman("Dashboard")

    def buat_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        try:
            import sys

            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            kemungkinan_path = [
                os.path.join(base_dir, "assets", "logo_sideris.png"),
                os.path.join(
                    base_dir, "..", "assets", "logo_sideris.png"
                ), 
                os.path.join(base_dir, "logo_sideris.png"),
            ]

            logo_path = None
            for p in kemungkinan_path:
                if os.path.exists(p):
                    logo_path = p
                    break

            if logo_path:
                pil_logo = Image.open(logo_path)
                logo_image = ctk.CTkImage(
                    light_image=pil_logo, dark_image=pil_logo, size=(120, 141)
                )
                logo_label = ctk.CTkLabel(
                    self.sidebar, image=logo_image, text=""
                )
                logo_label.image = logo_image
                logo_label.pack(pady=20)
            else:
                raise FileNotFoundError("Logo tidak ditemukan")

        except Exception as e:
            ctk.CTkLabel(
                self.sidebar,
                text="SIDERIS",
                font=("Arial", 28, "bold"),
                text_color=self.primary_pink,
            ).pack(pady=20)

        menus = [
            ("Dashboard", "🏠"), 
            ("Input Data", "📝"), 
            ("Pemeriksaan", "🩺"),
            ("Riwayat Pemeriksaan", "🕒")
        ]

        self.tombol_menu = {}

        for text, icon in menus:
            is_active = (text == self.halaman_aktif)

            bg_kotak = self.primary_pink if is_active else "#FFFFFF"    
            warna_teks = self.text_active if is_active else self.text_dark

            btn = ctk.CTkButton(
                self.sidebar, 
                text=f"   {icon}   {text}",
                command=lambda t=text: self.pindah_halaman(t),
                font=("Arial", 14, "bold" if is_active else "normal"),
                anchor="w", 
                height=50, 
                corner_radius=12,       
                width=220, 
                fg_color=bg_kotak,         
                text_color=warna_teks,  
                text_color_disabled=warna_teks,     
                hover_color=self.hover_color  
            )
            btn._canvas.configure(takefocus=False)
            btn.bind("<Button-1>", lambda e, b=btn: b.after(10, b.configure, require_redraw=True))
            btn.pack(fill="x", padx=15, pady=6)
            self.tombol_menu[text] = btn

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=1)
        spacer.pack(fill="both", expand=True) 

        btn_logout = ctk.CTkButton(
            self.sidebar, 
            text="⏻ LOGOUT",
            command=self.proses_logout,
            font=("Arial", 14, "bold"),
            anchor="center", 
            height=50, 
            corner_radius=12,
            width=220, 
            fg_color="#FFFFFF",    
            text_color=self.text_dark,  
            text_color_disabled=self.text_dark,
            hover_color=self.hover_color
        )
        btn_logout._canvas.configure(takefocus=False)
        btn_logout.bind("<Button-1>", lambda e, b=btn_logout: b.after(10, b.configure, require_redraw=True))
        btn_logout.pack(fill="x", padx=15, pady=(0, 25))

    def proses_logout(self):
        """Fungsi untuk menampilkan konfirmasi dialog sebelum keluar ke login"""
        tanya = messagebox.askyesno(
            title="Konfirmasi Keluar",
            message="Apakah Anda yakin ingin keluar dari aplikasi SIDERIS?"
        )
        if tanya:
            self.tampilkan_login()

    def pindah_halaman(self, nama_halaman):
        self.focus()
        self.halaman_aktif = nama_halaman
        if not self.konten_frame:
            return
            
        for widget in self.konten_frame.winfo_children():
            widget.destroy()

        for text, btn in self.tombol_menu.items():
            if text == nama_halaman:
                btn.configure(
                    fg_color=self.primary_pink, 
                    text_color=self.text_active, 
                    font=("Arial", 14, "bold")
                )
            else:
                btn.configure(
                    fg_color="#FFFFFF", 
                    text_color=self.text_dark, 
                    font=("Arial", 14, "normal")
                )

        if nama_halaman == "Dashboard":
            from dashboard import DashboardPage
            halaman = DashboardPage(self.konten_frame, controller=self, user_email=self.user_email)
            
        elif nama_halaman == "Input Data":
            from inputdata import InputDataPage
            halaman = InputDataPage(self.konten_frame, controller=self)
            
        elif nama_halaman == "Pemeriksaan":
            from pemeriksaan import PemeriksaanPage
            halaman = PemeriksaanPage(self.konten_frame, controller=self)
            
        elif nama_halaman == "Riwayat Pemeriksaan":
            from riwayat import RiwayatPage
            halaman = RiwayatPage(self.konten_frame, controller=self)
            
        halaman.pack(fill="both", expand=True)
        if hasattr(halaman, "muat_data_dari_db"):
            halaman.muat_data_dari_db()

if __name__ == "__main__":
    app = SiderisApp()
    app.mainloop()