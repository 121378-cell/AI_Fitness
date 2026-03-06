# PDF Knowledge Base Usage Guide

## Overview
The AI Fitness PDF Knowledge Base system allows you to enhance your AI coach with custom knowledge from PDF documents. This system extracts, indexes, and retrieves knowledge to improve training plan generation.

## Quick Start

### 1. Add a PDF to the Knowledge Base

```bash
python pdf_management.py add <pdf_path> --category <category>
```

**Example:**
```bash
python pdf_management.py add "C:\My Documents\Training_Guide.pdf" --category "Training"
```

**Supported Categories:**
- Training
- Nutrition
- Recovery
- Programming
- Anatomy
- General

### 2. List All Documents

```bash
python pdf_management.py list
```

Output:
```
ID    Filename                    Category        Chunks    Added
5     Training_Guide.pdf          Training        25        2026-03-06 20:30:15
6     Nutrition_Manual.pdf        Nutrition       18        2026-03-06 20:31:02
```

### 3. Search Knowledge

```bash
python pdf_management.py search "chest exercises"
```

### 4. View Statistics

```bash
python pdf_management.py stats
```

Output:
```
Knowledge Base Statistics:
  Total Documents: 2
  Total Chunks: 43
  Average Chunks per Document: 21.5
  Categories: 2
    - Training: 1 documents
    - Nutrition: 1 documents
```

### 5. Delete a Document

```bash
python pdf_management.py delete <doc_id>
```

## How It Works

### Step 1: PDF Processing
When you add a PDF:
1. Text is extracted from the PDF
2. Content is cleaned and normalized
3. Text is split into chunks (500 characters each)
4. Keywords are extracted automatically
5. Original PDF is saved to `data/knowledge_base/raw_pdfs/`

### Step 2: Knowledge Storage
Extracted content is stored in:
- **SQLite Database** (`data/knowledge_base/knowledge.db`)
- **Extracted Text Files** (`data/knowledge_base/extracted/`)

### Step 3: Knowledge Retrieval
When the AI coach generates plans:
1. Relevant knowledge is automatically retrieved
2. Context is included in the Ollama prompt
3. The AI generates better, more informed plans

### Step 4: Integration with Ollama
The knowledge context is added to prompts like:
```
"Based on the following training knowledge: [PDF content] 
and user data: [stats], 
generate a training plan..."
```

## Creating PDFs for Best Results

### For PDFs to work well:
1. **Clear Structure**: Use headings and sections
2. **Concise Content**: Keep paragraphs short
3. **Keywords**: Include relevant fitness terminology
4. **Examples**: Provide concrete examples of concepts
5. **Formatting**: Use bullet points and lists

### Example Content Structure:
```
# Exercise Programming Principles

## Progressive Overload
Progressive overload is...

## Variable Loading Techniques
- Pyramid sets: Start heavy, decrease weight
- Cluster sets: Heavy weight with short rest
- Double progression: Increase reps, then weight

## Recovery Guidelines
...
```

## File Organization

```
data/knowledge_base/
├── raw_pdfs/                    # Original PDF files
│   ├── Training_Principles.pdf
│   └── Nutrition_Guide.pdf
├── extracted/                   # Extracted text files
│   ├── Training_Principles_extracted.txt
│   └── Nutrition_Guide_extracted.txt
└── knowledge.db                 # SQLite database
```

## Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `add` | Add PDF to knowledge base | `python pdf_management.py add file.pdf --category Training` |
| `list` | List all documents | `python pdf_management.py list` |
| `search` | Search knowledge | `python pdf_management.py search "chest exercises"` |
| `stats` | View statistics | `python pdf_management.py stats` |
| `delete` | Remove document | `python pdf_management.py delete 5` |

## Troubleshooting

### PDF Not Being Added
- Check file exists: `ls data/knowledge_base/raw_pdfs/`
- Verify PDF is readable: Try opening in PDF reader
- Check database: `python pdf_management.py list`

### No Results When Searching
- Add more PDFs with relevant content
- Use more specific keywords
- Check category filters

### Low Quality Plans
- Add more training-specific PDFs
- Include different perspectives (periodization, recovery, etc.)
- Ensure PDFs have clear, structured content

## Advanced Usage

### Integrating with Ollama
The retriever automatically integrates with `Gemini_Hevy.py`:

```python
from knowledge_retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()
context = retriever.get_context_for_query("chest exercises")
retriever.close()
```

### Custom Queries
```python
from knowledge_retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()

# Get specific context
training_context = retriever.get_training_context()
recovery_context = retriever.get_recovery_context()
chest_context = retriever.get_muscle_group_context("chest")

retriever.close()
```

## Best Practices

1. **Start Small**: Begin with 2-3 high-quality PDFs
2. **Categorize**: Use consistent category names
3. **Monitor Quality**: Check generated plans improve over time
4. **Update Regularly**: Add new knowledge as it becomes available
5. **Test Queries**: Use `search` command to verify content is indexed

## Support

For issues or questions:
1. Check the knowledge base is initialized: `python pdf_management.py list`
2. Search for similar terms
3. Verify PDF content is readable
4. Check `data/knowledge_base/extracted/` files for extracted content