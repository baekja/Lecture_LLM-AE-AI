#!/usr/bin/env python3
"""
Build Embedding Index for RAG System
Creates and maintains a vector database from Markdown documents
"""

import os
import sys
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import hashlib

# Vector database and embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken

# Text processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingIndexBuilder:
    """Build and maintain vector index for documents"""
    
    def __init__(self, 
                 input_dir: str = "knowledge/md",
                 index_dir: str = "knowledge/index",
                 model_name: str = "BAAI/bge-m3",
                 chunk_size: int = 500,
                 chunk_overlap: int = 100):
        
        self.input_dir = Path(input_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model (multilingual support)
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Text chunking parameters
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.index_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = "documents"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"created": datetime.now().isoformat()}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        # Track indexed files
        self.metadata_file = self.index_dir / "_index_metadata.json"
        self.metadata = self.load_metadata()
    
    def load_metadata(self) -> Dict:
        """Load indexing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"files": {}, "stats": {}}
    
    def save_metadata(self):
        """Save indexing metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def get_file_hash(self, filepath: Path) -> str:
        """Calculate file hash for change detection"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def extract_metadata_from_markdown(self, content: str, filepath: Path) -> Dict:
        """Extract metadata from markdown headers"""
        metadata = {
            "source_file": filepath.name,
            "file_path": str(filepath),
            "indexed_at": datetime.now().isoformat()
        }
        
        # Extract document type and source from markdown headers
        lines = content.split('\n')
        for line in lines[:20]:  # Check first 20 lines for metadata
            if line.startswith('**Source**:'):
                metadata['original_source'] = line.replace('**Source**:', '').strip()
            elif line.startswith('**Type**:'):
                metadata['document_type'] = line.replace('**Type**:', '').strip()
            elif line.startswith('**Pages**:'):
                metadata['pages'] = line.replace('**Pages**:', '').strip()
        
        return metadata
    
    def chunk_markdown(self, content: str, metadata: Dict) -> List[Document]:
        """Split markdown content into chunks with metadata"""
        
        # Use RecursiveCharacterTextSplitter for better structure preservation
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n## ",  # H2 headers (pages, major sections)
                "\n### ", # H3 headers (subsections)
                "\n#### ", # H4 headers
                "\n\n",   # Paragraphs
                "\n",     # Lines
                " ",      # Words
                ""        # Characters
            ]
        )
        
        # Split the content
        chunks = splitter.split_text(content)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            # Try to extract page number from chunk
            page_num = None
            if "## Page " in chunk:
                try:
                    page_line = [l for l in chunk.split('\n') if l.startswith('## Page ')][0]
                    page_num = int(page_line.replace('## Page ', '').strip())
                except:
                    pass
            
            # Try to extract slide number
            slide_num = None
            if "## Slide " in chunk:
                try:
                    slide_line = [l for l in chunk.split('\n') if l.startswith('## Slide ')][0]
                    slide_num = int(slide_line.replace('## Slide ', '').strip())
                except:
                    pass
            
            # Create chunk metadata
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": f"{metadata['source_file']}_{i}",
                "chunk_index": i,
                "chunk_size": len(chunk)
            })
            
            # Only add page/slide if they exist
            if page_num is not None:
                chunk_metadata["page"] = page_num
            if slide_num is not None:
                chunk_metadata["slide"] = slide_num
            
            documents.append(Document(
                page_content=chunk,
                metadata=chunk_metadata
            ))
        
        return documents
    
    def index_file(self, filepath: Path) -> int:
        """Index a single markdown file"""
        logger.info(f"Indexing: {filepath.name}")
        
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        metadata = self.extract_metadata_from_markdown(content, filepath)
        
        # Chunk the content
        documents = self.chunk_markdown(content, metadata)
        
        if not documents:
            logger.warning(f"No chunks created for {filepath.name}")
            return 0
        
        # Generate embeddings
        texts = [doc.page_content for doc in documents]
        embeddings = self.model.encode(texts, 
                                       show_progress_bar=False,
                                       convert_to_tensor=False).tolist()
        
        # Prepare data for ChromaDB
        ids = [doc.metadata['chunk_id'] for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        logger.info(f"Indexed {len(documents)} chunks from {filepath.name}")
        return len(documents)
    
    def remove_file_chunks(self, filepath: Path):
        """Remove all chunks from a file from the index"""
        file_key = filepath.name
        
        # Get all chunk IDs for this file
        results = self.collection.get(
            where={"source_file": file_key}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Removed {len(results['ids'])} chunks from {file_key}")
    
    def build_index(self, force: bool = False):
        """Build or update the vector index"""
        if not self.input_dir.exists():
            logger.error(f"Input directory does not exist: {self.input_dir}")
            return
        
        total_chunks = 0
        files_indexed = 0
        files_skipped = 0
        
        # Process all markdown files
        for filepath in self.input_dir.glob('*.md'):
            if filepath.name.startswith('_'):  # Skip metadata files
                continue
            
            # Check if file needs indexing
            file_hash = self.get_file_hash(filepath)
            file_key = filepath.name
            
            if not force and file_key in self.metadata.get("files", {}):
                if self.metadata["files"][file_key]["hash"] == file_hash:
                    logger.info(f"Skipping unchanged file: {filepath.name}")
                    files_skipped += 1
                    continue
            
            # Remove old chunks if file was previously indexed
            if file_key in self.metadata.get("files", {}):
                self.remove_file_chunks(filepath)
            
            # Index the file
            chunks_added = self.index_file(filepath)
            
            # Update metadata
            if "files" not in self.metadata:
                self.metadata["files"] = {}
            
            self.metadata["files"][file_key] = {
                "hash": file_hash,
                "indexed_at": datetime.now().isoformat(),
                "chunks": chunks_added
            }
            
            total_chunks += chunks_added
            files_indexed += 1
        
        # Update statistics
        self.metadata["stats"] = {
            "total_files": files_indexed + files_skipped,
            "total_chunks": self.collection.count(),
            "last_updated": datetime.now().isoformat(),
            "embedding_model": "BAAI/bge-m3"
        }
        
        # Save metadata
        self.save_metadata()
        
        logger.info(f"Indexing complete: {files_indexed} files indexed, "
                   f"{files_skipped} skipped, {total_chunks} new chunks added")
        logger.info(f"Total chunks in collection: {self.collection.count()}")
    
    def verify_index(self):
        """Verify the index is working correctly"""
        count = self.collection.count()
        logger.info(f"Collection contains {count} chunks")
        
        # Test query
        if count > 0:
            test_query = "시스템 구조"
            logger.info(f"Testing query: '{test_query}'")
            
            query_embedding = self.model.encode([test_query])[0].tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            if results['documents'][0]:
                logger.info(f"Test query returned {len(results['documents'][0])} results")
                for i, doc in enumerate(results['documents'][0][:2]):
                    preview = doc[:100] + "..." if len(doc) > 100 else doc
                    logger.info(f"  Result {i+1}: {preview}")
            else:
                logger.warning("Test query returned no results")

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Embedding Index')
    parser.add_argument('--input-dir', default='knowledge/md',
                       help='Input directory with Markdown files')
    parser.add_argument('--index-dir', default='knowledge/index',
                       help='Output directory for vector index')
    parser.add_argument('--force', action='store_true',
                       help='Force rebuild entire index')
    parser.add_argument('--verify', action='store_true',
                       help='Verify index after building')
    parser.add_argument('--chunk-size', type=int, default=500,
                       help='Chunk size for text splitting')
    parser.add_argument('--chunk-overlap', type=int, default=100,
                       help='Overlap between chunks')
    
    args = parser.parse_args()
    
    builder = EmbeddingIndexBuilder(
        input_dir=args.input_dir,
        index_dir=args.index_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    builder.build_index(force=args.force)
    
    if args.verify:
        builder.verify_index()

if __name__ == "__main__":
    main()