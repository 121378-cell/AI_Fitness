"""
PDF Management Interface
Handles adding, listing, and managing PDFs in the knowledge base.
"""

import os
import sys
from pathlib import Path

from pdf_processor import process_pdf_file
from knowledge_base import KnowledgeBase


class PDFManagement:
    """
    Interface for managing PDFs and the knowledge base.
    """
    
    def __init__(self):
        """Initialize PDF management."""
        self.kb = KnowledgeBase()
        self.raw_pdf_dir = "data/knowledge_base/raw_pdfs"
        os.makedirs(self.raw_pdf_dir, exist_ok=True)
    
    def add_pdf(self, pdf_path, category="General"):
        """
        Add a PDF to the knowledge base.
        
        Args:
            pdf_path (str): Path to PDF file
            category (str): Document category
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify file exists
            if not os.path.exists(pdf_path):
                print(f"[!] PDF file not found: {pdf_path}")
                return False
            
            # Copy to raw_pdfs directory
            filename = os.path.basename(pdf_path)
            dest_path = os.path.join(self.raw_pdf_dir, filename)
            
            if not os.path.exists(dest_path):
                import shutil
                shutil.copy2(pdf_path, dest_path)
                print(f"✓ Copied PDF to {dest_path}")
            
            # Process PDF
            result = process_pdf_file(dest_path)
            
            if result['status'] != 'success':
                print(f"[!] Failed to process PDF: {result.get('error')}")
                return False
            
            # Add to knowledge base
            doc_id = self.kb.add_document(
                filename=filename,
                category=category,
                source_path=dest_path,
                extracted_file=result['file'],
                chunks=result['chunks'],
                keywords=result['keywords']
            )
            
            if doc_id > 0:
                print(f"✓ Successfully added to knowledge base (ID: {doc_id})")
                return True
            else:
                print("[!] Failed to add document to knowledge base")
                return False
        except Exception as e:
            print(f"[!] Error adding PDF: {e}")
            return False
    
    def list_pdfs(self):
        """
        List all PDFs in the knowledge base.
        
        Returns:
            list: List of document dictionaries
        """
        docs = self.kb.get_all_documents()
        
        if not docs:
            print("Knowledge base is empty.")
            return []
        
        print(f"\n{'ID':<5} {'Filename':<40} {'Category':<20} {'Chunks':<8} {'Added':<20}")
        print("-" * 100)
        
        for doc in docs:
            print(f"{doc['id']:<5} {doc['filename']:<40} {doc['category']:<20} {doc['chunk_count']:<8} {doc['date_added']:<20}")
        
        print(f"\nTotal: {len(docs)} documents")
        return docs
    
    def delete_pdf(self, doc_id):
        """
        Delete a PDF from the knowledge base.
        
        Args:
            doc_id (int): Document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.kb.delete_document(doc_id)
        except Exception as e:
            print(f"[!] Error deleting document: {e}")
            return False
    
    def search_knowledge(self, query):
        """
        Search the knowledge base.
        
        Args:
            query (str): Search query
        """
        results = self.kb.search_knowledge(query, limit=10)
        
        if not results:
            print(f"No results found for: {query}")
            return
        
        print(f"\n{'Chunk ID':<10} {'Source':<40} {'Category':<20}")
        print("-" * 75)
        
        for result in results:
            source = f"{result['filename']}"
            preview = result['text_content'][:60].replace('\n', ' ')
            print(f"{result['chunk_id']:<10} {source:<40} {result['category']:<20}")
            print(f"  Preview: {preview}...")
            print()
    
    def display_statistics(self):
        """Display knowledge base statistics."""
        docs = self.kb.get_all_documents()
        
        print("\nKnowledge Base Statistics:")
        print(f"  Total Documents: {len(docs)}")
        
        if docs:
            total_chunks = sum(doc['chunk_count'] for doc in docs)
            avg_chunks = total_chunks / len(docs)
            print(f"  Total Chunks: {total_chunks}")
            print(f"  Average Chunks per Document: {avg_chunks:.1f}")
            
            categories = {}
            for doc in docs:
                cat = doc['category'] or 'Uncategorized'
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"  Categories: {len(categories)}")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {cat}: {count} documents")
    
    def close(self):
        """Close knowledge base connection."""
        self.kb.close()


def main():
    """Command-line interface for PDF management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage PDFs in the AI Fitness knowledge base")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a PDF to the knowledge base')
    add_parser.add_argument('pdf_path', help='Path to PDF file')
    add_parser.add_argument('--category', default='General', help='Document category')
    
    # List command
    subparsers.add_parser('list', help='List all PDFs in knowledge base')
    
    # Delete command
    del_parser = subparsers.add_parser('delete', help='Delete a PDF from knowledge base')
    del_parser.add_argument('doc_id', type=int, help='Document ID')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge base')
    search_parser.add_argument('query', help='Search query')
    
    # Stats command
    subparsers.add_parser('stats', help='Display knowledge base statistics')
    
    args = parser.parse_args()
    
    pm = PDFManagement()
    
    try:
        if args.command == 'add':
            pm.add_pdf(args.pdf_path, args.category)
        elif args.command == 'list':
            pm.list_pdfs()
        elif args.command == 'delete':
            pm.delete_pdf(args.doc_id)
        elif args.command == 'search':
            pm.search_knowledge(args.query)
        elif args.command == 'stats':
            pm.display_statistics()
        else:
            parser.print_help()
    finally:
        pm.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("PDF Management Interface")
        print("\nUsage:")
        print("  python pdf_management.py add <pdf_path> [--category <category>]")
        print("  python pdf_management.py list")
        print("  python pdf_management.py delete <doc_id>")
        print("  python pdf_management.py search <query>")
        print("  python pdf_management.py stats")
