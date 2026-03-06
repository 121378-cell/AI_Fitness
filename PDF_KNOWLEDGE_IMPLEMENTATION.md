# PDF Knowledge Base Implementation Guide

## 📚 Overview

The AI Fitness Coach now includes a **PDF Knowledge Base System** that enables you to enhance the AI model with custom knowledge from fitness documents, training guides, nutrition manuals, and other resources.

## ✨ Features

- **PDF Text Extraction**: Automatically extracts content from PDF and text files
- **Local SQLite Database**: All knowledge stored locally for privacy and offline access
- **Smart Chunking**: Splits documents into manageable chunks for efficient retrieval
- **Keyword Extraction**: Automatically identifies key terms for better search
- **Semantic Search**: Retrieve relevant sections based on queries
- **Ollama Integration**: AI automatically uses relevant knowledge when generating plans
- **CLI Management**: Simple command-line interface for managing documents

## 🚀 Quick Start

### 1. Install PDF Libraries
```bash
pip install pdfplumber PyPDF2
```

### 2. Add a PDF to Knowledge Base
```bash
python pdf_management.py add "path/to/document.pdf" --category "Training"
```

### 3. View Documents
```bash
python pdf_management.py list
```

### 4. Search Knowledge
```bash
python pdf_management.py search "chest exercises"
```

### 5. Run AI Coach with Knowledge
```bash
python Gemini_Hevy.py
```

The script will automatically detect PDF knowledge and use it to generate better plans.

## 📁 File Structure

```
data/knowledge_base/
├── raw_pdfs/                      # Original PDF files
│   ├── Training_Principles.txt
│   ├── Nutrition_Guide.pdf
│   └── Recovery_Methods.pdf
├── extracted/                     # Extracted text files
│   ├── Training_Principles_extracted.txt
│   ├── Nutrition_Guide_extracted.txt
│   └── Recovery_Methods_extracted.txt
└── knowledge.db                   # SQLite database
```

## 📝 Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `add` | Add document to knowledge base | `python pdf_management.py add doc.pdf --category Training` |
| `list` | List all documents | `python pdf_management.py list` |
| `search` | Search knowledge | `python pdf_management.py search "query"` |
| `stats` | View statistics | `python pdf_management.py stats` |
| `delete` | Remove document | `python pdf_management.py delete 1` |

## 🏗️ Architecture

### PDF Processor (`pdf_processor.py`)
- Extracts text from PDFs and text files
- Cleans and normalizes content
- Chunks text into manageable pieces
- Automatically extracts keywords

### Knowledge Base (`knowledge_base.py`)
- SQLite-based local storage
- Stores documents and chunks
- Provides search functionality
- Manages document lifecycle

### Knowledge Retriever (`knowledge_retriever.py`)
- Queries knowledge base for relevant content
- Formats results for Ollama prompts
- Supports category-specific retrieval
- Context-aware search

### PDF Management (`pdf_management.py`)
- Command-line interface for document management
- Orchestrates PDF processing and storage
- Provides user-friendly commands

### Integration (`Gemini_Hevy.py`)
- Automatically detects available knowledge
- Retrieves context before generating plans
- Includes knowledge in AI prompts
- Graceful fallback if knowledge unavailable

## 💡 Use Cases

### 1. Custom Training Principles
Add your own training methodology documents to ensure the AI follows your specific principles.

### 2. Nutrition Integration
Include nutrition guides so the AI can provide holistic fitness recommendations.

### 3. Recovery Protocols
Add recovery and injury prevention knowledge for safer training plans.

### 4. Programming Templates
Include workout programming examples for consistency.

### 5. Assessment Protocols
Add testing and assessment methodologies for better progress tracking.

## 🔧 Advanced Usage

### Programmatic Access

```python
from pdf_management import PDFManagement

# Add document
pm = PDFManagement()
pm.add_pdf("training_guide.pdf", category="Training")
pm.list_pdfs()
pm.close()
```

