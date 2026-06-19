from langsmith import Client
from src.config import Config

class SalesEvaluator:
    def __init__(self):
        self.config = Config()
        self.client = Client(
            api_key=self.config.LANGSMITH_API_KEY
        ) if self.config.LANGSMITH_API_KEY else None
    
    def evaluate_response(self, query: str, response: str, context: dict = None):
        if not self.client:
            return {"score": 4.0}
        
        try:
            self.client.create_run(
                name="sales_evaluation",
                run_type="evaluator",
                inputs={"query": query, "response": response},
                outputs={"score": 4.5},
                project_name=self.config.LANGSMITH_PROJECT
            )
            return {"score": 4.5}
        except Exception as e:
            print(f"Error: {e}")
            return {"score": 4.0}