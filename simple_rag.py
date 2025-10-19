#!/usr/bin/env python3
"""
Structured Docs RAG - Simple RAG Pipeline

RAG system for querying structured documents using LlamaIndex and
Anthropic Claude. Supports both native PDFs and DocLing-converted
markdown files for image-based PDFs.

Part of the Structured Docs RAG project (work-in-progress).
Created: 2025-10-18
"""

import argparse
import os
import sys
import warnings
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Suppress pydantic warnings from LlamaIndex internals
warnings.filterwarnings("ignore", message=".*validate_default.*")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Simple RAG - Query documents using LlamaIndex and Claude',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Paul Graham essay (default)
  python simple_rag.py
  python simple_rag.py --question "What did the author do growing up?"

  # Legal PDF - Interactive mode
  python simple_rag.py --pdf us_immigration_case.pdf

  # Legal PDF - Test mode (answer and exit)
  python simple_rag.py --pdf us_immigration_case.pdf --question "Why was the petition denied?"

  # Short form
  python simple_rag.py --pdf motion_to_stay.pdf -q "What did Victor George request?"

  # Markdown file (converted from PDF using DocLing)
  python simple_rag.py --markdown ost_subcommittee_charter.md -q "What is the purpose?"
        '''
    )

    parser.add_argument(
        '--pdf',
        type=str,
        default=None,
        help='PDF filename (just the name, not path). If omitted, uses Paul Graham essay.'
    )

    parser.add_argument(
        '--markdown', '--md',
        type=str,
        default=None,
        help='Markdown filename from converted_markdown directory. Alternative to --pdf for image-based PDFs.'
    )

    parser.add_argument(
        '--question', '-q',
        type=str,
        default=None,
        help='Question to ask. If provided, answers and exits (test mode). If omitted, enters interactive mode.'
    )

    args = parser.parse_args()

    # Verify API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set it before running:")
        print("  export ANTHROPIC_API_KEY='your-key-here'  # Mac/Linux")
        print("  set ANTHROPIC_API_KEY=your-key-here      # Windows")
        sys.exit(1)
    print("✓ ANTHROPIC_API_KEY found in environment\n")

    # Check for mutually exclusive options
    if args.pdf and args.markdown:
        print("❌ Error: Cannot specify both --pdf and --markdown")
        sys.exit(1)

    # Determine which data to load
    if args.markdown:
        # Markdown file (converted from image-based PDF)
        md_path = Path(f"./data/converted_markdown/{args.markdown}")
        if not md_path.exists():
            print(f"❌ Error: Markdown file not found: {md_path}\n")
            print("Available markdown files in ./data/converted_markdown/:")
            md_dir = Path("./data/converted_markdown")
            if md_dir.exists():
                mds = sorted(md_dir.glob("*.md"))
                if mds:
                    for m in mds:
                        print(f"  - {m.name}")
                else:
                    print("  (no markdown files found)")
            else:
                print(f"  (directory not found: {md_dir})")
            sys.exit(1)

        reader = SimpleDirectoryReader(input_files=[str(md_path)])
        print(f"📂 Loading: {args.markdown}")
    elif args.pdf:
        # PDF document
        pdf_path = Path(f"./data/pdf/{args.pdf}")
        if not pdf_path.exists():
            print(f"❌ Error: PDF not found: {pdf_path}\n")
            print("Available PDFs in ./data/pdf/:")
            pdf_dir = Path("./data/pdf")
            if pdf_dir.exists():
                pdfs = sorted(pdf_dir.glob("*.pdf"))
                if pdfs:
                    for p in pdfs:
                        print(f"  - {p.name}")
                else:
                    print("  (no PDF files found)")
            else:
                print(f"  (directory not found: {pdf_dir})")
            sys.exit(1)

        reader = SimpleDirectoryReader(input_files=[str(pdf_path)])
        print(f"📂 Loading: {args.pdf}")
    else:
        # Default text document (Paul Graham essay)
        data_path = Path("./data/text")
        if not data_path.exists():
            print(f"❌ Error: Data directory not found: {data_path}")
            sys.exit(1)
        reader = SimpleDirectoryReader(str(data_path))
        print("📂 Loading default text document...")

    # Setup LLM and Embedding (exactly like notebook)
    print("⏳ Setting up models...")
    llm = Anthropic(temperature=0.0, model='claude-3-5-sonnet-20241022')
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

    # Configure global settings (exactly like notebook)
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 512
    print("✓ Models configured\n")

    # Load data (exactly like notebook)
    print("⏳ Loading documents...")
    documents = reader.load_data()
    print(f"✓ Loaded {len(documents)} document(s)\n")

    # Index data (exactly like notebook)
    print("⏳ Building index...")
    index = VectorStoreIndex.from_documents(documents)
    print("✓ Index built\n")

    # Create query engine with improved retrieval settings
    print("⏳ Creating query engine...")
    query_engine = index.as_query_engine(similarity_top_k=5)
    print("✓ Query engine ready\n")

    # Test mode or Interactive mode
    if args.question:
        # Test mode - answer and exit
        print("=" * 70)
        print(f"❓ Question: {args.question}")
        print("=" * 70)

        response = query_engine.query(args.question)

        print(f"\n💡 Answer:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        print()
    else:
        # Interactive mode
        print("=" * 70)
        print("💬 Interactive Mode - Ask questions!")
        print("=" * 70)
        print("Commands: 'quit', 'exit', or 'q' to stop\n")

        while True:
            try:
                question = input("❓ Your question: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break

                response = query_engine.query(question)
                print(f"\n💡 Answer:")
                print("-" * 70)
                print(response)
                print("-" * 70)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n⚠ Error: {e}\n")


if __name__ == "__main__":
    main()
