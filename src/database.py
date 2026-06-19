import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
from src.config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Inisialisasi tabel jika belum ada"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabel Products dengan spesifikasi lengkap
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
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
            
            # Tabel Customers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT
                )
            """)
            
            # Tabel Orders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
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
            
            conn.commit()
            self._seed_data()
    
    def _seed_data(self):
        """Isi data dummy produk dengan spesifikasi lengkap"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            
            if count == 0:
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
                conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_product_by_name(self, name: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE ?", (f"%{name.lower()}%",))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_products(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE stock > 0")
            return [dict(row) for row in cursor.fetchall()]
    
    def create_order(self, customer_id: int, product_id: int, quantity: int, total_price: float) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (customer_id, product_id, quantity, total_price, status)
                VALUES (?, ?, ?, ?, 'pending_approval')
            """, (customer_id, product_id, quantity, total_price))
            conn.commit()
            return cursor.lastrowid
    
    def get_order(self, order_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, p.name as product_name, c.name as customer_name 
                FROM orders o
                JOIN products p ON o.product_id = p.id
                JOIN customers c ON o.customer_id = c.id
                WHERE o.id = ?
            """, (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_customer_orders(self, customer_id: int) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, p.name as product_name 
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.customer_id = ?
                ORDER BY o.created_at DESC
            """, (customer_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_or_create_customer(self, name: str, email: str = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if email:
                cursor.execute("SELECT id FROM customers WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    return row['id']
            
            cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            return cursor.lastrowid