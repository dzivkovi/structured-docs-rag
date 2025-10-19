# Multi-Document Query Architecture (Phase 2)

*Design plan for implementing cross-document queries in Structured Docs RAG*

**Status**: Planning Phase
**Target**: Phase 2 Implementation
**Prerequisites**: Phase 1 (Single-document RAG) ✅ Complete

---

## Overview

This document outlines the architecture for enabling queries across multiple documents simultaneously in the Structured Docs RAG system. Currently, the system excels at single-document queries with 100% accuracy. Phase 2 will add the ability to:

- Query multiple documents in a single request
- Automatically route questions to relevant documents
- Synthesize answers from multiple sources
- Compare and contrast information across documents

---

## Current Limitations

### Single-Document Architecture

The current `simple_rag.py` implementation:
- ✅ **Strengths**: Clean extraction, 100% accuracy, simple interface
- ❌ **Limitations**:
  - One document per query session
  - No cross-document comparisons
  - No automatic document selection
  - Manual switching between documents required

### Why Bulk Loading Failed

The original attempt to load all 8 PDFs into a single index failed due to:

1. **Text Extraction Corruption**
   - PyMuPDF processed 8 complex PDFs simultaneously
   - Legal documents have tables, multi-column layouts, special formatting
   - Bulk processing caused garbled/encoded text
   - Result: "corrupted or unreadable text" in all responses

2. **Context Confusion**
   - Single index mixed content from different domains
   - Immigration law + energy data + banking regulations + legislative bills
   - No document routing or separation
   - Vector search retrieved irrelevant chunks from wrong documents

3. **Poor Retrieval Quality**
   - No metadata to guide document selection
   - Questions like "What was oil production?" pulled from legal documents
   - Questions like "What burden of proof?" pulled from energy reports

---

## Proposed Solution: SubQuestionQueryEngine

### LlamaIndex Built-in Multi-Document Support

LlamaIndex provides excellent built-in support for multi-document queries via **`SubQuestionQueryEngine`**:

**Key Components**:

1. **SubQuestionQueryEngine** - Core orchestrator that:
   - Breaks complex queries into sub-questions
   - Routes each sub-question to appropriate document(s)
   - Synthesizes answers from multiple sources
   - Handles compare/contrast queries automatically

2. **QueryEngineTool** - Wrapper that:
   - Encapsulates a query engine for a specific document
   - Provides metadata (name, description) for routing
   - Enables LLM to select relevant documents

3. **Automatic Query Decomposition**:
   - LLM analyzes the user's query
   - Generates targeted sub-questions
   - Routes to relevant tools based on metadata
   - Combines results into coherent response

### Architecture Pattern

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Immigration    │  │  Motion to      │  │  Energy Data    │
│  Index (PDF 1)  │  │  Stay Index     │  │  Index (PDF 3)  │
│  + Metadata     │  │  (PDF 2)        │  │  + Metadata     │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ SubQuestionEngine  │
                    │ - Routes queries   │
                    │ - Decomposes Qs    │
                    │ - Synthesizes As   │
                    └────────────────────┘
```

**Benefits**:
- ✅ Clean extraction (one PDF at a time)
- ✅ Document-specific routing via metadata
- ✅ Cross-document synthesis when needed
- ✅ Metadata guides LLM to relevant docs
- ✅ Parallel processing for speed
- ✅ Transparency (see sub-questions in verbose mode)

---

## Implementation Plan

### Phase 2.1: Create Individual Query Engine Tools

**Goal**: Build separate query engines for each document with descriptive metadata

**Document Metadata Structure**:

```python
DOCUMENTS = {
    "immigration_case": {
        "file": "us_immigration_case.pdf",
        "description": "Immigration law case about alien fiancé petition denial (Section 101(a)(15)(K))"
    },
    "motion_to_stay": {
        "file": "motion_to_stay.pdf",
        "description": "Legal motion to stay proceedings filed by Victor George"
    },
    "energy_data": {
        "file": "energy_supply_demand.pdf",
        "description": "U.S. crude oil production and energy supply/demand data 2015-2017"
    },
    # ... etc for all 8 documents
}
```

**Implementation**:

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata

query_engine_tools = []

for name, info in DOCUMENTS.items():
    # Load document
    reader = SimpleDirectoryReader(
        input_files=[f"./data/pdf/{info['file']}"]
    )
    documents = reader.load_data()

    # Create index and query engine
    index = VectorStoreIndex.from_documents(documents)
    engine = index.as_query_engine(similarity_top_k=5)

    # Wrap as tool with metadata
    tool = QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name=name,
            description=info['description']
        )
    )
    query_engine_tools.append(tool)
```

