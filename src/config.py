import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class Config:
    # ============================================
    # OLLAMA
    # ============================================
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
    
    # ============================================
    # LANGSMITH
    # ============================================
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING_V2", "true").lower() == "true"
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "sales-agent-project")
    
    # ============================================
    # MODEL
    # ============================================
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_PATH = os.path.join(ROOT_DIR, "database", "sales.db")
    
    # ============================================
    # SALES AGENT
    # ============================================
    SALESPERSON_NAME = os.getenv("SALESPERSON_NAME", "Sarah")
    SALESPERSON_ROLE = os.getenv("SALESPERSON_ROLE", "Sales Representative")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "TechSolutions")
    COMPANY_BUSINESS = os.getenv("COMPANY_BUSINESS", "Enterprise Software Solutions")
    COMPANY_VALUES = os.getenv("COMPANY_VALUES", "Innovation, Integrity, Customer Success")