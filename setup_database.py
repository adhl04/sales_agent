import sqlite3
import os

def setup_database():
    # Dapatkan path absolute dari folder saat ini
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, "database", "sales.db")
    
    print(f"Current directory: {current_dir}")
    print(f"Database path: {db_path}")
    
    # Buat folder database
    try:
        os.makedirs(os.path.join(current_dir, "database"), exist_ok=True)
        print("Folder database berhasil dibuat")
    except Exception as e:
        print(f"Folder sudah ada atau error: {e}")
    
    # Buat koneksi database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Koneksi database berhasil")
        
        # ============================================
        # DROP TABLES IF EXISTS (Untuk reset database)
        # ============================================
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS customers")
        print("✅ Tabel lama dihapus (jika ada)")
        
        # ============================================
        # BUAT TABEL products DENGAN SPESIFIKASI LENGKAP
        # ============================================
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                category TEXT,
                processor TEXT,
                ram TEXT,
                storage TEXT,
                screen_size TEXT,
                os TEXT,
                sensor TEXT,
                battery TEXT,
                connectivity TEXT
            )
        """)
        print("✅ Tabel products dibuat dengan kolom spesifikasi lengkap")
        
        # ============================================
        # BUAT TABEL customers
        # ============================================
        cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT
            )
        """)
        print("✅ Tabel customers dibuat")
        
        # ============================================
        # BUAT TABEL orders
        # ============================================
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                status TEXT DEFAULT 'pending_approval',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        print("✅ Tabel orders dibuat")
        
        # ============================================
        # INSERT SAMPLE PRODUCTS DENGAN SPESIFIKASI LENGKAP
        # ============================================
        products = [
            # Laptop Pro X1
            (
                'Laptop Pro X1',
                'Laptop premium dengan performa tinggi untuk profesional',
                15000000, 10, 'Laptop',
                'Intel Core i9-13900H (14 core, up to 5.4GHz)',
                '32GB DDR5 5600MHz',
                '1TB SSD NVMe PCIe Gen4',
                '16 inch OLED 4K (3840 x 2160), 120Hz',
                'Windows 11 Pro',
                'N/A',
                'Li-ion 90Wh (tahan 10 jam)',
                'WiFi 6E, Bluetooth 5.3, Thunderbolt 4'
            ),
            # Monitor Ultra HD 4K
            (
                'Monitor Ultra HD 4K',
                'Monitor 32 inch 4K dengan refresh rate 144Hz',
                8500000, 15, 'Monitor',
                'N/A',
                'N/A',
                'N/A',
                '32 inch 4K UHD (3840 x 2160), 144Hz, IPS Panel',
                'N/A',
                'N/A',
                'N/A',
                'N/A'
            ),
            # Keyboard Mechanical
            (
                'Keyboard Mechanical',
                'Keyboard mechanical dengan switch cherry mx blue',
                1250000, 30, 'Accessories',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'USB-C, Wireless 2.4GHz'
            ),
            # Mouse Wireless
            (
                'Mouse Wireless',
                'Mouse wireless dengan sensor 16000 DPI',
                750000, 25, 'Accessories',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'Sensor 16000 DPI, 1000Hz polling rate',
                'Battery 500mAh (3 bulan pemakaian)',
                '2.4GHz Wireless, Bluetooth 5.0'
            ),
            # SSD 1TB NVMe
            (
                'SSD 1TB NVMe',
                'SSD NVMe dengan kecepatan baca 7000 MB/s',
                2200000, 20, 'Storage',
                'N/A',
                'N/A',
                '1TB NVMe SSD PCIe Gen4, Read 7000MB/s, Write 5000MB/s',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A'
            ),
            # Webcam 4K
            (
                'Webcam 4K',
                'Webcam 4K dengan microphone built-in',
                3500000, 8, 'Accessories',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'USB-C, USB-A'
            )
        ]
        
        cursor.executemany("""
            INSERT INTO products 
            (name, description, price, stock, category, processor, ram, storage, screen_size, os, sensor, battery, connectivity) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
        print(f"✅ {len(products)} produk berhasil dimasukkan")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ Database berhasil dibuat dengan spesifikasi lengkap!")
        print(f"📁 File database: {db_path}")
        print("="*50)
        
        # Verifikasi
        verify_db(db_path)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def verify_db(db_path):
    """Verifikasi database telah terbuat"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek products
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\n📊 Products: {count} data")
        
        # Tampilkan produk dengan spesifikasi
        cursor.execute("""
            SELECT name, price, stock, processor, ram, storage, screen_size, sensor, battery, connectivity
            FROM products
        """)
        products = cursor.fetchall()
        
        print("\n📋 Daftar Produk dengan Spesifikasi:")
        print("-" * 70)
        for p in products:
            print(f"\n📦 {p[0]}")
            print(f"   💰 Rp{p[1]:,.0f} | 📊 Stok: {p[2]}")
            if p[3] and p[3] != 'N/A':
                print(f"   🔧 Processor: {p[3]}")
            if p[4] and p[4] != 'N/A':
                print(f"   💾 RAM: {p[4]}")
            if p[5] and p[5] != 'N/A':
                print(f"   💿 Storage: {p[5]}")
            if p[6] and p[6] != 'N/A':
                print(f"   🖥️ Layar: {p[6]}")
            if p[7] and p[7] != 'N/A':
                print(f"   📡 Sensor: {p[7]}")
            if p[8] and p[8] != 'N/A':
                print(f"   🔋 Baterai: {p[8]}")
            if p[9] and p[9] != 'N/A':
                print(f"   📶 Konektivitas: {p[9]}")
        
        conn.close()
        print("\n✅ Verifikasi berhasil!")
    except Exception as e:
        print(f"❌ Verifikasi error: {e}")

if __name__ == "__main__":
    setup_database()