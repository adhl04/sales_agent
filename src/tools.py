from langchain.tools import tool
from src.database import Database
from typing import Optional

db = Database()

# ============================================
# FUNGSI TOOLS (BISA DIPANGGIL LANGSUNG)
# ============================================

def list_available_products() -> str:
    """Menampilkan semua produk yang tersedia."""
    products = db.get_all_products()
    if not products:
        return "Maaf, tidak ada produk yang tersedia saat ini."
    
    result = "🛍️ Produk yang tersedia:\n\n"
    for p in products:
        result += f"• {p['name']} - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
    return result

# ============================================
# FUNGSI FILTER PRODUK
# ============================================

def filter_products_by_category(category: str) -> str:
    """Menampilkan produk berdasarkan kategori tertentu."""
    products = db.get_all_products()
    filtered = [p for p in products if p['category'].lower() == category.lower()]
    
    if not filtered:
        return f"Maaf, tidak ada produk dengan kategori '{category}'."
    
    result = f"🛍️ Produk dengan kategori '{category}':\n\n"
    for p in filtered:
        result += f"• {p['name']} - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
    return result

def filter_products_by_name_keyword(keyword: str) -> str:
    """Menampilkan produk yang mengandung kata kunci tertentu."""
    products = db.get_all_products()
    filtered = [p for p in products if keyword.lower() in p['name'].lower()]
    
    if not filtered:
        return f"Produk dengan kata kunci '{keyword}' tidak ditemukan."
    
    result = f"🛍️ Produk dengan kata kunci '{keyword}':\n\n"
    for p in filtered:
        result += f"• {p['name']} - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
    return result

# ============================================
# FUNGSI SPESIFIKASI PRODUK
# ============================================

def get_product_info(product_name: str) -> str:
    """Mencari informasi produk berdasarkan nama."""
    product = db.get_product_by_name(product_name)
    if not product:
        return f"Produk dengan nama '{product_name}' tidak ditemukan."
    
    return f"""
    📦 {product['name']}
    📝 {product['description']}
    💰 Harga: Rp{product['price']:,.0f}
    📊 Stok: {product['stock']} unit
    🏷️ Kategori: {product['category']}
    """

def get_product_specs(product_name: str) -> str:
    """Mendapatkan spesifikasi teknis produk (RAM, SSD, layar, dll)."""
    product = db.get_product_by_name(product_name)
    if not product:
        return f"Produk '{product_name}' tidak ditemukan."
    
    spec_fields = {
        'processor': 'Processor',
        'ram': 'RAM',
        'storage': 'Storage',
        'screen_size': 'Layar',
        'os': 'OS',
        'sensor': 'Sensor',
        'battery': 'Baterai',
        'connectivity': 'Konektivitas'
    }
    
    result = f"🔧 Spesifikasi {product['name']}:\n"
    has_spec = False
    
    for field, label in spec_fields.items():
        value = product.get(field, 'Tidak tersedia')
        if value and value != 'Tidak tersedia' and value != 'N/A':
            result += f"• {label}: {value}\n"
            has_spec = True
    
    if not has_spec:
        return f"ℹ️ Tidak ada spesifikasi yang tersedia untuk {product['name']}."
    
    return result

def get_product_specs_detail(product_name: str, spec_type: str = None) -> str:
    """Mendapatkan spesifikasi detail produk berdasarkan jenis spesifikasi."""
    product = db.get_product_by_name(product_name)
    if not product:
        return f"Produk '{product_name}' tidak ditemukan."
    
    spec_mapping = {
        'sensor': ('sensor', 'Sensor'),
        'battery': ('battery', 'Baterai'),
        'baterai': ('battery', 'Baterai'),
        'connectivity': ('connectivity', 'Konektivitas'),
        'koneksi': ('connectivity', 'Konektivitas'),
        'processor': ('processor', 'Processor'),
        'prosesor': ('processor', 'Processor'),
        'ram': ('ram', 'RAM'),
        'storage': ('storage', 'Storage'),
        'ssd': ('storage', 'Storage'),
        'layar': ('screen_size', 'Layar'),
        'screen': ('screen_size', 'Layar'),
        'inch': ('screen_size', 'Layar'),
        'os': ('os', 'OS')
    }
    
    if spec_type and spec_type in spec_mapping:
        column, label = spec_mapping[spec_type]
        value = product.get(column, 'Tidak tersedia')
        
        if not value or value == 'N/A' or value == 'Tidak tersedia':
            return f"ℹ️ Informasi {label} untuk {product['name']} tidak tersedia di database."
        
        return f"🔧 {label} {product['name']}: {value}"
    
    return get_product_specs(product_name)

