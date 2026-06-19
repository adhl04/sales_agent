from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.sales_agent import SalesAgent
import re

class SalesState(TypedDict):
    current_query: str
    intent: str
    response: str
    order_data: dict
    needs_approval: bool

class SalesGraphWorkflow:
    def __init__(self):
        self.agent = SalesAgent()
        self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(SalesState)
        
        workflow.add_node("process", self._process)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        self.workflow = workflow.compile(checkpointer=MemorySaver())
    
    def _classify_intent(self, query: str) -> str:
        """Klasifikasi intent dari query user"""
        query_lower = query.lower()
        
        # CEK APPROVAL/REJECT TERLEBIH DAHULU
        if any(kw in query_lower for kw in ["approve", "setuju", "ya", "ok", "okey"]):
            return "approve"
        elif any(kw in query_lower for kw in ["reject", "tolak", "tidak", "no", "batal"]):
            return "reject"
        elif any(kw in query_lower for kw in ["beli", "order", "pesan", "mau"]):
            return "order"
        elif any(kw in query_lower for kw in ["cek", "status", "tracking", "order #"]):
            return "track"
        elif any(kw in query_lower for kw in ["rekomendasi", "saran", "rekomen"]):
            return "recommend"
        elif any(kw in query_lower for kw in ["produk", "harga", "stok", "available", "daftar", "list", "tampilkan"]):
            return "product"
        elif any(kw in query_lower for kw in ["ram", "ssd", "storage", "processor", "layar", "screen", "spesifikasi", "spec"]):
            return "specs"
        else:
            return "general"
    
    def _extract_order_data(self, query: str, response: str) -> dict:
        """Ekstrak data order dari response jika ada"""
        order_data = {}
        
        if "ORDER #" in response:
            import re
            order_match = re.search(r"ORDER #(\d+)", response)
            if order_match:
                order_data["order_id"] = int(order_match.group(1))
            
            product_match = re.search(r"Produk:\s*(.+?)(?:\n|$)", response)
            if product_match:
                order_data["product_name"] = product_match.group(1).strip()
            
            qty_match = re.search(r"Jumlah:\s*(\d+)", response)
            if qty_match:
                order_data["quantity"] = int(qty_match.group(1))
            
            price_match = re.search(r"Total:\s*Rp([\d,]+)", response)
            if price_match:
                order_data["total_price"] = price_match.group(1).replace(",", "")
        
        return order_data
    
    def _process(self, state: SalesState) -> SalesState:
        """Proses query dan klasifikasi intent"""
        query = state["current_query"]
        
        intent = self._classify_intent(query)
        state["intent"] = intent
        
        response = self.agent.process_with_tools(query)
        state["response"] = response
        
        order_data = self._extract_order_data(query, response)
        if order_data:
            state["order_data"] = order_data
        
        if intent == "order" and "MENUNGGU PERSETUJUAN" in response:
            state["needs_approval"] = True
        
        print(f"🔍 Intent: {intent} | Query: {query}")
        
        return state
    
    def process_query(self, query: str, thread_id: str = "default") -> dict:
        initial_state = {
            "current_query": query,
            "intent": "",
            "response": "",
            "order_data": {},
            "needs_approval": False
        }
        
        config = {
            "configurable": {"thread_id": thread_id},
            "run_name": f"sales_query_{query[:30]}"
        }
        
        result = self.workflow.invoke(initial_state, config=config)
        
        return {
            "query": query,
            "response": result.get("response", ""),
            "intent": result.get("intent", ""),
            "order_data": result.get("order_data", {}),
            "needs_approval": result.get("needs_approval", False),
            "messages": []
        }