import chromadb

class SecureRetriever:
    def __init__(self, vector_db):
        self.db = vector_db

    def search(self, query_text, user_role):
        # MITIGATION: Retrieval filtering (Role-scoped)
        # Prevent Employee from ever seeing HR-only document chunks
        filter_criteria = {"role": "Employee"} if user_role == "Employee" else {}
        
        results = self.db.query(
            query_texts=[query_text],
            n_results=2,
            where=filter_criteria
        )
        return results['documents']