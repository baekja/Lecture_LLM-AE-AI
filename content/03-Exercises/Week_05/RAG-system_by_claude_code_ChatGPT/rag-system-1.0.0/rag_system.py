#!/usr/bin/env python3
"""
RAG System - Standalone Executable
Retrieval-Augmented Generation System for Document Search
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict
import subprocess

# Determine project root based on package structure
CURRENT_DIR = Path(__file__).parent

# Check if we're in a distribution package (scripts folder at same level)
# or development environment (scripts in parent directory)
if (CURRENT_DIR / "scripts").exists():
    # Distribution package: rag_system.py and scripts/ are in the same directory
    PROJECT_ROOT = CURRENT_DIR
elif (CURRENT_DIR.parent / "scripts").exists():
    # Development environment: rag_system.py is in deployment/ subdirectory
    PROJECT_ROOT = CURRENT_DIR.parent
else:
    # Fallback to current directory
    PROJECT_ROOT = CURRENT_DIR

sys.path.insert(0, str(PROJECT_ROOT))

class RAGSystem:
    """Main RAG System Application"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or PROJECT_ROOT
        self.scripts_dir = self.base_dir / "scripts"
        self.docs_dir = self.base_dir / "docs" / "originals"
        self.knowledge_dir = self.base_dir / "knowledge"
        
        # Ensure directories exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        (self.knowledge_dir / "md").mkdir(exist_ok=True)
        (self.knowledge_dir / "index").mkdir(exist_ok=True)
        (self.base_dir / "scratch").mkdir(exist_ok=True)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        # Map package names to their actual import names
        package_mappings = {
            'chromadb': 'chromadb',
            'sentence-transformers': 'sentence_transformers',
            'langchain': 'langchain',
            'langchain-community': 'langchain_community',
            'PyMuPDF': 'fitz',  # PyMuPDF imports as 'fitz'
            'python-docx': 'docx',  # python-docx imports as 'docx'
            'openpyxl': 'openpyxl',
            'python-pptx': 'pptx',  # python-pptx imports as 'pptx'
            'tabulate': 'tabulate',
            'tiktoken': 'tiktoken',
            'tqdm': 'tqdm',
            'pandas': 'pandas'
        }

        missing = []
        for package, import_name in package_mappings.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package)

        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            print(f"   Run: pip install {' '.join(missing)}")
            return False

        print("✅ All dependencies installed")
        return True

    def install_dependencies(self) -> bool:
        """Automatically install missing dependencies"""
        print("\n📦 Installing dependencies...")

        # Check for requirements.txt in current directory first
        current_dir_req = Path("requirements.txt")
        base_dir_req = self.base_dir / "requirements.txt"

        requirements_file = None
        if current_dir_req.exists():
            requirements_file = current_dir_req
        elif base_dir_req.exists():
            requirements_file = base_dir_req
        else:
            print("❌ requirements.txt not found")
            return False

        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            print(f"   Installing from: {requirements_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def ingest_documents(self, force: bool = False) -> bool:
        """Process documents to Markdown"""
        print("\n📄 Processing documents...")
        
        cmd = [sys.executable, str(self.scripts_dir / "ingest.py")]
        if force:
            cmd.append("--force")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Documents processed successfully")
                return True
            else:
                print(f"❌ Error processing documents: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Failed to run ingestion: {e}")
            return False
    
    def build_index(self, verify: bool = False) -> bool:
        """Build vector embeddings index"""
        print("\n🔨 Building vector index...")
        
        cmd = [sys.executable, str(self.scripts_dir / "build_index.py")]
        if verify:
            cmd.append("--verify")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Index built successfully")
                return True
            else:
                print(f"❌ Error building index: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Failed to build index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10, format_type: str = "markdown") -> str:
        """Search documents"""
        cmd = [
            sys.executable, 
            str(self.scripts_dir / "retrieve.py"),
            query,
            "--top-k", str(top_k),
            "--format", format_type
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Search failed: {e}"
    
    def get_stats(self) -> str:
        """Get index statistics"""
        cmd = [sys.executable, str(self.scripts_dir / "retrieve.py"), "--stats"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Failed to get stats: {e}"
    
    def setup(self, force: bool = False, auto_install: bool = True) -> bool:
        """Complete setup process"""
        print("🚀 RAG System Setup")
        print("=" * 50)

        # Check dependencies
        if not self.check_dependencies():
            if auto_install:
                print("\n🔧 Attempting to install missing dependencies...")
                if not self.install_dependencies():
                    print("\n💡 Please install dependencies manually:")
                    print("   pip install -r requirements.txt")
                    return False

                # Recheck dependencies after installation
                if not self.check_dependencies():
                    print("❌ Dependencies still missing after installation")
                    return False
            else:
                return False

        # Check for documents
        doc_count = len(list(self.docs_dir.glob("*")))
        if doc_count == 0:
            print(f"\n⚠️  No documents found in {self.docs_dir}")
            print("   Please add documents before running setup")
            return False

        print(f"\n📚 Found {doc_count} documents to process")

        # Process documents
        if not self.ingest_documents(force):
            return False

        # Build index
        if not self.build_index():
            return False

        # Verify
        if not self.build_index(verify=True):
            return False

        print("\n✨ Setup complete!")
        print(self.get_stats())
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RAG System - Document Search and Retrieval',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initial setup
  rag_system setup
  
  # Search documents
  rag_system search "your query"
  
  # Process new documents
  rag_system ingest
  rag_system index
  
  # Get statistics
  rag_system stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Complete setup process')
    setup_parser.add_argument('--force', action='store_true',
                            help='Force reprocess all documents')
    setup_parser.add_argument('--no-auto-install', action='store_true',
                            help='Do not automatically install missing dependencies')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Process documents to Markdown')
    ingest_parser.add_argument('--force', action='store_true',
                             help='Force reprocess all documents')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Build vector index')
    index_parser.add_argument('--verify', action='store_true',
                            help='Verify index after building')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--top-k', type=int, default=10,
                             help='Number of results')
    search_parser.add_argument('--format', choices=['markdown', 'json'],
                             default='markdown', help='Output format')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show index statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize system
    rag = RAGSystem()
    
    # Execute command
    if args.command == 'setup':
        success = rag.setup(force=args.force, auto_install=not args.no_auto_install)
        sys.exit(0 if success else 1)
    
    elif args.command == 'ingest':
        success = rag.ingest_documents(force=args.force)
        sys.exit(0 if success else 1)
    
    elif args.command == 'index':
        success = rag.build_index(verify=args.verify)
        sys.exit(0 if success else 1)
    
    elif args.command == 'search':
        result = rag.search(args.query, args.top_k, args.format)
        print(result)
        sys.exit(0)
    
    elif args.command == 'stats':
        print(rag.get_stats())
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()