**Key Points**:
- Each document gets its own clean index
- Metadata descriptions guide routing
- `similarity_top_k=5` for better retrieval (learned from Phase 1)

---

### Phase 2.2: Implement SubQuestionQueryEngine

**Goal**: Create orchestrator that routes queries and synthesizes answers

**Implementation**:

```python
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(temperature=0.0, model='claude-3-5-sonnet-20241022')

multi_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    llm=llm,
    use_async=True,  # Parallel sub-question processing
    verbose=True     # Show sub-questions and routing
)
```

**Features**:
- `use_async=True` - Process sub-questions in parallel for speed
- `verbose=True` - Show decomposition and routing decisions
- Claude 3.5 Sonnet for superior query analysis and synthesis

---

### Phase 2.3: Query Flow Example

**User Query**: "What burden of proof standards are mentioned in the legal documents?"

**SubQuestionQueryEngine Process** (verbose mode):

```
🔍 Analyzing query and generating sub-questions...

Generated sub-questions:
1. [immigration_case] What burden of proof standard is mentioned?
2. [motion_to_stay] What burden of proof standard is mentioned?
3. [legal_case_2003] What burden of proof standard is mentioned?

⏳ Querying documents in parallel...

📄 Answers:
1. Preponderance of evidence (petitioner must prove eligibility)
2. Clear and convincing evidence (motion requires higher standard)
3. Beyond reasonable doubt (criminal statute reference)

💡 Final Synthesis:
The legal documents mention three burden of proof standards:
- Preponderance of evidence (immigration_case) - lowest standard
- Clear and convincing evidence (motion_to_stay) - intermediate
- Beyond reasonable doubt (legal_case_2003) - highest standard
```

---

## Example Queries

### Single-Document Routing

**Query**: "Why was the alien fiancé petition denied?"

**Expected Behavior**:
- Engine analyzes metadata
- Identifies only "immigration_case" is relevant
- Routes ONLY to that document
- Returns focused answer

### Multi-Document Synthesis

**Query**: "What financial and regulatory trends are discussed?"

**Expected Behavior**:
- Generates sub-questions for:
  - `energy_data` (oil production trends)
  - `banking_eval` (financial ratings)
  - `foreign_markets` (market analysis)
- Synthesizes comprehensive answer from all three

### Compare/Contrast

**Query**: "Compare the legal standards in the immigration case versus the 2003 legal case"

**Expected Behavior**:
- Generate comparison sub-questions
- Retrieve relevant information from both cases
- Provide structured comparison highlighting differences

---

## Performance Considerations

### Speed Optimization

**Parallel Processing**:
- `use_async=True` enables concurrent sub-question execution
- 3 documents queried simultaneously vs sequentially
- Estimated speedup: 2-3x for multi-doc queries

**Caching** (Future Enhancement):
- Cache individual document indices
- Avoid re-embedding on every run
- Trade memory for speed (indices are ~13MB for 8 docs)

### Token Usage

**Estimated Costs**:

| Query Type | Documents Queried | Tokens per Query | Claude API Cost |
|------------|------------------|------------------|-----------------|
| Single-doc | 1 | ~3,000-4,500 | $0.01-$0.02 |
| Multi-doc (3) | 3 | ~9,000-13,500 | $0.03-$0.05 |
| Multi-doc (8) | 8 | ~24,000-36,000 | $0.08-$0.12 |

**Mitigation**:
- Metadata-driven routing prevents unnecessary queries
- LLM only queries relevant documents
- Most queries will be single or 2-3 document queries

---

## File Structure (After Phase 2)

```
structured-docs-rag/
├── simple_rag.py                      # Phase 1: Single-document queries
├── multi_doc_rag.py                   # Phase 2: Multi-document queries (NEW)
├── convert_pdf_docling.py             # DocLing PDF converter
├── requirements.txt                   # Dependencies
├── README.md                          # Main documentation
├── docs/
│   └── multi-document-query-architecture.md  # This file
├── data/
│   ├── pdf/                           # 8 source PDFs
│   ├── text/                          # Text documents
│   └── converted_markdown/            # DocLing outputs
└── test_scripts/                      # Testing utilities (NEW)
    ├── test_single_docs.sh            # Test each document individually
    └── test_multi_docs.sh             # Test cross-document queries
```

---

## Success Criteria

Phase 2 will be considered successful when:

