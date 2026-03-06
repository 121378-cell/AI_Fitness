"""
PDF Processor Module
Extracts text content from PDF files for knowledge base indexing.
"""

import os
import re
from pathlib import Path


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file or text file.
    
    Args:
        pdf_path (str): Path to the PDF file or text file
        
    Returns:
        str: Extracted text content, or empty string if extraction fails
    """
    try:
        # Check if it's a text file
        if pdf_path.lower().endswith('.txt'):
            with open(pdf_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Try using pdfplumber first (preferred)
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            # Fallback to PyPDF2
            from PyPDF2 import PdfReader
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def clean_extracted_text(text):
    """
    Clean and normalize extracted text.
    
    Args:
        text (str): Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace and newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    return text


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks for knowledge base indexing.
    
    Args:
        text (str): Text to chunk
        chunk_size (int): Approximate size of each chunk (in characters)
        overlap (int): Character overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def extract_keywords(text, num_keywords=10):
    """
    Extract key terms from text (simple approach).
    
    Args:
        text (str): Text to extract keywords from
        num_keywords (int): Number of keywords to extract
        
    Returns:
        list: List of extracted keywords
    """
    # Remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
        'is', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it'
    }
    
    # Extract words and filter
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count occurrences and return most common
    from collections import Counter
    counted = Counter(keywords)
    return [word for word, _ in counted.most_common(num_keywords)]


def process_pdf_file(pdf_path, output_dir="data/knowledge_base/extracted"):
    """
    Process a PDF file: extract text, clean, chunk, and save.
    
    Args:
        pdf_path (str): Path to PDF file
        output_dir (str): Directory to save extracted content
        
    Returns:
        dict: Processing results {'chunks': [...], 'keywords': [...], 'status': 'success'/'failed'}
    """
    try:
        # Extract text
        print(f"Extracting text from {os.path.basename(pdf_path)}...")
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"  [!] No text extracted from {pdf_path}")
            return {"chunks": [], "keywords": [], "status": "failed", "error": "No text extracted"}
        
        # Clean text
        text = clean_extracted_text(text)
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=500)
        
        # Extract keywords
        keywords = extract_keywords(text, num_keywords=15)
        
        # Save extracted content
        os.makedirs(output_dir, exist_ok=True)
        base_name = Path(pdf_path).stem
        output_file = os.path.join(output_dir, f"{base_name}_extracted.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {os.path.basename(pdf_path)}\n")
            f.write(f"Keywords: {', '.join(keywords)}\n")
            f.write(f"Chunks: {len(chunks)}\n")
            f.write("\n" + "="*80 + "\n\n")
            f.write(text)
        
        print(f"  ✓ Extracted {len(chunks)} chunks, saved to {output_file}")
        
        return {
            "chunks": chunks,
            "keywords": keywords,
            "status": "success",
            "file": output_file,
            "chunk_count": len(chunks)
        }
    
    except Exception as e:
        print(f"  [!] Error processing {pdf_path}: {e}")
        return {"chunks": [], "keywords": [], "status": "failed", "error": str(e)}


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        result = process_pdf_file(pdf_file)
        print(f"Result: {result}")
    else:
        print("Usage: python pdf_processor.py <pdf_file>")
