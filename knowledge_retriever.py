"""
Knowledge Retriever Module
Retrieves relevant knowledge from the knowledge base to enhance AI prompts.
"""

from knowledge_base import KnowledgeBase


class KnowledgeRetriever:
    """
    Retrieves and formats knowledge from the knowledge base for use in AI prompts.
    """
    
    def __init__(self, db_path="data/knowledge_base/knowledge.db"):
        """Initialize the knowledge retriever."""
        self.kb = KnowledgeBase(db_path)
    
    def get_context_for_query(self, query, max_chunks=5, max_chars=2000):
        """
        Retrieve relevant context from knowledge base for a given query.
        
        Args:
            query (str): User query or topic
            max_chunks (int): Maximum number of chunks to return
            max_chars (int): Maximum total characters to return
            
        Returns:
            str: Formatted context string to include in prompts, or empty string if no results
        """
        try:
            # Search knowledge base
            results = self.kb.search_knowledge(query, limit=max_chunks)
            
            if not results:
                return ""
            
            # Format results
            context = "=== RELEVANT KNOWLEDGE FROM PDF DOCUMENTS ===\n\n"
            total_chars = 0
            
            for i, result in enumerate(results, 1):
                chunk_text = result['text_content']
                source = f"{result['filename']} ({result['category']})"
                
                # Check character limit
                chunk_with_header = f"[{i}] From {source}:\n{chunk_text[:500]}\n\n"
                if total_chars + len(chunk_with_header) > max_chars:
                    break
                
                context += chunk_with_header
                total_chars += len(chunk_with_header)
            
            context += "=== END KNOWLEDGE CONTEXT ===\n\n"
            return context
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
    def get_training_context(self):
        """
        Get general training knowledge context.
        
        Returns:
            str: Formatted training context
        """
        return self.get_context_for_query("training principles exercise programming")
    
    def get_recovery_context(self):
        """
        Get recovery and nutrition context.
        
        Returns:
            str: Formatted recovery context
        """
        return self.get_context_for_query("recovery sleep nutrition rest")
    
    def get_muscle_group_context(self, muscle_group):
        """
        Get context for specific muscle group.
        
        Args:
            muscle_group (str): Muscle group name (e.g., 'chest', 'legs')
            
        Returns:
            str: Formatted context for muscle group
        """
        return self.get_context_for_query(f"{muscle_group} exercises programming")
    
    def list_available_knowledge(self):
        """
        List all available documents in knowledge base.
        
        Returns:
            list: List of document dictionaries
        """
        return self.kb.get_all_documents()
    
    def get_knowledge_summary(self):
        """
        Get summary of knowledge base contents.
        
        Returns:
            str: Summary string
        """
        docs = self.kb.get_all_documents()
        
        if not docs:
            return "Knowledge base is empty. Add PDFs using pdf_management.py"
        
        summary = f"Knowledge Base Summary:\n"
        summary += f"  Total Documents: {len(docs)}\n"
        
        total_chunks = sum(doc['chunk_count'] for doc in docs)
        summary += f"  Total Chunks: {total_chunks}\n\n"
        
        summary += "Documents:\n"
        for doc in docs:
            summary += f"  - {doc['filename']} ({doc['category']}): {doc['chunk_count']} chunks\n"
        
        return summary
    
    def close(self):
        """Close knowledge base connection."""
        self.kb.close()


if __name__ == "__main__":
    # Example usage
    retriever = KnowledgeRetriever()
    
    print(retriever.get_knowledge_summary())
    print("\n")
    
    # Example query
    context = retriever.get_context_for_query("chest exercises workout")
    if context:
        print("Retrieved context:")
        print(context)
    else:
        print("No knowledge found. Add PDFs to the knowledge base.")
    
    retriever.close()