# ============================================
# FUNGSI DETAIL PRODUK LENGKAP
# ============================================

def get_product_full_details(product_name: str) -> str:
    """Mendapatkan detail lengkap produk (termasuk spesifikasi)."""
    product = db.get_product_by_name(product_name)
    if not product:
        return f"Produk '{product_name}' tidak ditemukan."
    
    specs = {
        'processor': product.get('processor', 'Tidak tersedia'),
        'ram': product.get('ram', 'Tidak tersedia'),
        'storage': product.get('storage', 'Tidak tersedia'),
        'screen_size': product.get('screen_size', 'Tidak tersedia'),
        'os': product.get('os', 'Tidak tersedia'),
        'sensor': product.get('sensor', 'Tidak tersedia'),
        'battery': product.get('battery', 'Tidak tersedia'),
        'connectivity': product.get('connectivity', 'Tidak tersedia')
    }
    
    result = f"""
📦 **{product['name']}**
📝 {product['description']}
💰 **Harga:** Rp{product['price']:,.0f}
📊 **Stok:** {product['stock']} unit
🏷️ **Kategori:** {product['category']}
"""
    
    spec_labels = {
        'processor': '🔧 Processor',
        'ram': '💾 RAM',
        'storage': '💿 Storage',
        'screen_size': '🖥️ Layar',
        'os': '⚙️ OS',
        'sensor': '📡 Sensor',
        'battery': '🔋 Baterai',
        'connectivity': '📶 Konektivitas'
    }
    
    has_spec = False
    for field, label in spec_labels.items():
        value = specs.get(field)
        if value and value != 'Tidak tersedia' and value != 'N/A':
            result += f"{label}: {value}\n"
            has_spec = True
    
    return result

# ============================================
# FUNGSI ORDER DAN STATUS
# ============================================

def create_order(product_name: str, quantity: int, customer_name: str, customer_email: Optional[str] = None) -> str:
    """Membuat pesanan baru."""
    product = db.get_product_by_name(product_name)
    if not product:
        return f"Produk '{product_name}' tidak ditemukan."
    
    if product['stock'] < quantity:
        return f"Stok tidak mencukupi. Tersedia: {product['stock']} unit."
    
    total_price = product['price'] * quantity
    customer_id = db.get_or_create_customer(customer_name, customer_email)
    order_id = db.create_order(customer_id, product['id'], quantity, total_price)
    
    return f"""
🛒 ORDER #{order_id} - MENUNGGU PERSETUJUAN

📋 Detail Pesanan:
• Produk: {product['name']}
• Jumlah: {quantity} unit
• Total: Rp{total_price:,.0f}
• Customer: {customer_name}

⚠️ Pesanan ini memerlukan approval sebelum dieksekusi.
Ketik 'approve' untuk menyetujui atau 'reject' untuk membatalkan.
"""

