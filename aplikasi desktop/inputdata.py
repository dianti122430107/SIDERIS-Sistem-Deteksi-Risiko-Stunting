import os
import sys
import sqlite3
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
from tkcalendar import Calendar, DateEntry
import tkinter.messagebox as messagebox
from database import ambil_semua_data_sideris, insert_biodata_awal, get_connection

# Konfigurasi Tema Utama Aplikasi
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class InputDataPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F1F5F9")
        self.controller = controller

        self.text_dark = "#0F172A"
        self.text_muted = "#64748B"

        self.all_data = []

        self.grid_columnconfigure(0, weight=1)  # Kolom Form (Kiri)
        self.grid_columnconfigure(1, weight=1)  # Kolom Tabel (Kanan)
        self.grid_rowconfigure(0, weight=1)

        self.setup_form()
        self.setup_table_section()

        self.muat_data_dari_db()

    def setup_form(self):
        self.input_card = ctk.CTkFrame(self, fg_color="white", corner_radius=16, border_width=0)
        self.input_card.grid(row=0, column=0, padx=(25, 12), pady=25, sticky="nsew")

        self.input_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.input_frame.pack(fill="both", expand=True, padx=25, pady=25)

        header_form_box = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        header_form_box.pack(fill="x", pady=(0, 20))

        icon_pink_lbl = ctk.CTkLabel(
            header_form_box, text="📄", font=("Arial", 20), 
            fg_color="#5B8DEF", text_color="white", 
            width=42, height=42, corner_radius=10
        )
        icon_pink_lbl.pack(side="left", padx=(0, 12))

        text_title_box = ctk.CTkFrame(header_form_box, fg_color="transparent")
        text_title_box.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            text_title_box, text="Input Data Balita", 
            font=("Helvetica", 20, "bold"), text_color="#0F172A"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_title_box, text="Masukkan data balita untuk memantau\ntumbuh kembangnya.", 
            font=("Arial", 12), text_color="#64748B", justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # Pengaturan gaya font dan warna label input kustom
        lbl_font, lbl_color = ("Helvetica", 13, "bold"), "#334155"

        ctk.CTkLabel(self.input_frame, text="👤  Nama Lengkap Balita", font=lbl_font, text_color=lbl_color).pack(anchor="w", pady=(5, 0))
        self.entry_nama = ctk.CTkEntry(
            self.input_frame, placeholder_text="Masukkan nama balita", 
            height=42, 
            fg_color="white",
            border_color="#E2E8F0", 
            border_width=1.5, corner_radius=10, text_color="#334155"
        )
        self.entry_nama.pack(fill="x", pady=(6, 18))

        ctk.CTkLabel(self.input_frame, text="📅  Tanggal Lahir Balita", font=lbl_font, text_color=lbl_color).pack(anchor="w")

        cal_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        cal_container.pack(fill="x", pady=(6, 18))

        self.entry_cal = ctk.CTkEntry(
            cal_container, fg_color="white", text_color="#334155", 
            border_width=1.5, border_color="#E2E8F0", height=42, 
            placeholder_text="dd/mm/yyyy", corner_radius=10
        )
        self.entry_cal.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry_cal.insert(0, "17/06/2026")

        btn_cal_pilih = ctk.CTkButton(
            cal_container, text="📅", width=42, height=42, 
            fg_color="#F1F5F9", text_color="black", hover_color="#E2E8F0", corner_radius=10,
            command=lambda: self.buka_popup_kalender(self.entry_cal)
        )
        btn_cal_pilih.pack(side="right")

        ctk.CTkLabel(self.input_frame, text="👥  Jenis Kelamin", font=lbl_font, text_color=lbl_color).pack(anchor="w")
        
        jk_box = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        jk_box.pack(fill="x", pady=(6, 25))

        self.selected_jk = ctk.StringVar(value="")

        self.btn_jk_lki = ctk.CTkButton(
            jk_box, text="Laki-Laki", font=("Arial", 11, "bold"), height=42, border_width=1, corner_radius=10,
            fg_color="white", border_color="#E2E8F0", text_color="#64748B", hover_color="#F8FAFC",
            command=lambda: self.set_jk_selection("Laki-Laki")
        )
        self.btn_jk_lki.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_jk_prm = ctk.CTkButton(
            jk_box, text="Perempuan", font=("Arial", 11, "bold"), height=42, border_width=1, corner_radius=10,
            fg_color="white", border_color="#E2E8F0", text_color="#64748B", hover_color="#F8FAFC",
            command=lambda: self.set_jk_selection("Perempuan")
        )
        self.btn_jk_prm.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.btn_submit = ctk.CTkButton(
            self.input_frame, text="📩 Submit Data", fg_color="#5B8DEF", 
            text_color="white", hover_color="#5B8DEF", 
            corner_radius=10, height=45, font=("Helvetica", 14, "bold"),
            command=self.handle_submit
        )
        self.btn_submit.pack(fill="x", pady=(0, 25))

        info_banner = ctk.CTkFrame(self.input_frame, fg_color="#FFF1F2", corner_radius=10, border_width=0)
        info_banner.pack(fill="x", pady=(10, 0))
        
        info_text = "📋\n\nPastikan data yang dimasukkan sudah sesuai\ndan lengkap sebelum disimpan."
        
        info_lbl = ctk.CTkLabel(
            info_banner, text=info_text, font=("Arial", 11, "bold"), 
            text_color="#9F1239", justify="center"
        )
        info_lbl.pack(padx=15, pady=12, fill="both", expand=True)
        
    def muat_data_dari_db(self):
        """Membaca isi database SQLite terbaru menggunakan koneksi resmi dari database.py"""
        try:
            user_id_aktif = self.controller.current_user_id
            rows = ambil_semua_data_sideris(user_id_aktif)

            self.all_data = []
            for indeks, row in enumerate(rows, start=1):
                self.all_data.append((indeks, row[0], row[1], row[2], None))

            self.update_table(self.all_data)
            print(f"Sukses memuat {len(rows)} data balita ke tabel kanan.")
        except Exception as e:
            print(f"Gagal memuat data awal dari SQLite: {e}")
            
    def buka_popup_kalender(self, target_entry):
        popup = ctk.CTkToplevel(self)
        popup.title("Pilih Tanggal")
        popup.geometry("340x320")
        popup.resizable(False, False)
        
        popup.grab_set()
        popup.attributes("-topmost", True)
        
        frame_popup = ctk.CTkFrame(popup, fg_color="#F1F5F9")
        frame_popup.pack(fill="both", expand=True, padx=15, pady=15)
        
        cal_picker = Calendar(
            frame_popup, 
            date_pattern='dd/mm/yyyy', 
            font=("Arial", 10), 
            showweeknumbers=False,
            background='#475569',          
            foreground='white',            
            headersbackground='#F1F5F9',   
            headersforeground='#475569',   
            selectbackground='#E9708D',    
            selectforeground='white',      
            normalbackground='white',      
            normalforeground='#0F172A',    
            weekendbackground='#F8FAFC',   
            weekendforeground='#EF4444'    
        )
        cal_picker.pack(fill="both", expand=True, padx=10, pady=(10, 15))
        
        try:
            cal_picker.set_date(target_entry.get())
        except Exception:
            pass

        def konfirmasi_tanggal():
            tanggal_terpilih = cal_picker.get_date()
            target_entry.delete(0, 'end')
            target_entry.insert(0, tanggal_terpilih)
            popup.destroy()

        btn_pilih = ctk.CTkButton(
            frame_popup, text="Pilih Tanggal", fg_color="#E9708D", 
            text_color="white", hover_color="#D85F7C", height=40,
            font=("Arial", 12, "bold"), corner_radius=10,
            command=konfirmasi_tanggal
        )
        btn_pilih.pack(fill="x", side="bottom", pady=(5, 5))
        
    def set_jk_selection(self, pilihan):
        self.selected_jk.set(pilihan)
        if pilihan == "Laki-Laki":
            self.btn_jk_lki.configure(fg_color="#EFF6FF", border_color="#2563EB", text_color="#2563EB")
            self.btn_jk_prm.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")
        elif pilihan == "Perempuan":
            self.btn_jk_prm.configure(fg_color="#FFF1F2", border_color="#9F1239", text_color="#9F1239")
            self.btn_jk_lki.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")

    def setup_table_section(self):
        self.table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        self.table_card.grid(row=0, column=1, padx=(15, 30), pady=30, sticky="nsew")

        self.right_frame = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.right_frame.pack(fill="both", expand=True, padx=24, pady=24)

        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Data Terbaru", font=("Arial", 20, "bold"), text_color="#1E293B").pack(side="left")

        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text="🔍 Cari nama balita...", width=240, height=38, fg_color="#F8FAFC", border_color="#E2E8F0", corner_radius=8)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.filter_data)

        self.table_grid_container = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent", label_text="")
        self.table_grid_container.pack(fill="both", expand=True)

        self.table_grid_container.grid_columnconfigure(0, weight=1) 
        self.table_grid_container.grid_columnconfigure(1, weight=3) 
        self.table_grid_container.grid_columnconfigure(2, weight=3) 
        self.table_grid_container.grid_columnconfigure(3, weight=3) 
        self.table_grid_container.grid_columnconfigure(4, weight=2) 

        self.update_table(self.all_data)

    def update_table(self, data_list):
        for widget in self.table_grid_container.winfo_children():
            widget.destroy()

        header_bg = ctk.CTkFrame(self.table_grid_container, fg_color="#F1F5F9", height=40, corner_radius=8)
        header_bg.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 10))
        
        header_bg.grid_columnconfigure(0, weight=1) 
        header_bg.grid_columnconfigure(1, weight=3) 
        header_bg.grid_columnconfigure(2, weight=3) 
        header_bg.grid_columnconfigure(3, weight=3) 
        header_bg.grid_columnconfigure(4, weight=2) 

        headers = ["No", "Nama", "Tanggal Lahir", "Jenis Kelamin", "Aksi"]
        alignments = ["nsew", "w", "nsew", "nsew", "nsew"] 
        
        for idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_bg, 
                text=text, 
                font=("Arial", 12, "bold"), 
                text_color="#475569",
                fg_color="transparent"
            )
            lbl.grid(row=0, column=idx, sticky=alignments[idx], padx=15, pady=8)
            
        current_row = 1
        for item in data_list:
            no, nama, tgl_lahir, jk, _ = item
            
            if jk == "Perempuan":
                jk_display = "Perempuan  ♀"
                jk_color = "#9F1239"   
            else:
                jk_display = "Laki-Laki  ♂"
                jk_color = "#2563EB"   

            ctk.CTkLabel(self.table_grid_container, text=no, font=("Arial", 12, "bold"), text_color="#334155").grid(row=current_row, column=0, sticky="nsew", pady=12)
            ctk.CTkLabel(self.table_grid_container, text=nama, font=("Arial", 12, "bold"), text_color="#334155").grid(row=current_row, column=1, sticky="w", padx=15, pady=12)
            ctk.CTkLabel(self.table_grid_container, text=f"📅 {tgl_lahir}", font=("Arial", 12), text_color="#475569").grid(row=current_row, column=2, sticky="nsew", pady=12)
            
            ctk.CTkLabel(
                self.table_grid_container, 
                text=jk_display, 
                font=("Arial", 12, "bold"),   
                text_color=jk_color          
            ).grid(row=current_row, column=3, sticky="nsew", pady=12)

            btn_edit = ctk.CTkButton(
                self.table_grid_container, text="✏️ Edit", font=("Arial", 11, "bold"),
                text_color="#2563EB", fg_color="white", hover_color="#F1F5F9",
                border_width=1, border_color="#CBD5E1",
                height=28, width=65, corner_radius=8,
                command=lambda n=nama, t=tgl_lahir, j=jk: self.isi_form_dari_tabel(n, t, j)
            )
            btn_edit.grid(row=current_row, column=4, sticky="", pady=12)

            line = ctk.CTkFrame(self.table_grid_container, height=1, fg_color="#F1F5F9")
            line.grid(row=current_row, column=0, columnspan=5, sticky="ew", pady=(40, 0))

            current_row += 1

    def isi_form_dari_tabel(self, nama, tgl_lahir, gender):
        self.entry_nama.delete(0, 'end')
        self.entry_nama.insert(0, nama)
        self.entry_cal.delete(0, 'end')
        self.entry_cal.insert(0, tgl_lahir)
        self.set_jk_selection(gender)
        self.btn_submit.configure(text="Update Data")

    def filter_data(self, event):
        query = self.search_entry.get().lower()
        filtered = [d for d in self.all_data if query in d[1].lower()]
        self.update_table(filtered) 

    def handle_submit(self):
        nama = self.entry_nama.get().strip()
        tgl_lahir = self.entry_cal.get().strip()
        gender = self.selected_jk.get()

        # PRINT UNTUK DIAGNOSIS DI TERMINAL
        print(f"--- MENGECEK INPUT ---")
        print(f"Nama: '{nama}'")
        print(f"Tanggal Lahir: '{tgl_lahir}'")
        print(f"Gender Terbaca: '{gender}'")

        # 1. Validasi input dengan pop-up agar ketahuan mana yang kosong
        if not nama:
            messagebox.showwarning("Gagal", "Nama balita tidak boleh kosong!")
            return
        if not tgl_lahir:
            messagebox.showwarning("Gagal", "Tanggal lahir tidak boleh kosong!")
            return
        if not gender or gender == "":
            messagebox.showwarning("Gagal", "Jenis Kelamin belum dipilih! Silakan pilih Jenis Kelamin terlebih dahulu.")
            return

        if self.btn_submit.cget("text") == "Update Data":
            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE data_sideris 
                    SET tanggal_lahir = ?, jenis_kelamin = ? 
                    WHERE nama = ?
                """, (tgl_lahir, gender, nama))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sukses", f"Data balita '{nama}' berhasil diperbarui!")

                self.btn_submit.configure(text="📩 Submit Data")

                self.entry_nama.delete(0, 'end')
                self.selected_jk.set("")
                self.btn_jk_lki.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")
                self.btn_jk_prm.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")

                self.muat_data_dari_db()
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui data di database.\nLog: {e}")

        else:
            user_id_aktif = self.controller.current_user_id
            simpan_sukses = insert_biodata_awal(user_id_aktif, nama, tgl_lahir, gender)
            
            if simpan_sukses:
                messagebox.showinfo(title="Sukses", message=f"Biodata dasar balita '{nama}' berhasil disimpan!")
                self.entry_nama.delete(0, 'end')
                self.selected_jk.set("")
                self.btn_jk_lki.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")
                self.btn_jk_prm.configure(fg_color="white", border_color="#E2E8F0", text_color="#64748B")
                self.muat_data_dari_db()
            else:
                messagebox.showerror(title="Gagal", message=f"Anak dengan nama '{nama}' sudah terdaftar!")

class InputDataApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SIDERIS - Sistem Informasi Deteksi Stunting")
        self.geometry("1280x800")
        self.configure(fg_color="#F1F5F9")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_main_content()

    def setup_main_content(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        self.active_page = InputDataPage(self.main_container, self)
        self.active_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = InputDataApp()
    app.mainloop()