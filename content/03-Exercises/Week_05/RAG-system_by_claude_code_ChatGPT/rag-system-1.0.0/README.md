# RAG System - Retrieval-Augmented Generation

## Quick Start

### Option 1: Local Installation

#### Unix/Linux/macOS:
```bash
chmod +x install.sh
./install.sh
```

#### Windows:
```cmd
install.bat
```

### Option 2: Docker

```bash
docker-compose up -d
docker-compose run rag-system setup
docker-compose run rag-system search "your query"
```

### Option 3: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup
python rag_system.py setup

# Search
python rag_system.py search "your query"
```

## Usage

1. Add documents to `docs/originals/`
2. Run setup: `rag-system setup`
3. Search: `rag-system search "your query"`

## Supported Formats

- PDF documents
- Word documents (DOCX)
- Excel spreadsheets (XLSX)
- PowerPoint presentations (PPTX)
- Python source code (.py)

## Commands

- `setup` - Complete setup process
- `ingest` - Process documents to Markdown
- `index` - Build vector index
- `search` - Search documents
- `stats` - Show index statistics

## Requirements

- Python 3.8+
- 2GB+ RAM recommended
- 1GB+ disk space for index

## License

MIT License
