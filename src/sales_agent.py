# ============================================
# IMPORT
# ============================================
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langsmith import Client, traceable
from src.config import Config
from src.tools import (
    get_product_info,
    list_available_products,
    check_order_status,
    get_recommendations,
    get_product_specs,
    get_product_specs_detail,
    filter_products_by_category,
    filter_products_by_name_keyword,
    get_product_full_details
)
from src.database import Database
import os
import re
from datetime import datetime

class SalesAgent:
    def __init__(self):
        self.config = Config()
        
        # ============================================
        # OLLAMA VIA OPENAI-COMPATIBLE API
        # ============================================
        self.llm = ChatOpenAI(
            model=self.config.OLLAMA_MODEL,
            temperature=self.config.TEMPERATURE,
            base_url=self.config.OLLAMA_BASE_URL,
            api_key=self.config.OLLAMA_API_KEY,
        )
        # ============================================
        
        # LangSmith Client
        self.langsmith_client = None
        if self.config.LANGSMITH_API_KEY:
            try:
                self.langsmith_client = Client(
                    api_key=self.config.LANGSMITH_API_KEY
                )
                print(f"✅ LangSmith Client initialized: {self.config.LANGSMITH_PROJECT}")
            except Exception as e:
                print(f"⚠️ LangSmith init error: {e}")
        
        self.conversation_history = ""
        self._pending_order = None
        
        # ============================================
        # INISIALISASI DATABASE
        # ============================================
        self.db = Database()
        # ============================================
    
    @traceable(name="process_with_tools", project_name="sales-agent-project")
    def process_with_tools(self, user_input: str) -> str:
        """Main entry point - proses semua query"""
        user_input = user_input.strip()
        
        if self.langsmith_client:
            try:
                self.langsmith_client.create_run(
                    name="process_with_tools",
                    run_type="chain",
                    inputs={"user_input": user_input},
                    project_name=self.config.LANGSMITH_PROJECT
                )
            except Exception as e:
                print(f"LangSmith log error: {e}")
        
        return self._process(user_input)
    
    def _extract_product_name(self, user_input_lower: str) -> str:
        """Ekstrak nama produk dari input user."""
        all_products = self.db.get_all_products()
        
        for p in all_products:
            if p['name'].lower() in user_input_lower:
                return p['name']
            
            product_keywords = p['name'].lower().split()
            for keyword in product_keywords:
                if keyword in user_input_lower and len(keyword) > 2:
                    return p['name']
        
        return None
    
    # ============================================
    # DETEKSI GREETING DINAMIS
    # ============================================
    def _detect_greeting(self, user_input_lower: str) -> str:
        """Deteksi greeting dan kembalikan balasan yang sesuai."""
        greetings = {
            'selamat pagi': 'Selamat pagi! 🌅',
            'selamat siang': 'Selamat siang! ☀️',
            'selamat sore': 'Selamat sore! 🌤️',
            'selamat malam': 'Selamat malam! 🌙',
            'pagi': 'Selamat pagi! 🌅',
            'siang': 'Selamat siang! ☀️',
            'sore': 'Selamat sore! 🌤️',
            'malam': 'Selamat malam! 🌙'
        }
        
        for keyword, response in greetings.items():
            if keyword in user_input_lower:
                return f"{response} Ada yang bisa saya bantu? Saya {self.config.SALESPERSON_NAME} dari {self.config.COMPANY_NAME}."
        
        return None
    
    # ============================================
    # GENERATE NATURAL RESPONSE
    # ============================================
    def _generate_natural_response(self, user_input: str, response: str, intent: str = None) -> str:
        """Generate respons yang lebih natural."""
        
        if response and "🛍️" not in response and "📋" not in response:
            return response
        
        user_input_lower = user_input.lower()
        
        # RESPON UNTUK PERTANYAAN KATEGORI PRODUK
        category_keywords = {
            "laptop": "Laptop",
            "monitor": "Monitor",
            "aksesoris": "Accessories",
            "accessories": "Accessories",
            "storage": "Storage",
            "ssd": "Storage"
        }
        
        detected_category = None
        for keyword, category in category_keywords.items():
            if keyword in user_input_lower:
                detected_category = category
                break
        
        if detected_category:
            products = self.db.get_all_products()
            filtered = [p for p in products if p['category'].lower() == detected_category.lower()]
            
            if filtered:
                result = f"Tentu! Untuk **{detected_category}**, kami memiliki beberapa pilihan produk:\n\n"
                for p in filtered:
                    result += f"• **{p['name']}** - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
                result += "\nApakah Anda ingin melihat spesifikasi atau harga dari salah satu produk? 😊"
                return result
        
        # RESPON UNTUK PERTANYAAN "tentang" PRODUK
        if "tentang" in user_input_lower:
            product_name = self._extract_product_name(user_input_lower)
            if product_name:
                product = self.db.get_product_by_name(product_name)
                return f"Tentu! **{product['name']}** adalah salah satu produk kami. Berikut detailnya:\n\n• Harga: Rp{product['price']:,.0f}\n• Stok: {product['stock']} unit\n• Kategori: {product['category']}\n\nApakah Anda ingin melihat spesifikasi atau membuat pesanan? 😊"
            
            return "Tentu, saya bisa bantu informasi produk. Produk apa yang ingin Anda ketahui? Saya bisa memberikan informasi tentang Laptop, Monitor, atau Aksesoris. 😊"
        
        # RESPON UNTUK PRODUK SPESIFIK
        product_name = self._extract_product_name(user_input_lower)
        if product_name:
            product = self.db.get_product_by_name(product_name)
            return f"Tentu! **{product['name']}** adalah salah satu produk kami. Berikut detailnya:\n\n• Harga: Rp{product['price']:,.0f}\n• Stok: {product['stock']} unit\n• Kategori: {product['category']}\n\nApakah Anda ingin melihat spesifikasi atau membuat pesanan? 😊"
        
        return response
    
    # ============================================
    # GET CURRENT DATETIME
    # ============================================
    def _get_current_datetime(self) -> str:
        """Mendapatkan tanggal dan waktu saat ini dalam format yang rapi."""
        now = datetime.now()
        return now.strftime("%d %B %Y, %H:%M:%S")
    
    def _process(self, user_input: str) -> str:
        """Proses query dengan rule-based"""
        user_input_lower = user_input.lower().strip()
        
        # ============================================
        # 1. CEK APPROVAL / REJECT
        # ============================================
        if user_input_lower in ["approve", "setuju", "ya", "ok", "okey"]:
            return self._handle_approve()
        
        if user_input_lower in ["reject", "tolak", "tidak", "no", "batal"]:
            return self._handle_reject()
        
        # ============================================
        # 2. CEK STATUS ORDER (PRIORITAS UTAMA!)
        # ============================================
        if ("order #" in user_input_lower or 
            ("cek" in user_input_lower and "order" in user_input_lower) or
            ("status" in user_input_lower and "order" in user_input_lower)):
            match = re.search(r"#(\d+)", user_input)
            if match:
                return check_order_status(int(match.group(1)))
            match = re.search(r"order\s*#?\s*(\d+)", user_input_lower)
            if match:
                return check_order_status(int(match.group(1)))
            return "Untuk cek status, ketik: 'cek status order #123' atau 'order #123'"
        
        # ============================================
        # 3. CEK HARGA PRODUK
        # ============================================
        if any(kw in user_input_lower for kw in ["harga", "berapa"]):
            product_name = self._extract_product_name(user_input_lower)
            
            if product_name:
                product = self.db.get_product_by_name(product_name)
                return f"Tentu! Harga **{product['name']}** adalah Rp{product['price']:,.0f}. Apakah ada produk lain yang ingin Anda ketahui harganya? 😊"
            else:
                return "Tentu, saya bisa bantu cek harga produk. Produk apa yang ingin Anda ketahui harganya? 😊"
        
        # ============================================
        # 4. CEK SPESIFIKASI PRODUK
        # ============================================
        specs_keywords = [
            "sensor", "battery", "baterai", "connectivity", "koneksi",
            "processor", "prosesor", "ram", "storage", "ssd", 
            "layar", "screen", "spesifikasi", "spec"
        ]
        
        is_specs_query = any(kw in user_input_lower for kw in specs_keywords)
        
        if is_specs_query:
            product_name = self._extract_product_name(user_input_lower)
            
            if product_name:
                spec_type = None
                for kw in specs_keywords:
                    if kw in user_input_lower:
                        spec_type = kw
                        break
                
                if spec_type in ["spesifikasi", "spec"]:
                    specs = get_product_specs(product_name)
                    return f"Tentu, berikut spesifikasi untuk **{product_name}**:\n\n{specs}"
                else:
                    result = get_product_specs_detail(product_name, spec_type)
                    if "tidak tersedia" in result.lower():
                        return f"ℹ️ Informasi {spec_type.upper()} untuk {product_name} tidak tersedia di database."
                    return f"Tentu, berikut informasi **{spec_type.upper()}** untuk **{product_name}**:\n\n{result}"
            else:
                return "Tentu, saya bisa bantu lihat spesifikasi produk. Produk apa yang ingin Anda lihat spesifikasinya? 😊"
        
        # ============================================
        # 5. CEK ORDER (HANYA jika tidak ada "#")
        # ============================================
        if any(kw in user_input_lower for kw in ["beli", "pesan", "mau"]) or (
            "order" in user_input_lower and "#" not in user_input_lower
        ):
            return self._handle_order(user_input)
        
        # ============================================
        # 6. CEK PERTANYAAN TENTANG PRODUK (NATURAL)
        # ============================================
        if "tentang" in user_input_lower or "produk" in user_input_lower:
            if "laptop" in user_input_lower:
                category = "Laptop"
            elif "monitor" in user_input_lower:
                category = "Monitor"
            elif "aksesoris" in user_input_lower or "accessories" in user_input_lower:
                category = "Accessories"
            elif "storage" in user_input_lower or "ssd" in user_input_lower:
                category = "Storage"
            else:
                product_name = self._extract_product_name(user_input_lower)
                if product_name:
                    product = self.db.get_product_by_name(product_name)
                    return f"Tentu! **{product['name']}** adalah salah satu produk kami. Berikut detailnya:\n\n• Harga: Rp{product['price']:,.0f}\n• Stok: {product['stock']} unit\n• Kategori: {product['category']}\n\nApakah Anda ingin melihat spesifikasi atau membuat pesanan? 😊"
                return "Tentu, saya bisa bantu informasi produk. Produk apa yang ingin Anda ketahui? 😊"
            
            products = self.db.get_all_products()
            filtered = [p for p in products if p['category'].lower() == category.lower()]
            
            if filtered:
                result = f"Tentu! Untuk **{category}**, kami memiliki beberapa pilihan produk:\n\n"
                for p in filtered:
                    result += f"• **{p['name']}** - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
                result += "\nApakah Anda ingin melihat spesifikasi atau harga dari salah satu produk? 😊"
                return result
            else:
                return f"Maaf, untuk **{category}** tidak ada produk yang tersedia saat ini. Apakah ada produk lain yang ingin Anda ketahui? 😊"
        
        # ============================================
        # 7. FILTER BERDASARKAN KATEGORI
        # ============================================
        category_keywords = {
            "laptop": "Laptop",
            "monitor": "Monitor",
            "aksesoris": "Accessories",
            "accessories": "Accessories",
            "storage": "Storage",
            "ssd": "Storage"
        }
        
        detected_category = None
        for keyword, category in category_keywords.items():
            if keyword in user_input_lower:
                detected_category = category
                break
        
        if detected_category:
            products = self.db.get_all_products()
            filtered = [p for p in products if p['category'].lower() == detected_category.lower()]
            
            if filtered:
                result = f"Tentu! Untuk **{detected_category}**, kami memiliki beberapa pilihan produk:\n\n"
                for p in filtered:
                    result += f"• **{p['name']}** - Rp{p['price']:,.0f} (Stok: {p['stock']})\n"
                result += "\nApakah Anda ingin melihat spesifikasi atau harga dari salah satu produk? 😊"
                return result
            else:
                return f"Maaf, untuk varian **{detected_category}** tidak ada produk yang tersedia saat ini."
        
        # ============================================
        # 8. TAMPILKAN PRODUK (SEMUA)
        # ============================================
        if any(kw in user_input_lower for kw in ["produk", "daftar", "list", "tampilkan"]):
            return list_available_products()
        
        # ============================================
        # 9. CEK STOK
        # ============================================
        if "stok" in user_input_lower:
            match = re.search(r"stok\s*(.+)", user_input_lower)
            if match:
                return get_product_info(match.group(1).strip())
            return "Untuk cek stok, ketik: 'cek stok [nama produk]'"
        
        # ============================================
        # 10. REKOMENDASI
        # ============================================
        if any(kw in user_input_lower for kw in ["rekomendasi", "saran"]):
            return get_recommendations("Customer")
        
        # ============================================
        # 11. GREETING - DINAMIS + LLM FALLBACK
        # ============================================
        greeting_keywords = ["halo", "hai", "hello", "assalamualaikum", 
                             "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
                             "pagi", "siang", "sore", "malam"]
        
        if any(kw in user_input_lower for kw in greeting_keywords):
            dynamic_greeting = self._detect_greeting(user_input_lower)
            if dynamic_greeting:
                return dynamic_greeting
            return self._generate_greeting(user_input)
        
        # ============================================
        # 12. DEFAULT - PAKAI LLM
        # ============================================
        return self._generate_response(user_input)
    
    def _generate_greeting(self, user_input: str) -> str:
        """Generate greeting menggunakan LLM"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""Anda adalah {self.config.SALESPERSON_NAME}, Sales Representative dari {self.config.COMPANY_NAME}.
                Balas sapaan user dengan ramah dalam Bahasa Indonesia.
                Perkenalkan diri Anda dan tawarkan bantuan."""),
                ("human", user_input)
            ])
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({})
        except Exception as e:
            print(f"LLM error: {e}")
            return f"Halo! Saya {self.config.SALESPERSON_NAME} dari {self.config.COMPANY_NAME}. Ada yang bisa saya bantu?"
    
    def _generate_response(self, user_input: str) -> str:
        """Generate response menggunakan LLM"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""Anda adalah {self.config.SALESPERSON_NAME}, Sales Representative dari {self.config.COMPANY_NAME}.
                {self.config.COMPANY_NAME} bergerak di bidang {self.config.COMPANY_BUSINESS}.
                Balas pertanyaan user dengan ramah dan informatif dalam Bahasa Indonesia.
                Jika user menanyakan produk, arahkan untuk menggunakan perintah yang tersedia.
                
                Perintah yang tersedia:
                - 'tampilkan produk' - Lihat semua produk
                - 'cek stok [nama produk]' - Cek stok produk
                - 'saya mau beli [produk] [jumlah] unit' - Buat pesanan
                - 'cek status order #123' - Cek status pesanan
                - 'rekomendasi produk' - Dapatkan rekomendasi
                - 'spesifikasi [produk]' - Lihat spesifikasi teknis produk"""),
                ("human", user_input)
            ])
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({})
        except Exception as e:
            print(f"LLM error: {e}")
            return f"""
            Saya {self.config.SALESPERSON_NAME} dari {self.config.COMPANY_NAME}.
            
            Saya bisa membantu Anda dengan:
            • 📋 'tampilkan produk' - Lihat semua produk
            • 📦 'cek stok [nama produk]' - Cek stok produk
            • 🛒 'saya mau beli [produk] [jumlah] unit' - Buat pesanan
            • 📊 'cek status order #123' - Cek status pesanan
            • 🎯 'rekomendasi produk' - Dapatkan rekomendasi
            • 🔧 'spesifikasi [produk]' - Lihat spesifikasi teknis
            
            Ada yang bisa saya bantu?
            """
    
    # ============================================
    # HANDLE ORDER - DENGAN RESPON NATURAL
    # ============================================
    def _handle_order(self, user_input: str) -> str:
        """Handle pembuatan order dengan respons natural"""
        if self._pending_order:
            return f"""
            ⚠️ Masih ada order yang menunggu persetujuan:
            • Produk: {self._pending_order['product_name']}
            • Jumlah: {self._pending_order['quantity']} unit
            • Total: Rp{self._pending_order['total_price']:,.0f}
            
            Ketik **'approve'** untuk menyetujui atau **'reject'** untuk membatalkan.
            """
        
        qty_match = re.search(r"(\d+)\s*(unit|pcs|buah|item)", user_input.lower())
        quantity = int(qty_match.group(1)) if qty_match else 1
        
        product_name = self._extract_product_name(user_input.lower())
        
        if not product_name:
            return "Produk apa yang ingin Anda pesan? Sebutkan nama produknya. Contoh: 'saya mau beli Laptop Pro X1 2 unit'"
        
        product = self.db.get_product_by_name(product_name)
        if not product:
            return f"Produk '{product_name}' tidak ditemukan."
        if product['stock'] < quantity:
            return f"Stok tidak mencukupi. Tersedia: {product['stock']} unit."
        
        total_price = product['price'] * quantity
        customer_id = self.db.get_or_create_customer("Customer")
        order_id = self.db.create_order(customer_id, product['id'], quantity, total_price)
        
        product_details = get_product_full_details(product_name)
        
        self._pending_order = {
            "order_id": order_id,
            "product_name": product_name,
            "quantity": quantity,
            "total_price": total_price
        }
        
        return f"""
🛒 **Baik, kami akan memproses pesanan Anda!**

📋 **Detail Pesanan:**
{product_details}

📦 **Jumlah:** {quantity} unit
💰 **Total:** Rp{total_price:,.0f}
👤 **Customer:** Customer
📅 **Tanggal Pemesanan:** {self._get_current_datetime()}

⚠️ Pesanan ini memerlukan **approval** sebelum dieksekusi.
Ketik **'approve'** untuk menyetujui atau **'reject'** untuk membatalkan.
"""
    
    # ============================================
    # HANDLE APPROVE - DENGAN RESPON NATURAL
    # ============================================
    def _handle_approve(self) -> str:
        """Handle approval order dengan respons natural"""
        if not self._pending_order:
            return "Tidak ada order yang menunggu persetujuan."
        
        order_id = self._pending_order["order_id"]
        product_name = self._pending_order["product_name"]
        quantity = self._pending_order["quantity"]
        total_price = self._pending_order["total_price"]
        
        self.db.update_order_status(order_id, "approved")
        self._pending_order = None
        
        product_details = get_product_full_details(product_name)
        
        return f"""
🎉 **Selamat! Pesanan Anda berhasil dibeli!**

✅ Pesanan Anda sedang kami proses dan akan segera dibuat.

📋 **Detail Pesanan:**
{product_details}

📦 **Jumlah:** {quantity} unit
💰 **Total:** Rp{total_price:,.0f}
📊 **Status:** Processing
📅 **Tanggal Pemesanan:** {self._get_current_datetime()}

Terima kasih telah berbelanja di {self.config.COMPANY_NAME}! 😊
"""
    
    def _handle_reject(self) -> str:
        """Handle reject order"""
        if not self._pending_order:
            return "Tidak ada order yang menunggu persetujuan."
        
        order_id = self._pending_order["order_id"]
        self.db.update_order_status(order_id, "rejected")
        self._pending_order = None
        
        return f"❌ ORDER #{order_id} DIBATALKAN."