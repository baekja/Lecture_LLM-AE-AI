#!/usr/bin/env python3
"""
Document Retrieval System
Performs semantic search on the vector index and returns relevant chunks
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

# Vector database and embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Set to WARNING to reduce noise in output
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentRetriever:
    """Retrieve relevant documents from vector index"""
    
    def __init__(self,
                 index_dir: str = "knowledge/index",
                 model_name: str = "BAAI/bge-m3",
                 top_k: int = 10):
        
        self.index_dir = Path(index_dir)
        self.top_k = top_k
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Connect to ChromaDB
        if not self.index_dir.exists():
            raise FileNotFoundError(f"Index directory not found: {self.index_dir}")
        
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.index_dir),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Get collection
        self.collection_name = "documents"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"Connected to collection: {self.collection_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to collection: {e}")
    
    def search(self, 
               query: str, 
               top_k: Optional[int] = None,
               filter_conditions: Optional[Dict] = None) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_conditions: Optional metadata filters
        
        Returns:
            List of relevant document chunks with metadata
        """
        if not query.strip():
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_conditions
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                    'relevance_score': 1 - (results['distances'][0][i] if results['distances'] else 0)
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def format_results_markdown(self, results: List[Dict]) -> str:
        """Format search results as Markdown"""
        if not results:
            return "# No Results Found\n\nNo relevant documents found for your query."
        
        output = []
        output.append("# Search Results\n")
        output.append(f"**Found {len(results)} relevant chunks**\n")
        output.append("---\n")
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            # Extract source information
            source = metadata.get('original_source', metadata.get('source_file', 'Unknown'))
            doc_type = metadata.get('document_type', 'Document')
            page = metadata.get('page')
            slide = metadata.get('slide')
            
            # Build location string
            location_parts = []
            if page is not None:
                location_parts.append(f"Page {page}")
            if slide is not None:
                location_parts.append(f"Slide {slide}")
            location = f" - {', '.join(location_parts)}" if location_parts else ""
            
            # Format result
            output.append(f"\n## Result {i}\n")
            output.append(f"**Source**: {source}{location}\n")
            output.append(f"**Type**: {doc_type}\n")
            output.append(f"**Relevance**: {result['relevance_score']:.2%}\n\n")
            
            # Content preview (limit length for readability)
            content = result['content']
            if len(content) > 1000:
                content = content[:1000] + "...\n*(truncated)*"
            
            output.append(f"### Content\n\n{content}\n")
            output.append("\n---\n")
        
        return '\n'.join(output)
    
    def format_results_json(self, results: List[Dict]) -> str:
        """Format search results as JSON"""
        formatted = []
        for result in results:
            formatted.append({
                'content': result['content'],
                'source': result['metadata'].get('original_source', 
                                                result['metadata'].get('source_file', 'Unknown')),
                'type': result['metadata'].get('document_type', 'Document'),
                'page': result['metadata'].get('page'),
                'slide': result['metadata'].get('slide'),
                'relevance': round(result['relevance_score'], 3)
            })
        
        return json.dumps(formatted, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict:
        """Get index statistics"""
        count = self.collection.count()
        
        # Get metadata about indexed files
        all_sources = set()
        all_types = set()
        
        # Sample some documents to get metadata
        sample = self.collection.get(limit=100)
        if sample['metadatas']:
            for metadata in sample['metadatas']:
                if 'original_source' in metadata:
                    all_sources.add(metadata['original_source'])
                if 'document_type' in metadata:
                    all_types.add(metadata['document_type'])
        
        return {
            'total_chunks': count,
            'indexed_files': len(all_sources),
            'document_types': list(all_types)
        }

def main():
    """Main execution for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Document Retrieval System')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--index-dir', default='knowledge/index',
                       help='Vector index directory')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of results to return')
    parser.add_argument('--format', choices=['markdown', 'json'], 
                       default='markdown',
                       help='Output format')
    parser.add_argument('--stats', action='store_true',
                       help='Show index statistics')
    parser.add_argument('--filter-type', 
                       help='Filter by document type')
    parser.add_argument('--filter-source',
                       help='Filter by source file')
    
    args = parser.parse_args()
    
    # Initialize retriever
    try:
        retriever = DocumentRetriever(
            index_dir=args.index_dir,
            top_k=args.top_k
        )
    except Exception as e:
        print(f"Error initializing retriever: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Show statistics if requested
    if args.stats:
        stats = retriever.get_statistics()
        print(f"Index Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Indexed files: {stats['indexed_files']}")
        print(f"  Document types: {', '.join(stats['document_types'])}")
        sys.exit(0)
    
    # Check if query provided
    if not args.query:
        print("Error: Please provide a search query", file=sys.stderr)
        print("Usage: python retrieve.py 'your search query'", file=sys.stderr)
        sys.exit(1)
    
    # Build filter conditions if provided
    filter_conditions = {}
    if args.filter_type:
        filter_conditions['document_type'] = args.filter_type
    if args.filter_source:
        filter_conditions['original_source'] = args.filter_source
    
    # Perform search
    results = retriever.search(
        args.query, 
        top_k=args.top_k,
        filter_conditions=filter_conditions if filter_conditions else None
    )
    
    # Format and output results
    if args.format == 'json':
        output = retriever.format_results_json(results)
    else:
        output = retriever.format_results_markdown(results)
    
    print(output)

if __name__ == "__main__":
    main()