import sqlite3
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "sideris_database.db"


def get_connection():
    """Fungsi untuk membuat koneksi ke SQLite DB"""
    return sqlite3.connect(str(DB_PATH))


def migrasi_dan_hapus_unique_constraint():
    """Otomatis dijalankan untuk menghapus constraint UNIQUE pada kolom nama"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Cek apakah tabel data_sideris sudah ada
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='data_sideris'"
        )
        row = cursor.fetchone()
        
        if row:
            schema_sql = row[0]
            # Cek apakah skema masih mengandung UNIQUE pada nama
            if "UNIQUE" in schema_sql.upper():
                print("⚙️ Melakukan migrasi database: Menghapus batasan UNIQUE pada nama balita...")
                cursor.execute("PRAGMA foreign_keys=OFF;")
                cursor.execute("ALTER TABLE data_sideris RENAME TO data_sideris_old;")
                
                cursor.execute("""
                CREATE TABLE data_sideris (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    nama TEXT NOT NULL,
                    tanggal_lahir TEXT NOT NULL,
                    jenis_kelamin TEXT NOT NULL,
                    tanggal_pemeriksaan TEXT,
                    usia_bulan INTEGER,
                    berat_badan_lahir REAL,
                    berat_badan REAL,
                    tinggi_badan REAL,
                    lingkar_kepala REAL,
                    asi TEXT,
                    imunisasi TEXT,
                    asupan_gizi TEXT,
                    bb_u_zscore REAL,
                    bb_u_status TEXT,
                    tb_u_zscore REAL,
                    tb_u_status TEXT,
                    bb_tb_zscore REAL,
                    bb_tb_status TEXT,
                    lk_u_zscore REAL,
                    lk_u_status TEXT,
                    tingkat_risiko TEXT,
                    FOREIGN KEY (user_id) REFERENCES akun_user(id)
                );
                """)
                
                cursor.execute("INSERT INTO data_sideris SELECT * FROM data_sideris_old;")
                cursor.execute("DROP TABLE data_sideris_old;")
                cursor.execute("PRAGMA foreign_keys=ON;")
                conn.commit()
                print("✅ SUKSES: Database berhasil dimigrasi!")
    except Exception as e:
        print("Status migrasi database:", e)
    finally:
        conn.close()


def init_database():
    """Fungsi inisialisasi tabel database SIDERIS"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_sideris (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nama TEXT NOT NULL,
        tanggal_lahir TEXT NOT NULL,
        jenis_kelamin TEXT NOT NULL,
        tanggal_pemeriksaan TEXT,
        usia_bulan INTEGER,
        berat_badan_lahir REAL,
        berat_badan REAL,
        tinggi_badan REAL,
        lingkar_kepala REAL,
        asi TEXT,
        imunisasi TEXT,
        asupan_gizi TEXT,
        bb_u_zscore REAL,
        bb_u_status TEXT,
        tb_u_zscore REAL,
        tb_u_status TEXT,
        bb_tb_zscore REAL,
        bb_tb_status TEXT,
        lk_u_zscore REAL,
        lk_u_status TEXT,
        tingkat_risiko TEXT,
        FOREIGN KEY (user_id) REFERENCES akun_user(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS akun_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_lengkap TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tabel_ffq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kategori TEXT NOT NULL,
        nama_makanan TEXT NOT NULL
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM tabel_ffq")
    if cursor.fetchone()[0] == 0:
        item_ffq_default = [
            ("Karbohidrat", "Nasi"),
            ("Karbohidrat", "Bubur"),
            ("Karbohidrat", "Mie / Bihun"),
            ("Karbohidrat", "Roti"),
            ("Karbohidrat", "Kentang / Ubi / Singkong"),
            ("Protein Hewani", "Telur"),
            ("Protein Hewani", "Ayam"),
            ("Protein Hewani", "Ikan"),
            ("Protein Hewani", "Daging Sapi / Kambing"),
            ("Protein Hewani", "Hati Ayam / Sapi"),
            ("Susu", "Susu / Susu Formula"),
            ("Protein Nabati", "Tempe"),
            ("Protein Nabati", "Tahu"),
            ("Protein Nabati", "Kacang-kacangan"),
            ("Sayuran", "Sayur Hijau"),
            ("Sayuran", "Sayur Orange"),
            ("Sayuran", "Sayur Sup / Bening"),
            ("Buah", "Pisang"),
            ("Buah", "Pepaya / Mangga"),
            ("Buah", "Jeruk"),
            ("Buah", "Buah Lainnya"),
            ("Camilan", "Biskuit / Biskuit Balita"),
            ("Camilan", "Snack Kemasan"),
            ("Camilan", "Permen / Coklat"),
            ("Camilan", "Minuman Manis"),
        ]
        cursor.executemany(
            "INSERT INTO tabel_ffq (kategori, nama_makanan) VALUES (?, ?)",
            item_ffq_default,
        )

    conn.commit()
    conn.close()


def insert_biodata_awal(user_id, nama, tanggal_lahir, jenis_kelamin):
    """Mendaftarkan balita baru pertama kali"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM data_sideris WHERE user_id = ? AND nama = ? LIMIT 1",
            (user_id, nama),
        )
        if cursor.fetchone():
            print(f"Anak dengan nama {nama} sudah terdaftar.")
            return False

        cursor.execute(
            """
            INSERT INTO data_sideris (user_id, nama, tanggal_lahir, jenis_kelamin) 
            VALUES (?, ?, ?, ?)
        """,
            (user_id, nama, tanggal_lahir, jenis_kelamin),
        )
        conn.commit()
        return True
    except Exception as e:
        print("Gagal mendaftarkan balita:", e)
        return False
    finally:
        conn.close()


def ambil_daftar_nama_balita(user_id):
    """Mengambil daftar nama unik balita untuk dropdown"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT nama FROM data_sideris WHERE user_id = ? ORDER BY nama ASC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def ambil_biodata_balita(user_id, nama):
    """Mengambil biodata dasar balita"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT jenis_kelamin, tanggal_lahir 
        FROM data_sideris 
        WHERE user_id = ? AND nama = ?
        ORDER BY id ASC
        LIMIT 1
    """,
        (user_id, nama),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def ambil_semua_data_sideris(user_id):
    """Mengambil data pemeriksaan paling update dari setiap anak"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d1.nama, d1.tanggal_lahir, d1.jenis_kelamin, d1.tanggal_pemeriksaan, d1.usia_bulan,
               d1.berat_badan_lahir, d1.berat_badan, d1.tinggi_badan, d1.lingkar_kepala,
               d1.asi, d1.imunisasi, d1.asupan_gizi,
               d1.bb_u_zscore, d1.bb_u_status,
               d1.tb_u_zscore, d1.tb_u_status,
               d1.bb_tb_zscore, d1.bb_tb_status,
               d1.lk_u_zscore, d1.lk_u_status,
               d1.tingkat_risiko
        FROM data_sideris d1
        WHERE d1.id IN (
            SELECT MAX(id) FROM data_sideris WHERE user_id = ? GROUP BY nama
        )
        ORDER BY d1.id DESC
    """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def ambil_data_sideris_by_nama(user_id, nama):
    """Mengambil 1 data pemeriksaan terakhir untuk kurva/hasil"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM data_sideris 
        WHERE user_id = ? AND nama = ? AND tanggal_pemeriksaan IS NOT NULL
        ORDER BY id DESC LIMIT 1
    """,
        (user_id, nama),
    )
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "SELECT * FROM data_sideris WHERE user_id = ? AND nama = ? LIMIT 1",
            (user_id, nama),
        )
        row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def ambil_riwayat_pemeriksaan_by_nama(user_id, nama):
    """Mengambil seluruh histori pemeriksaan anak berurutan dari yang terbaru"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM data_sideris 
        WHERE user_id = ? AND nama = ? AND tanggal_pemeriksaan IS NOT NULL
        ORDER BY id DESC
    """,
        (user_id, nama),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_data_pemeriksaan(user_id, nama, data_medis):
    """Menyimpan data pemeriksaan (update baris pertama jika kosong, atau insert baris baru)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT tanggal_lahir, jenis_kelamin, tanggal_pemeriksaan FROM data_sideris WHERE user_id = ? AND nama = ? ORDER BY id ASC LIMIT 1",
            (user_id, nama),
        )
        bio = cursor.fetchone()
        tgl_lahir = bio["tanggal_lahir"] if bio else "-"
        jk = bio["jenis_kelamin"] if bio else "-"

        # Cek apakah pendaftaran balita ini belum pernah diisi pemeriksaan sama sekali
        cursor.execute(
            "SELECT id FROM data_sideris WHERE user_id = ? AND nama = ? AND tanggal_pemeriksaan IS NULL LIMIT 1",
            (user_id, nama),
        )
        kosong = cursor.fetchone()

        if kosong:
            sql = """
            UPDATE data_sideris 
            SET 
                tanggal_pemeriksaan = ?, usia_bulan = ?, berat_badan_lahir = ?,
                berat_badan = ?, tinggi_badan = ?, lingkar_kepala = ?, 
                asi = ?, imunisasi = ?, asupan_gizi = ?, 
                bb_u_zscore = ?, bb_u_status = ?, 
                tb_u_zscore = ?, tb_u_status = ?, 
                bb_tb_zscore = ?, bb_tb_status = ?, 
                lk_u_zscore = ?, lk_u_status = ?, 
                tingkat_risiko = ?
            WHERE id = ?
            """
            params = (
                data_medis["tanggal_pemeriksaan"],
                int(data_medis["usia_bulan"]),
                float(data_medis["berat_badan_lahir"]),
                float(data_medis["berat_badan"]),
                float(data_medis["tinggi_badan"]),
                float(data_medis["lingkar_kepala"]),
                data_medis["asi"],
                data_medis["imunisasi"],
                data_medis["asupan_gizi"],
                data_medis["zscore"].get("BB/U"),
                data_medis["status_text"].get("BB/U"),
                data_medis["zscore"].get("TB/U"),
                data_medis["status_text"].get("TB/U"),
                data_medis["zscore"].get("BB/TB"),
                data_medis["status_text"].get("BB/TB"),
                data_medis["zscore"].get("LK/U"),
                data_medis["status_text"].get("LK/U"),
                data_medis["tingkat_risiko"],
                kosong["id"],
            )
        else:
            sql = """
            INSERT INTO data_sideris (
                user_id, nama, tanggal_lahir, jenis_kelamin,
                tanggal_pemeriksaan, usia_bulan, berat_badan_lahir,
                berat_badan, tinggi_badan, lingkar_kepala,
                asi, imunisasi, asupan_gizi,
                bb_u_zscore, bb_u_status,
                tb_u_zscore, tb_u_status,
                bb_tb_zscore, bb_tb_status,
                lk_u_zscore, lk_u_status,
                tingkat_risiko
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                user_id,
                nama,
                tgl_lahir,
                jk,
                data_medis["tanggal_pemeriksaan"],
                int(data_medis["usia_bulan"]),
                float(data_medis["berat_badan_lahir"]),
                float(data_medis["berat_badan"]),
                float(data_medis["tinggi_badan"]),
                float(data_medis["lingkar_kepala"]),
                data_medis["asi"],
                data_medis["imunisasi"],
                data_medis["asupan_gizi"],
                data_medis["zscore"].get("BB/U"),
                data_medis["status_text"].get("BB/U"),
                data_medis["zscore"].get("TB/U"),
                data_medis["status_text"].get("TB/U"),
                data_medis["zscore"].get("BB/TB"),
                data_medis["status_text"].get("BB/TB"),
                data_medis["zscore"].get("LK/U"),
                data_medis["status_text"].get("LK/U"),
                data_medis["tingkat_risiko"],
            )

        cursor.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        print("Gagal menyimpan data pemeriksaan:", e)
        return False
    finally:
        conn.close()


# Inisialisasi dan migrasi otomatis saat modul ini dimuat
init_database()
migrasi_dan_hapus_unique_constraint()