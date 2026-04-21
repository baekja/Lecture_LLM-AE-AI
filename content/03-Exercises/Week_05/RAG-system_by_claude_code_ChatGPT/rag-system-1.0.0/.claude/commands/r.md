# /r - Document Retrieval Command

Searches through indexed documents and provides relevant information based on your query.

## Usage
```
/r <your search query>
```

## Examples
- `/r system architecture`
- `/r API authentication methods`
- `/r 데이터베이스 설계 패턴`

## Process
1. Run the retrieval script with your query
2. Save results to a temporary file
3. Read and analyze the results
4. Provide a comprehensive answer with citations

## Implementation

When this command is invoked:

1. First, run the retrieval script:
```bash
python3 scripts/retrieve.py "$ARGUMENTS" --top-k 8 > scratch/_search_results.md
```

2. Then read the results file:
```
Read scratch/_search_results.md
```

3. Finally, provide an answer based on the retrieved documents, always including:
   - Direct quotes from relevant sources
   - Source citations in format: (Source: filename, Page/Slide: N)
   - Synthesis of information from multiple sources when applicable

## Notes
- The system searches across all indexed documents (PDF, Word, Excel, PowerPoint, Python code)
- Results are ranked by relevance score
- Always cite sources when providing information from retrieved documents