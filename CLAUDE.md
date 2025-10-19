# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Structured Docs RAG** is a learning project exploring Retrieval-Augmented Generation (RAG) systems for high-stakes domains (legal, medical, regulatory documents). Built with LlamaIndex and Claude 3.5 Sonnet, it demonstrates structure preservation and grounding in source material.

**Project Status**: Learning project demonstrating RAG fundamentals (Phase 1 complete - 8/8 test documents passing)

**Important**: This is a learning foundation for exploring more advanced techniques including tree-sitter for code indexing, graph-based retrieval, and hierarchical document structures. Not production-ready.

**Core Technologies**:
- LlamaIndex (RAG framework)
- Anthropic Claude 3.5 Sonnet (LLM)
- HuggingFace BAAI/bge-base-en-v1.5 (local embeddings)
- DocLing (OCR for image-based PDFs)

## Key Architecture Decisions

### Single-Document RAG (Current Implementation)

The system processes **one document at a time** by design. Early attempts at bulk processing (loading 8 PDFs into a single index) failed catastrophically:
- Mixed contexts from different domains caused text corruption
- Vector search retrieved irrelevant chunks from wrong documents
- No metadata to guide document selection

**Lesson**: Start simple. Single-document RAG first, multi-document later (planned for Phase 2).

### Critical Configuration

```python
# simple_rag.py - Key settings learned from validation
Settings.chunk_size = 512
query_engine = index.as_query_engine(similarity_top_k=5)  # Critical: NOT 3
```

**`similarity_top_k=5` is important** - Default value of 3 caused retrieval failures. The bank evaluation document test failed with `top_k=3` (75%) but succeeded with `top_k=5` (8/8 passing). This 25-point improvement is worth the +33% token cost in high-stakes domains.

### PDF Processing Strategy

**Two-tier approach**:

1. **Native PDFs (digitally created)**: Use LlamaIndex's default PyMuPDF parser
   - Fast (~1-2 seconds)
   - Works for 7/8 test documents

2. **Image-based PDFs (scanned documents)**: Use DocLing with OCR
   - Slow (~55 seconds per 4-page PDF on CPU)
   - Required for scanned documents (e.g., `ost_subcommittee_charter.pdf`)
   - Detection: If you see "0 characters" in chunk output → use DocLing

**DocLing Workflow**:
```bash
# Step 1: Convert PDF to markdown
python convert_pdf_docling.py data/pdf/document.pdf data/converted_markdown --cpu

# Step 2: Query the markdown file
python simple_rag.py --markdown document.md --question "Your question"
```

## Common Development Commands

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Set API key (required)
export ANTHROPIC_API_KEY='your-key-here'  # Mac/Linux
set ANTHROPIC_API_KEY=your-key-here       # Windows
```

### Running the RAG System

```bash
# Default: Paul Graham essay (interactive mode)
python simple_rag.py

# Query a specific PDF (test mode - answer and exit)
python simple_rag.py --pdf us_immigration_case.pdf --question "Why was the petition denied?"

# Interactive mode with a PDF
python simple_rag.py --pdf motion_to_stay.pdf

# Query a DocLing-converted markdown file
python simple_rag.py --markdown ost_subcommittee_charter.md -q "What is the purpose?"
```

### Testing

```bash
# Test all 8 documents with predefined questions
./test_all_pdfs.sh              # Mac/Linux/Git Bash
test_all_pdfs.bat               # Windows

# Save validation results
./test_all_pdfs.sh 2>&1 | tee validation_results.txt
```

### PDF Conversion (for image-based PDFs)

```bash
# Single file
python convert_pdf_docling.py data/pdf/document.pdf data/converted_markdown --cpu

# Batch convert all PDFs in directory
python convert_pdf_docling.py data/pdf/ data/converted_markdown --cpu