### Custom Queries

```python
from knowledge_retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()

# Get specific contexts
training_context = retriever.get_training_context()
recovery_context = retriever.get_recovery_context()
chest_context = retriever.get_muscle_group_context("chest")

retriever.close()
```

### Search Results

```python
from knowledge_base import KnowledgeBase

kb = KnowledgeBase()
results = kb.search_knowledge("progressive overload", limit=5)

for result in results:
    print(f"From: {result['filename']}")
    print(f"Content: {result['text_content'][:200]}...")
    
kb.close()
```

## 📊 Database Schema

### Documents Table
```
- id (PRIMARY KEY)
- filename (UNIQUE)
- category
- source_path
- extracted_file
- chunk_count
- keywords (JSON)
- date_added
- date_updated
```

### Chunks Table
```
- id (PRIMARY KEY)
- doc_id (FOREIGN KEY)
- chunk_num
- text_content
- keywords (JSON)
```

### Query Cache Table
```
- id (PRIMARY KEY)
- query_hash (UNIQUE)
- results (JSON)
- timestamp
```

## ⚡ Performance Tips

1. **Start Small**: Begin with 2-3 high-quality documents
2. **Clear Organization**: Use consistent category names
3. **Focused Content**: PDFs with specific topics work better
4. **Regular Updates**: Add documents incrementally
5. **Monitor Results**: Check if plans improve with new knowledge

## 🐛 Troubleshooting

### PDF Not Added
```bash
# Check if file exists
ls data/knowledge_base/raw_pdfs/

# Verify processing
python pdf_processor.py "path/to/file.pdf"
```

### No Search Results
```bash
# List documents
python pdf_management.py list

# Check extracted content
ls data/knowledge_base/extracted/
```

### Low Quality Plans
- Add more training-specific documents
- Ensure PDFs have clear structure
- Use focused, relevant content
- Check knowledge is being retrieved

## 📚 Recommended Documents

Consider adding PDFs for:
- **Exercise Science**: Biomechanics, muscle physiology
- **Training Programming**: Periodization, intensity techniques
- **Nutrition**: Macro/micronutrients, meal timing
- **Recovery**: Sleep optimization, injury prevention
- **Testing**: Assessment protocols, progress tracking

## 🔐 Privacy & Offline

- All knowledge stored **locally** on your machine
- **No cloud uploads** of your PDFs
- **Offline access** after documents are processed
- **Full control** over what knowledge is used

## 🚀 Integration with Ollama

When generating plans, the system:
1. Detects available knowledge documents
2. Retrieves relevant chunks based on plan requirements
3. Adds context to Ollama prompts
4. AI generates informed, knowledge-based plans

Example prompt enhancement:
```
BEFORE:
"Generate a training plan based on user stats"

AFTER:
"Based on the following training knowledge: [progressive 
overload principles, compound exercise recommendations, 
recovery guidelines] and user stats: [data], 
generate a training plan"
```

## 📖 Example: Adding a Training Guide

```bash
# 1. Prepare your PDF
# Create or save a training guide as PDF

# 2. Add to knowledge base
python pdf_management.py add "My_Training_Guide.pdf" --category "Training"

# 3. Verify it was added
python pdf_management.py list

# 4. Search to confirm content
python pdf_management.py search "periodization"

# 5. Run Gemini_Hevy to generate plans using this knowledge
python Gemini_Hevy.py
```

## ✅ Validation Checklist

- [ ] PDF libraries installed (`pdfplumber`, `PyPDF2`)
- [ ] Knowledge base directory created
- [ ] First PDF added successfully
- [ ] Search returns relevant results
- [ ] Gemini_Hevy.py shows "Using knowledge from X document(s)"
- [ ] Generated plans reflect added knowledge

---

For detailed usage instructions, see [PDF_KNOWLEDGE_GUIDE.md](PDF_KNOWLEDGE_GUIDE.md)