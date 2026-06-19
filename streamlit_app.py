import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from src.graph_workflow import SalesGraphWorkflow
from src.database import Database

st.set_page_config(
    page_title="Virtual Sales Agent",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
def apply_custom_css():
    st.markdown("""
    <style>
    /* ========================================
       GLOBAL STYLING
    ======================================== */
    .main {
        background: linear-gradient(135deg, #0F0A1A 0%, #1A1430 50%, #0F0A1A 100%);
    }
    
    /* ========================================
       SIDEBAR STYLING
    ======================================== */
    .css-1d391kg, .st-emotion-cache-1d391kg {
        background: linear-gradient(180deg, #0F0A1A 0%, #1A1430 100%) !important;
        border-right: 1px solid rgba(124, 58, 237, 0.3) !important;
    }
    
    .css-1d391kg .st-emotion-cache-1v0mbdj, 
    .st-emotion-cache-1v0mbdj {
        color: #C4B5FD !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #A78BFA !important;
    }
    
    .st-emotion-cache-1r6slb0 {
        background: linear-gradient(90deg, transparent, #7C3AED, transparent) !important;
        height: 1px !important;
    }
    
    /* ========================================
       CHAT BUBBLE STYLING
    ======================================== */
    [data-testid="stChatMessage"]:nth-child(odd) .st-emotion-cache-1c7y2kd {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        border-radius: 20px 20px 5px 20px !important;
        padding: 12px 18px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    
    [data-testid="stChatMessage"]:nth-child(even) .st-emotion-cache-1c7y2kd {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px 20px 20px 5px !important;
        padding: 12px 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        color: #F5F3FF !important;
    }
    
    .stChatMessage {
        margin-bottom: 8px !important;
    }
    
    /* ========================================
       BUTTON STYLING
    ======================================== */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5) !important;
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
    }
    
    .stButton > button:has(> div:contains("Reset")) {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }
    
    .stButton > button:has(> div:contains("Reset")):hover {
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5) !important;
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%) !important;
    }
    
    /* ========================================
       INPUT BOX STYLING
    ======================================== */
    .stChatInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(124, 58, 237, 0.3) !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        color: #F5F3FF !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput input:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.2) !important;
        outline: none !important;
    }
    
    .stChatInput input::placeholder {
        color: #6B7280 !important;
    }
    
    /* ========================================
       EXPANDER STYLING
    ======================================== */
    .streamlit-expanderHeader {
        background: rgba(124, 58, 237, 0.1) !important;
        border-radius: 10px !important;
        color: #A78BFA !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid rgba(124, 58, 237, 0.1) !important;
        border-top: none !important;
    }
    
    /* ========================================
       METRIC CARDS
    ======================================== */
    [data-testid="stMetricValue"] {
        color: #A78BFA !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #C4B5FD !important;
    }
    
    /* ========================================
       SCROLLBAR
    ======================================== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0F0A1A !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #7C3AED !important;
        border-radius: 10px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6D28D9 !important;
    }
    
    /* ========================================
       TITLE & HEADER
    ======================================== */
    h1, h2, h3 {
        color: #F5F3FF !important;
    }
    
    .st-emotion-cache-1v0mbdj {
        color: #C4B5FD !important;
    }
    
    .st-emotion-cache-1r4qj8v {
        color: #9CA3AF !important;
    }
    
    /* ========================================
       PRODUCT CARD
    ======================================== */
    .product-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin: 6px 0 !important;
        border-left: 3px solid #7C3AED !important;
        transition: all 0.3s ease !important;
    }
    
    .product-card:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateX(5px) !important;
    }
    
    .product-card .product-name {
        color: #F5F3FF !important;
        font-weight: 600 !important;
    }
    
    .product-card .product-detail {
        color: #C4B5FD !important;
        font-size: 0.9em !important;
    }
    
    /* ========================================
       WARNING & INFO BOX
    ======================================== */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        background: rgba(124, 58, 237, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stAlert .st-emotion-cache-1v0mbdj {
        color: #F5F3FF !important;
    }
    
    .stSpinner > div {
        border-color: #7C3AED !important;
    }
    
    .sidebar-product {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        border-left: 2px solid #7C3AED;
    }
    
    .sidebar-product .name {
        color: #F5F3FF;
        font-weight: 500;
    }
    
    .sidebar-product .detail {
        color: #C4B5FD;
        font-size: 0.85em;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()
# ============================================

@st.cache_resource
def init_workflow():
    return SalesGraphWorkflow()

@st.cache_resource
def init_database():
    return Database()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "sales_session_001"
if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = False

# ============================================
# HEADER
# ============================================
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 3em; margin-bottom: 0;">🛒 Virtual Sales Agent</h1>
    <p style="color: #9CA3AF; font-size: 1.1em;">
        Powered by LangChain, LangGraph & LangSmith, llama3.2:1b
    </p>
</div>
""", unsafe_allow_html=True)
# ============================================

workflow = init_workflow()
db = init_database()

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #A78BFA;">📊 Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🛍️ Available Products")
    products = db.get_all_products()
    if products:
        for p in products[:5]:
            st.markdown(f"""
            <div class="sidebar-product">
                <div class="name">• {p['name']}</div>
                <div class="detail">Rp{p['price']:,.0f} | Stok: {p['stock']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No products available")
    
    st.divider()
    
    st.subheader("🔍 Monitoring")
    if os.getenv("LANGSMITH_API_KEY"):
        st.success("✅ LangSmith Active")
        st.write(f"Project: {os.getenv('LANGSMITH_PROJECT')}")
    else:
        st.warning("⚠️ LangSmith not configured")
    
    st.divider()
    
    st.subheader("📈 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    if st.button("🔄 Reset Session"):
        st.session_state.messages = []
        st.session_state.pending_approval = False
        st.rerun()

# ============================================
# CHAT HISTORY
# ============================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.pending_approval:
    st.warning("⚠️ **Menunggu Konfirmasi Pesanan**")
    st.info("Ketik 'approve' untuk menyetujui atau 'reject' untuk membatalkan.")

# ============================================
# CHAT INPUT
# ============================================
if prompt := st.chat_input("💬 Tanyakan tentang produk atau buat pesanan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🧠 Memproses..."):
            result = workflow.process_query(
                prompt,
                thread_id=st.session_state.thread_id
            )
            
            response = result.get("response", "Maaf, terjadi kesalahan.")
            
            # ============================================
            # RESET pending_approval
            # ============================================
            if not result.get("needs_approval", False):
                st.session_state.pending_approval = False
            
            if result.get("needs_approval", False):
                st.session_state.pending_approval = True
                st.info("⚠️ **Menunggu persetujuan pesanan**")
            # ============================================
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # ============================================
            # DETAIL PROSES
            # ============================================
            with st.expander("🔍 Detail Proses"):
                intent = result.get("intent", "tidak terdeteksi")
                st.write(f"**Intent:** {intent}")
                
                if result.get("order_data"):
                    st.divider()
                    st.write("**📋 Order Data:**")
                    st.json(result["order_data"])
                
                if result.get("needs_approval"):
                    st.divider()
                    st.warning("⚠️ **Status:** Menunggu persetujuan")
            # ============================================
            
            if os.getenv("LANGSMITH_API_KEY"):
                st.caption("🔗 Trace tersedia di LangSmith Dashboard")
# ============================================