def check_order_status(order_id: int) -> str:
    """Mengecek status pesanan dengan detail lengkap dan respons natural."""
    order = db.get_order(order_id)
    if not order:
        return f"❌ Order #{order_id} tidak ditemukan."
    
    status_emoji = {
        'pending_approval': '⏳',
        'approved': '✅',
        'rejected': '❌',
        'processing': '🔄',
        'shipped': '🚚',
        'delivered': '📦'
    }
    
    emoji = status_emoji.get(order['status'], '❓')
    status_text = order['status'].replace('_', ' ').upper()
    
    product_name = order['product_name']
    product = db.get_product_by_name(product_name)
    
    result = f"""
📋 **Ini pesanan Anda:**

{emoji} **ORDER #{order_id}** - *{status_text}*
"""
    
    if product:
        result += f"""
📦 **Produk:** {product['name']}
📝 {product['description']}
💰 **Harga:** Rp{product['price']:,.0f}
🏷️ **Kategori:** {product['category']}
"""
        
        specs = {
            'processor': product.get('processor', 'Tidak tersedia'),
            'ram': product.get('ram', 'Tidak tersedia'),
            'storage': product.get('storage', 'Tidak tersedia'),
            'screen_size': product.get('screen_size', 'Tidak tersedia'),
            'os': product.get('os', 'Tidak tersedia'),
            'sensor': product.get('sensor', 'Tidak tersedia'),
            'battery': product.get('battery', 'Tidak tersedia'),
            'connectivity': product.get('connectivity', 'Tidak tersedia')
        }
        
        spec_labels = {
            'processor': '🔧 Processor',
            'ram': '💾 RAM',
            'storage': '💿 Storage',
            'screen_size': '🖥️ Layar',
            'os': '⚙️ OS',
            'sensor': '📡 Sensor',
            'battery': '🔋 Baterai',
            'connectivity': '📶 Konektivitas'
        }
        
        for field, label in spec_labels.items():
            value = specs.get(field)
            if value and value != 'Tidak tersedia' and value != 'N/A':
                result += f"{label}: {value}\n"
    
    result += f"""
📦 **Jumlah:** {order['quantity']} unit
💰 **Total:** Rp{order['total_price']:,.0f}
📅 **Tanggal Pemesanan:** {order['created_at']}

Terima kasih telah berbelanja di TechSolutions! 😊
"""
    
    return result

def get_recommendations(customer_name: str) -> str:
    """Memberikan rekomendasi produk berdasarkan riwayat pembelian."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE name LIKE ?", (f"%{customer_name}%",))
        row = cursor.fetchone()
        
        if not row:
            return f"Customer '{customer_name}' tidak ditemukan. Berikut produk populer kami:\n{list_available_products()}"
        
        customer_id = row['id']
        orders = db.get_customer_orders(customer_id)
        
        if not orders:
            return f"{customer_name} belum memiliki riwayat pembelian. Berikut produk populer kami:\n{list_available_products()}"
        
        categories = []
        for order in orders[:5]:
            product = db.get_product(order['product_id'])
            if product and product['category']:
                categories.append(product['category'])
        
        if not categories:
            return "Rekomendasi berdasarkan pembelian terbaru: coba cek produk di kategori yang sama!"
        
        most_common_category = max(set(categories), key=categories.count)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products 
                WHERE category = ? AND stock > 0
                LIMIT 3
            """, (most_common_category,))
            recs = cursor.fetchall()
        
        if not recs:
            return f"Tidak ada produk di kategori {most_common_category}."
        
        result = f"🎯 Rekomendasi untuk {customer_name} (berdasarkan kategori '{most_common_category}'):\n\n"
        for p in recs:
            result += f"• {p['name']} - Rp{p['price']:,.0f}\n"
        
        return result

# ============================================
# TOOLS LANGSMITH (UNTUK AGENT)
# ============================================
@tool
def list_available_products_tool() -> str:
    """Menampilkan semua produk yang tersedia."""
    return list_available_products()

@tool
def filter_products_by_category_tool(category: str) -> str:
    """Menampilkan produk berdasarkan kategori (laptop, monitor, accessories, storage)."""
    return filter_products_by_category(category)

@tool
def filter_products_by_name_keyword_tool(keyword: str) -> str:
    """Menampilkan produk berdasarkan kata kunci nama."""
    return filter_products_by_name_keyword(keyword)

@tool
def get_product_info_tool(product_name: str) -> str:
    """Mencari informasi produk berdasarkan nama."""
    return get_product_info(product_name)

@tool
def get_product_specs_tool(product_name: str) -> str:
    """Mendapatkan spesifikasi teknis produk (RAM, SSD, layar, processor, OS)."""
    return get_product_specs(product_name)

@tool
def create_order_tool(product_name: str, quantity: int, customer_name: str, customer_email: Optional[str] = None) -> str:
    """Membuat pesanan baru."""
    return create_order(product_name, quantity, customer_name, customer_email)

@tool
def check_order_status_tool(order_id: int) -> str:
    """Mengecek status pesanan."""
    return check_order_status(order_id)

@tool
def get_recommendations_tool(customer_name: str) -> str:
    """Memberikan rekomendasi produk."""
    return get_recommendations(customer_name)