✅ **Functionality**:
- [ ] Single-document routing works (query goes to correct doc)
- [ ] Multi-document synthesis works (combines answers from multiple sources)
- [ ] Compare/contrast queries work (structured comparisons)
- [ ] Irrelevant documents are NOT queried (efficient routing)

✅ **Performance**:
- [ ] Multi-doc queries complete in <10 seconds (parallel processing)
- [ ] Metadata routing reduces token usage vs querying all docs
- [ ] Answer quality matches or exceeds single-doc quality

✅ **Transparency**:
- [ ] Verbose mode shows sub-questions and routing
- [ ] Users can see which documents contributed to answer
- [ ] Debugging is straightforward

---

## Testing Strategy

### Test Suite 1: Single-Document Routing

Verify that single-doc questions only query relevant document:

```bash
# Should ONLY query immigration_case
python multi_doc_rag.py "Why was the alien fiancé petition denied?"

# Should ONLY query energy_data
python multi_doc_rag.py "What was U.S. crude oil production in 2017?"
```

**Validation**: Check verbose output - only 1 document should be queried

### Test Suite 2: Multi-Document Synthesis

Verify that broad questions query multiple relevant documents:

```bash
# Should query multiple legal documents
python multi_doc_rag.py "What legal standards are mentioned across the documents?"

# Should query financial + energy + markets
python multi_doc_rag.py "What economic trends are discussed?"
```

**Validation**: Multiple sub-questions, synthesized answer

### Test Suite 3: Compare/Contrast

Verify structured comparisons work:

```bash
python multi_doc_rag.py --verbose "Compare the outcomes in the immigration case versus the 2003 legal case"
```

**Validation**: Answer highlights differences/similarities

---

## Risks and Mitigation

### Risk 1: Poor Metadata Descriptions

**Problem**: If metadata doesn't clearly describe document content, routing fails

**Mitigation**:
- Craft detailed, distinctive descriptions for each document
- Include key entities, dates, topics
- Test routing with diverse queries
- Iterate on metadata based on routing failures

### Risk 2: LLM Over-Querying

**Problem**: LLM might query all documents even when not necessary

**Mitigation**:
- Clear, specific metadata
- Use Claude 3.5 Sonnet (superior reasoning)
- Monitor verbose output to catch over-querying
- Tune prompts if needed

### Risk 3: Synthesis Quality

**Problem**: Multi-doc answers might lose precision or introduce hallucinations

**Mitigation**:
- Test extensively with known correct answers
- Compare multi-doc answers to single-doc answers
- Use same `similarity_top_k=5` as Phase 1
- Maintain grounding requirement (cite sources)

---

## Future Enhancements (Phase 3+)

**Book-Scale Knowledge Graphs**:
- Parse table of contents and chapter hierarchies
- Preserve cross-references within books
- Navigate by structure (TOC) + semantics (vector)

**Medical Knowledge Bases**:
- Diagnostic criteria from DSM-5, ICD-11
- Drug interaction detection
- Evidence-based treatment protocols

**Graph-Based Retrieval**:
- Neo4j + Vector hybrid approach
- Store hierarchical document structure
- Traverse graph for context preservation

---

## References

**LlamaIndex Documentation**:
- [SubQuestionQueryEngine](https://docs.llamaindex.ai/en/stable/examples/query_engine/sub_question_query_engine/)
- [QueryEngineTool](https://docs.llamaindex.ai/en/stable/api_reference/tools/query_engine/)
- [Multi-Document Queries](https://docs.llamaindex.ai/en/stable/examples/query_transformations/SimpleIndexDemo-multidoc/)

**Related Documents**:
- [../README.md](../README.md) - Main project documentation
- [../IMPROVEMENTS_SUMMARY.md](../IMPROVEMENTS_SUMMARY.md) - Phase 1 improvements
- [../validation_report.md](../validation_report.md) - Single-document validation results

**Original Research**:
- [../../analysis/2025-10-18/04-multi-document-rag-research-and-implementation-plan.md](../../analysis/2025-10-18/04-multi-document-rag-research-and-implementation-plan.md)

---

## Next Steps

1. **Finalize Phase 1 Documentation** - Ensure single-doc system is fully documented
2. **Review This Architecture** - Get feedback on approach
3. **Prototype with 3 Documents** - Proof of concept with subset
4. **Full Implementation** - All 8 documents with complete test suite
5. **Benchmark Performance** - Compare speed and accuracy vs single-doc
6. **Production Deployment** - CLI interface matching simple_rag.py quality

**Estimated Implementation Time**: 2-3 hours for complete Phase 2

---

*Last Updated: 2025-10-19*
