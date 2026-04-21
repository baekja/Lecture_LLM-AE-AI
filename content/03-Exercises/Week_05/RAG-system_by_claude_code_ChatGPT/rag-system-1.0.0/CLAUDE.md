# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG (Retrieval-Augmented Generation) System that enables Claude Code to search and utilize information from project documents (PDF, Word, Excel, PowerPoint, Python code).

## Quick Start

### 1. Setup Environment
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Process Documents
```bash
# Place documents in docs/originals/
# Then run ingestion pipeline
python3 scripts/ingest.py

# Build vector index
python3 scripts/build_index.py
```

### 3. Search Documents
```bash
# Command line search
python3 scripts/retrieve.py "your search query"

# In Claude Code, use the /r command
/r system architecture
```

## Project Structure

```
.claude/
  commands/r.md        # Document retrieval slash command
  settings.json        # Tool permissions and hooks
scripts/
  ingest.py           # Convert documents to Markdown
  build_index.py      # Build vector embeddings index
  retrieve.py         # Semantic search interface
deployment/            # Deployment and distribution files
  rag_system.py       # Standalone executable
  Dockerfile          # Docker container definition
  docker-compose.yml  # Docker Compose configuration
  install.sh          # Unix/Linux/macOS installer
  install.bat         # Windows installer
  package.sh          # Distribution packaging script
  dist/               # Distribution packages
knowledge/
  md/                 # Processed Markdown documents
  index/              # ChromaDB vector database
docs/
  originals/          # Original documents (PDF/DOCX/XLSX/PPTX)
scratch/              # Temporary files for search results
```

## Key Commands

### Document Processing
```bash
# Process all new/changed documents
python3 scripts/ingest.py

# Force reprocess all documents
python3 scripts/ingest.py --force

# Build/update vector index
python3 scripts/build_index.py

# Verify index
python3 scripts/build_index.py --verify
```

### Document Search
```bash
# Search from command line
python3 scripts/retrieve.py "search query" --top-k 10

# Get index statistics
python3 scripts/retrieve.py --stats

# Filter by document type
python3 scripts/retrieve.py "query" --filter-type "PDF"
```

### Claude Code Integration
- Use `/r <query>` to search documents and get contextual answers
- Documents are automatically processed when added to `docs/originals/`
- Search results include source citations (file, page, slide)

## Document Support

- **PDF**: Full text extraction with page markers, table detection
- **Word (DOCX)**: Structure-preserving conversion with formatting
- **Excel (XLSX)**: All sheets converted to Markdown tables
- **PowerPoint (PPTX)**: Slide content with text and tables
- **Python (.py)**: Code files with syntax highlighting

## Architecture

1. **Ingestion Layer**: Converts various formats to searchable Markdown
2. **Embedding Layer**: BAAI/bge-m3 multilingual embeddings for Korean/English
3. **Vector Database**: ChromaDB for efficient similarity search
4. **Retrieval Layer**: Semantic search with metadata filtering
5. **Integration Layer**: Claude Code slash commands and hooks

## Deployment

### Standalone Application
```bash
# Use the unified RAG system script
python deployment/rag_system.py setup
python deployment/rag_system.py search "query"
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f deployment/docker-compose.yml up -d
docker-compose -f deployment/docker-compose.yml run rag-system setup
```

### Distribution
```bash
# Create distribution packages
cd deployment && ./package.sh

# Install on new system
tar -xzf dist/rag-system-1.0.0.tar.gz
cd rag-system-1.0.0 && ./install.sh
```

## Troubleshooting

### Common Issues

#### ChromaDB Metadata Error
- **Problem**: "Expected metadata value to be a str, int, float or bool"
- **Solution**: Fixed in build_index.py - only adds non-None metadata values

#### Missing Dependencies
- **Problem**: ModuleNotFoundError for fitz, tabulate, etc.
- **Solution**: Run `pip install PyMuPDF tabulate` or use requirements.txt

#### Text Splitter Compatibility
- **Problem**: MarkdownTextSplitter separator issues
- **Solution**: Use RecursiveCharacterTextSplitter instead

### Performance Optimization
- Adjust chunk_size in build_index.py (default: 1000)
- Increase top_k for more search results
- Use --force flag to rebuild index after configuration changes

## Advanced Usage

### Batch Processing
```bash
# Process multiple directories
for dir in project1 project2; do
    cp $dir/*.pdf docs/originals/
    python scripts/ingest.py
done
python scripts/build_index.py
```

### Custom Embeddings
The system uses BAAI/bge-m3 for multilingual support. To change:
1. Edit model_name in scripts/build_index.py and retrieve.py
2. Rebuild index after model change

### API Integration
```python
# Use retriever programmatically
from scripts.retrieve import DocumentRetriever

retriever = DocumentRetriever()
results = retriever.search("your query", top_k=5)
```

### Search Filters
```bash
# Filter by document type
python scripts/retrieve.py "query" --filter-type "PDF"

# Filter by source file
python scripts/retrieve.py "query" --filter-source "specific_file.pdf"
```

## Dependencies

### Core Requirements
- Python 3.8+
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- LangChain for text processing

### Document Processing
- PyMuPDF (fitz) for PDF extraction
- python-docx for Word documents
- openpyxl for Excel files
- python-pptx for PowerPoint
- tabulate for table formatting

### Full Installation
```bash
pip install chromadb sentence-transformers langchain langchain-community \
            PyMuPDF python-docx openpyxl python-pptx tabulate
```

## Migration to Other Projects

### Quick Migration
1. Copy entire project structure to new location
2. Clear existing index: `rm -rf knowledge/index/*`
3. Add new documents to `docs/originals/`
4. Run setup: `python deployment/rag_system.py setup`

### Selective Migration
```bash
# Copy only essential files
cp -r scripts/ /new/project/
cp -r .claude/ /new/project/
cp deployment/rag_system.py /new/project/
cp requirements.txt /new/project/

# Create directories
cd /new/project
mkdir -p docs/originals knowledge/{md,index} scratch

# Setup and run
pip install -r requirements.txt
python rag_system.py setup
```

## Best Practices

### Document Organization
- Keep original documents in `docs/originals/`
- Use descriptive filenames for better search context
- Group related documents in subdirectories

### Index Management
- Rebuild index weekly or after major document updates
- Backup `knowledge/index/` before major changes
- Monitor index size - consider splitting if >1GB

### Search Optimization
- Use specific keywords for better results
- Combine Korean and English terms when applicable
- Review top-k parameter based on document corpus size

### Security Considerations
- Avoid indexing sensitive documents
- Implement access controls for deployment
- Regularly update dependencies for security patches

## Tips

- Place documents in `docs/originals/` before processing
- Run ingestion → build_index in sequence for new documents
- Use `/r` command for quick document searches within Claude Code
- Search results are saved to `scratch/_search_results.md` for reference
- The system preserves document structure (pages, slides, sheets) in search results
- Use `rag_system.py` for unified command-line interface
- Deploy with Docker for isolated environments
- Create distribution packages with `deployment/package.sh`
- Monitor ChromaDB size in `knowledge/index/` directory
- Test searches after adding new document types