# GPU acceleration (if CUDA available)
python convert_pdf_docling.py data/pdf/document.pdf data/converted_markdown
```

## Project Structure

```
structured-docs-rag/
├── simple_rag.py                    # Main RAG pipeline (CLI interface)
├── convert_pdf_docling.py           # DocLing converter for image-based PDFs
├── requirements.txt                 # Python dependencies (Python 3.11+)
├── data/
│   ├── pdf/                         # Source PDF documents (8 legal/regulatory PDFs)
│   ├── text/                        # Text documents (Paul Graham essay)
│   └── converted_markdown/          # DocLing-processed markdown files
├── docs/
│   └── multi-document-query-architecture.md  # Phase 2 design document
├── test_all_pdfs.sh/.bat            # Batch testing scripts
└── rag_index/                       # Auto-generated index cache (gitignored)
```

**Auto-generated files** (in `.gitignore`):
- `rag_index/` - LlamaIndex cache, regenerated on every run
- `__pycache__/` - Python bytecode
- DocLing model cache in `~/.cache/docling`

## Development Patterns

### Adding Support for New Document Types

1. **Test with default parser first**:
   ```bash
   python simple_rag.py --pdf new_document.pdf -q "Test question"
   # Check output: Does it extract text? Or "0 characters"?
   ```

2. **If text extraction fails** (0 characters), use DocLing:
   ```bash
   python convert_pdf_docling.py data/pdf/new_document.pdf data/converted_markdown --cpu
   python simple_rag.py --markdown new_document.md -q "Test question"
   ```

3. **Tune retrieval if needed**:
   - Default: `similarity_top_k=5` (works for 8/8 current documents)
   - If answers lack detail: Increase to 7 or 10
   - If answers are too noisy: Decrease to 3 (rare)

### Quality Validation Checklist

When testing new documents or changes:
- [ ] Grounding: All answers cite source material (no hallucinations)
- [ ] Accuracy: Answers match source PDF when manually verified
- [ ] Retrieval quality: Relevant chunks are retrieved (check verbose mode if debugging)
- [ ] Completeness: Complex questions get multi-faceted answers

### Known Issues

**Pydantic Warnings** (cosmetic only):
```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated
```
- Source: LlamaIndex internals (imported before warning suppression runs)
- Impact: None (functionality unaffected)
- Mitigation: Warnings are suppressed in code but may appear in test output
- Not a blocker for development or deployment

## Future Development (Planned Phases)

### Phase 2: Multi-Document Queries
**Status**: Design complete ([docs/multi-document-query-architecture.md](docs/multi-document-query-architecture.md))

Use LlamaIndex `SubQuestionQueryEngine` to enable:
- Cross-document queries ("Compare ratings across all evaluations")
- Automatic document routing based on metadata
- Synthesized answers from multiple sources

**Key implementation detail**: Create separate query engines per document with rich metadata descriptions, then compose with `SubQuestionQueryEngine` for orchestration.

### Phase 3+: Book-Scale Knowledge Graphs
- Parse table of contents and preserve chapter hierarchies
- Support cross-references within books
- Medical knowledge bases (DSM-5, pharmacology references)
- Graph-based retrieval (Neo4j + Vector hybrid)

## Important Constraints

**High-Stakes Domain Requirements**:
- Zero-hallucination tolerance (all answers must be grounded in source)
- Complete source attribution for validation
- Answer precision > recall (better to say "I don't know" than guess)
- Target: "Answer as if you are the textbook author"

**Performance Trade-offs**:
- `similarity_top_k=5` costs +33% more tokens than `top_k=3`
- Worth it: +25 percentage points accuracy improvement (75% → 100%)
- DocLing is slow (~55s/4 pages) but necessary for scanned PDFs

**Privacy**:
- Local embeddings (HuggingFace) - documents never leave your machine for embedding
- Only LLM queries sent to Anthropic API (with retrieved chunks as context)

## Research Context

This project is part of broader research into structure-preserving RAG:
- [Structure-Preserving RAG Research](https://github.com/dzivkovi/Structure-Preserving-RAG-Research) - Graph-based approaches, hierarchical indexing
- Target applications: Medical textbooks, clinical guidelines, regulatory compliance documents

Training documents sourced from: [LlamaIndex Legal RAG Example](https://github.com/run-llama/llama_cloud_services/blob/main/examples/parse/multimodal/legal_rag.ipynb)

## Test Results (Current)

| Metric | Value |
|--------|-------|
| Test Documents Passing | 8/8 |
| Grounding Quality | All answers sourced from documents |
| Hallucination Detection | Answers verified against source PDFs |
| Average Query Time | 3-5 seconds |
| Index Building Time | 5-10 seconds per PDF |
