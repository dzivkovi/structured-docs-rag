# Structured Docs RAG

*Precision-focused RAG pipeline for legal, medical, and regulatory documents using LlamaIndex and Claude*

A Retrieval-Augmented Generation (RAG) system (work-in-progress) designed for **high-stakes domains** where absolute correctness is critical. This project demonstrates structure-preserving document indexing and retrieval using LlamaIndex, with a focus on diverse document types as a learning foundation for future applications in medical knowledge bases, regulatory compliance, and book-scale structured documents.

**Success Rate**: 100% (8/8 test documents) ✅

---

## Table of Contents

- [Source & Attribution](#source--attribution)
- [Training Documents](#training-documents)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the RAG Pipeline](#running-the-rag-pipeline)
- [DocLing Integration](#docling-integration)
- [Focus: Getting LlamaIndex to Work](#focus-getting-llamaindex-to-work)
- [Future Vision](#future-vision)
- [Performance Metrics](#performance-metrics)

---

## Source & Attribution

### Training Documents - PDF Dataset

The PDFs in the [data/pdf/](data/pdf/) folder were downloaded from the LlamaIndex example repository:

**[Building a RAG Pipeline over Legal Documents](https://github.com/run-llama/llama_cloud_services/blob/main/examples/parse/multimodal/legal_rag.ipynb)**

This multimodal RAG example demonstrates:
- Parsing complex legal PDFs with tables, footnotes, and nested clauses
- Building hierarchical document representations
- Multimodal retrieval combining text and document structure
- Question-answering over legal contracts and regulatory documents

**Note**: These documents (legal, regulatory, financial, legislative) serve as a **learning foundation**. The system is designed to scale to:
- Medical textbooks and diagnostic manuals (DSM-5, ICD-11, pharmacology references)
- Regulatory compliance documents (FDA guidelines, clinical practice guidelines)
- Book-scale knowledge bases with hierarchical navigation
- Sports regulations and technical specifications

### Research Background

This project is part of ongoing research into structure-preserving RAG systems:

- **[Structure-Preserving RAG Research](https://github.com/dzivkovi/Structure-Preserving-RAG-Research)** - Exploring graph-based approaches, hierarchical indexing, and precision-focused retrieval for high-stakes domains
- **[Structured Documents RAG](https://github.com/dzivkovi/Structured-Documents-RAG)** - Implementation research for books, medical documents, and complex technical texts

**Research Goals**:
- Preserve document structure (table of contents, section hierarchies, cross-references)
- Achieve near-zero hallucination through grounding in source material
- Enable "book author-level" expertise in Q&A responses
- Support multi-document knowledge graphs for complex queries

---

## Training Documents

The current dataset includes 8 legal PDFs spanning various document types:

| Document | Type | Size | Description |
|----------|------|------|-------------|
| `us_immigration_case.pdf` | Legal Case | 100KB | Immigration petition denial case with statutory references |
| `motion_to_stay.pdf` | Legal Motion | 62KB | Court motion filings with case number references |
| `energy_supply_demand.pdf` | Regulatory | 454KB | Energy production statistics and regulatory analysis |
| `a_2003-19.pdf` | Legal Reference | 139KB | Tax code references with multiple IRC section citations |
| `barre_savings_bank_evaluation.pdf` | Financial | 189KB | CRA bank evaluation with performance ratings |
| `foreign_markets.pdf` | Market Analysis | 52KB | International energy market analysis |
| `oc_bill_offshore_drilling.pdf` | Legislative | 243KB | Marijuana Opportunity Reinvestment and Expungement (MORE) Act |
| `ost_subcommittee_charter.pdf` | Government Charter | 187KB | Ocean Science and Technology Subcommittee charter (image-based PDF) |

**Test Coverage**: All 8 documents successfully answer domain-specific questions with 100% grounding in source material.

---

## Project Structure

```
structured-docs-rag/
├── simple_rag.py                      # Main RAG pipeline (CLI interface)
├── convert_pdf_docling.py             # DocLing converter for image-based PDFs
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── .gitignore                         # Git ignore patterns
├── data/
│   ├── pdf/                           # Source PDF documents (8 files)
│   ├── text/                          # Text documents (Paul Graham essay)
│   └── converted_markdown/            # DocLing-processed markdown files
├── docs/
│   └── multi-document-query-architecture.md  # Phase 2 design document
├── test_all_pdfs.bat                  # Windows batch testing script
├── test_all_pdfs.sh                   # Mac/Linux/Git Bash testing script
├── validation_report.md               # Detailed validation analysis
└── IMPROVEMENTS_SUMMARY.md            # System improvements documentation
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Quick Start

```bash
# Clone repository
cd structured-docs-rag

# Install dependencies
pip install -r requirements.txt

# Set up API key
export ANTHROPIC_API_KEY='your-key-here'  # Mac/Linux
set ANTHROPIC_API_KEY=your-key-here       # Windows
```

### Manual Installation

If you prefer to install dependencies manually:

```bash
# Core RAG Framework
pip install llama-index-core llama-index-readers-file

# LLM Integration
pip install llama-index-llms-anthropic anthropic

# Embeddings
pip install llama-index-embeddings-huggingface huggingface-hub torch torchvision

# PDF Conversion (for image-based PDFs)
pip install docling docling-core docling-ibm-models docling-parse

# Data Validation
pip install pydantic pydantic-settings
```

See [requirements.txt](requirements.txt) for specific version numbers.

---

## Running the RAG Pipeline

### Basic Usage

```bash
# Default: Paul Graham essay (interactive mode)
python simple_rag.py

# Query a specific legal PDF (test mode - answer and exit)
python simple_rag.py --pdf us_immigration_case.pdf --question "Why was the petition denied?"

# Interactive mode with a legal PDF
python simple_rag.py --pdf motion_to_stay.pdf

# Short form
python simple_rag.py --pdf energy_supply_demand.pdf -q "What was the production trend from 2015-2017?"
```

### Sample Test Questions

#### Immigration Case
```bash
python simple_rag.py --pdf us_immigration_case.pdf --question "Why was the alien fiancé petition denied?"
```
**Expected Answer**: Petitioner was lawful permanent resident, not U.S. citizen

#### Bank Evaluation
```bash
python simple_rag.py --pdf barre_savings_bank_evaluation.pdf --question "What is the overall rating for this bank?"
```
**Expected Answer**: "Satisfactory" rating with performance criteria breakdown

#### Energy Analysis
```bash
python simple_rag.py --pdf energy_supply_demand.pdf --question "What was the trend in U.S. crude oil production from 2015 to 2017?"
```
**Expected Answer**: Decreasing trend - 9.42M → 8.86M → 8.78M barrels/day

### Batch Testing

Test all 8 documents with predefined questions:

```bash
# Windows
test_all_pdfs.bat

# Mac/Linux/Git Bash
./test_all_pdfs.sh
```

---

## DocLing Integration

### Why DocLing?

Traditional PDF parsers (PyMuPDF, pypdf) fail on **image-based PDFs** (scanned documents) because they only extract embedded text. DocLing uses OCR and deep learning models to:

- Extract text from scanned/image-based PDFs
- Understand document layout (headers, sections, tables)
- Preserve document structure during conversion
- Handle complex multi-column layouts

### When to Use DocLing

**Use DocLing if**:
- PDF is scanned/image-based (no embedded text)
- LlamaIndex returns empty chunks (0 characters)
- Document has complex layouts or diagrams

**Use default parser if**:
- PDF is digitally created (has embedded text)
- LlamaIndex successfully extracts content
- Speed is critical (DocLing is slower ~55s for 4 pages)

### DocLing Workflow

#### Step 1: Convert PDF to Markdown

```bash
# Single file conversion
python convert_pdf_docling.py data/pdf/ost_subcommittee_charter.pdf data/converted_markdown --cpu

# Directory conversion (all PDFs)
python convert_pdf_docling.py data/pdf/ data/converted_markdown --cpu

# GPU acceleration (if available)
python convert_pdf_docling.py data/pdf/document.pdf data/converted_markdown
```

**Output**:
- `document.md` - Converted markdown with preserved structure
- `document.json` - Structured data export for advanced use

#### Step 2: Query the Markdown File

```bash
python simple_rag.py --markdown ost_subcommittee_charter.md --question "What is the purpose of this subcommittee?"
```

### Detection Method

If you see this pattern, use DocLing:

```
Loaded 4 chunks
Chunk 0: 0 characters
Chunk 1: 0 characters
# → Image-based PDF detected, use DocLing workflow
```

### Performance Characteristics

| Conversion Method | Speed | Image PDFs | Text PDFs | Structure Preservation |
|-------------------|-------|------------|-----------|------------------------|
| PyMuPDF (default) | Fast (~1s) | ❌ Fails | ✅ Excellent | Good |
| DocLing | Slow (~55s/4 pages) | ✅ Excellent | ✅ Excellent | Excellent |

---

## Focus: Getting LlamaIndex to Work

This project represents a learning journey in building RAG systems with LlamaIndex. Key learnings and challenges overcome:

### Initial Challenges

1. **Bulk Document Processing Failed**
   - Loading 8 PDFs into single index → corrupted text
   - Root cause: Mixed contexts from different legal domains
   - Solution: One PDF at a time (simple_rag.py approach)

2. **Retrieval Quality Issues**
   - Default `similarity_top_k=3` missed relevant chunks
   - Bank evaluation rating existed but wasn't retrieved
   - Solution: Increased to `similarity_top_k=5` for better recall

3. **Image-based PDF Parsing**
   - Traditional parsers returned 0 characters for scanned PDFs
   - Solution: DocLing integration with OCR capability

4. **Pydantic Warnings**
   - LlamaIndex internals caused cosmetic warnings
   - Solution: Warning suppression for clean output

### Architecture Decisions

**Why LlamaIndex?**
- Mature, well-documented RAG framework
- Flexible index types (Vector, Tree, Graph)
- Strong integration ecosystem (Anthropic, HuggingFace, OpenAI)
- Active development and community support
- Clear path to advanced features (SubQuestionQueryEngine for multi-doc queries)

**Why Claude 3.5 Sonnet?**
- Superior reasoning for complex legal/medical queries
- Excellent instruction following
- Strong citation and grounding capabilities
- Production-ready via Anthropic API

**Why Local Embeddings?**
- HuggingFace BAAI/bge-base-en-v1.5 runs locally
- No API costs for embedding generation
- Privacy-preserving (documents never leave your machine)
- Fast enough for single-document use cases

### Success Metrics

**Validation Results**:
- Initial success rate: 6/8 (75%)
- After improvements: 8/8 (100%) ✅
- Improvement: +25 percentage points

**Key Improvements**:
1. ✅ Better retrieval (`similarity_top_k=5`)
2. ✅ Image PDF support (DocLing integration)
3. ✅ Clean output (warning suppression)

See [validation_report.md](validation_report.md) for detailed analysis of each document.

### Lessons Learned

1. **Start Simple** - Single-document RAG first, multi-document later
2. **Validate Early** - Test with diverse document types (native PDFs, scanned PDFs, complex layouts)
3. **Measure Everything** - Track grounding, accuracy, retrieval quality
4. **Preprocessing Matters** - Complex documents need specialized tools (DocLing)
5. **Default Settings Aren't Optimal** - Tune `similarity_top_k`, chunk sizes for your domain

---

## Future Vision

This project is the foundation for more ambitious structure-preserving RAG systems:

### Phase 2: Multi-Document Queries (Planned)

Implement LlamaIndex `SubQuestionQueryEngine` to enable:
- Cross-document queries ("Compare ratings across all bank evaluations")
- Synthesized answers from multiple sources
- Document routing based on query intent

**Research**: See [./analysis/2025-10-18/04-multi-document-rag-research-and-implementation-plan.md](./analysis/2025-10-18/04-multi-document-rag-research-and-implementation-plan.md)

### Phase 3: Book-Scale Knowledge Graphs

- Parse book table of contents and chapter hierarchies
- Preserve cross-references ("see Chapter 5, Section 2.3")
- Navigate via structure (TOC) + semantics (vector search)
- Handle diagrams and figures with multimodal models

### Phase 4: Medical Knowledge Bases

Target applications from Structure-Preserving RAG Research:

- Psychiatric textbooks (DSM-5, ICD-11 diagnostic criteria)
- Pharmacology references (drug interactions, dosing guidelines)
- Clinical practice guidelines (evidence-based treatment protocols)
- Medical assessment tools (diagnostic criteria, scoring systems)

**Requirements**:
- 95%+ precision for medication interaction detection
- Complete source attribution for clinical validation
- Zero hallucination tolerance
- Answer as if you are the textbook author

### Phase 5: Graph-based Retrieval

Explore Neo4j + Vector hybrid approach:
- Store hierarchical document structure in graph
- Vector embeddings for semantic search
- Traverse graph for context preservation
- Combine structural + semantic signals for retrieval

---

## Project Status

**Current State**: Work-in-progress (Phase 1 complete)

✅ **Completed (Phase 1)**:

- Single-document RAG with 100% accuracy (8/8 test documents)
- Image-based PDF support via DocLing OCR
- Professional CLI interface with argparse
- Comprehensive validation and testing
- Complete documentation

🚧 **In Progress**:

- Documentation refinements
- Testing with additional document types

📋 **Planned** (See [docs/multi-document-query-architecture.md](docs/multi-document-query-architecture.md)):

- **Phase 2**: Multi-document queries with SubQuestionQueryEngine
- **Phase 3**: Book-scale knowledge graphs with TOC preservation
- **Phase 4**: Medical knowledge bases (DSM-5, pharmacology)
- **Phase 5**: Graph-based retrieval (Neo4j + Vector hybrid)

---

## Performance Metrics

### Accuracy

| Metric | Value |
|--------|-------|
| Document Success Rate | 100% (8/8) |
| Grounding Quality | Excellent - all answers sourced from documents |
| Hallucination Rate | 0% (verified against source PDFs) |

### Speed

| Operation | Time |
|-----------|------|
| Document Loading | ~2-3 seconds |
| Index Building | ~5-10 seconds per PDF |
| Query Execution | ~3-5 seconds per question |
| DocLing Conversion | ~55 seconds per 4-page PDF (CPU) |

### Token Usage

| Configuration | Tokens per Query |
|---------------|------------------|
| similarity_top_k=3 | ~2,000-3,000 |
| similarity_top_k=5 | ~3,000-4,500 |

**Trade-off**: +33% token cost for +25% accuracy improvement (worth it for high-stakes domains)

---

## Contributing

This is a research project exploring structure-preserving RAG systems. Feedback and suggestions welcome!

**Areas of Interest**:
- Medical document parsing strategies
- Graph-based retrieval approaches
- Multi-document query architectures
- Complex document preprocessing (diagrams, tables, figures)

---

## License

This project uses training documents from the LlamaIndex repository (Apache 2.0 license). See original source for licensing details.

---

## Contact

For questions about structure-preserving RAG research or collaboration opportunities, please open an issue.

---

**Built with** ❤️ **using LlamaIndex, Claude 3.5 Sonnet, and DocLing**
