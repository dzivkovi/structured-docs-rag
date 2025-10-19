#!/usr/bin/env python3
"""
Legal Document RAG Query System

A standalone script that uses LlamaIndex to build a RAG pipeline over legal documents,
then queries them using Anthropic's Claude. This consolidates learnings from the
Jupyter notebooks into a clean, production-ready script.

Author: Daniel
Date: 2025-10-18
"""

import os
import sys
from pathlib import Path
from typing import Optional

# LlamaIndex imports
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic


class LegalRAGSystem:
    """RAG system for querying legal documents using LlamaIndex and Claude."""

    def __init__(
        self,
        documents_dir: str = "../third_party/HuggingFace/Training Documents",
        index_dir: str = "./rag_index",
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        llm_model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
    ):
        """
        Initialize the Legal RAG System.

        Args:
            documents_dir: Path to directory containing PDF documents
            index_dir: Path to store/load the vector index
            embedding_model: HuggingFace embedding model name
            llm_model: Anthropic Claude model name
            temperature: LLM temperature for response generation
        """
        self.documents_dir = Path(documents_dir)
        self.index_dir = Path(index_dir)
        self.embedding_model_name = embedding_model
        self.llm_model = llm_model
        self.temperature = temperature

        # Will be initialized later
        self.embedding_model = None
        self.llm = None
        self.index = None
        self.query_engine = None

    def setup(self):
        """Set up the RAG system components."""
        print("=" * 70)
        print("🚀 Legal Document RAG System - Setup")
        print("=" * 70)

        # 1. Verify API key
        self._verify_api_key()

        # 2. Initialize embedding model
        self._initialize_embedding_model()

        # 3. Initialize LLM
        self._initialize_llm()

        # 4. Load or create index
        self._load_or_create_index()

        # 5. Create query engine
        self._create_query_engine()

        print("\n✓ Setup complete! Ready to query legal documents.\n")

    def _verify_api_key(self):
        """Verify that ANTHROPIC_API_KEY is set in environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables.\n"
                "Please set it before running: export ANTHROPIC_API_KEY='your-key-here'"
            )
        print("✓ ANTHROPIC_API_KEY found in environment")

    def _initialize_embedding_model(self):
        """Initialize HuggingFace embedding model."""
        print(f"⏳ Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = HuggingFaceEmbedding(
            model_name=self.embedding_model_name
        )
        print(f"✓ Embedding model loaded: {self.embedding_model_name}")

    def _initialize_llm(self):
        """Initialize Anthropic Claude LLM."""
        print(f"⏳ Initializing Claude LLM: {self.llm_model}")
        self.llm = Anthropic(
            temperature=self.temperature,
            model=self.llm_model,
        )
        print(f"✓ Claude LLM initialized: {self.llm_model}")

    def _load_or_create_index(self):
        """Load existing index or create new one from documents."""
        if self.index_dir.exists() and (self.index_dir / "docstore.json").exists():
            print(f"⏳ Loading existing index from: {self.index_dir}")
            self._load_index()
        else:
            print(f"⏳ Creating new index from documents in: {self.documents_dir}")
            self._create_index()

    def _load_index(self):
        """Load pre-built index from disk."""
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.index_dir)
            )
            self.index = load_index_from_storage(
                storage_context, embed_model=self.embedding_model
            )
            print(f"✓ Index loaded from: {self.index_dir}")
        except Exception as e:
            print(f"⚠ Failed to load index: {e}")
            print("⏳ Creating new index instead...")
            self._create_index()

    def _create_index(self):
        """Create new index from PDF documents."""
        # Load documents
        print(f"⏳ Loading documents from: {self.documents_dir}")
        if not self.documents_dir.exists():
            raise FileNotFoundError(
                f"Documents directory not found: {self.documents_dir}\n"
                f"Current working directory: {os.getcwd()}"
            )

        loader = SimpleDirectoryReader(
            input_dir=str(self.documents_dir),
            recursive=True,
            required_exts=[".pdf"],
        )
        documents = loader.load_data()
        print(f"✓ Loaded {len(documents)} document chunks from PDFs")

        # Create index
        print("⏳ Building vector index (this may take a minute)...")
        self.index = VectorStoreIndex.from_documents(
            documents,
            embed_model=self.embedding_model,
        )

        # Persist index
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index.storage_context.persist(persist_dir=str(self.index_dir))
        print(f"✓ Index created and saved to: {self.index_dir}")

    def _create_query_engine(self):
        """Create query engine with Claude LLM."""
        print("⏳ Creating query engine with Claude...")
        self.query_engine = self.index.as_query_engine(
            llm=self.llm,
            similarity_top_k=3,  # Retrieve top 3 most relevant chunks
        )
        print("✓ Query engine created with Claude 3.5 Sonnet")

    def query(self, question: str, verbose: bool = True) -> str:
        """
        Query the legal documents.

        Args:
            question: Question to ask about the documents
            verbose: Whether to print the question

        Returns:
            Answer string from Claude
        """
        if verbose:
            print("\n" + "=" * 70)
            print(f"❓ Question: {question}")
            print("=" * 70)

        response = self.query_engine.query(question)

        if verbose:
            print(f"\n💡 Answer:\n{response.response}\n")

        return response.response

    def run_test_questions(self):
        """Run a set of predefined test questions to validate the system."""
        print("\n" + "=" * 70)
        print("🧪 Running Test Questions")
        print("=" * 70 + "\n")

        test_questions = [
            {
                "category": "Immigration Law",
                "question": "Why was the alien fiancé petition denied?",
            },
            {
                "category": "Legal Procedure",
                "question": "What did Victor George request from the court, and was it granted?",
            },
            {
                "category": "Energy Data",
                "question": "What was the trend in U.S. crude oil production from 2015 to 2017?",
            },
            {
                "category": "Legal Citations",
                "question": "What does Section 101(a)(15)(K) of the Immigration and Nationality Act state?",
            },
            {
                "category": "Cross-Document",
                "question": "What are the burden of proof standards mentioned across the legal documents?",
            },
        ]

        for i, test in enumerate(test_questions, 1):
            print(f"\n{'─' * 70}")
            print(f"Test {i}/{len(test_questions)} - Category: {test['category']}")
            print(f"{'─' * 70}")
            self.query(test["question"], verbose=True)

        print("\n" + "=" * 70)
        print("✅ All test questions completed!")
        print("=" * 70 + "\n")

    def interactive_mode(self):
        """Run in interactive mode where user can ask questions."""
        print("\n" + "=" * 70)
        print("💬 Interactive Query Mode")
        print("=" * 70)
        print("\nType your questions about the legal documents.")
        print("Commands:")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'test' to run predefined test questions")
        print("=" * 70 + "\n")

        while True:
            try:
                question = input("❓ Your question: ").strip()

                if not question:
                    continue

                if question.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!\n")
                    break

                if question.lower() == "test":
                    self.run_test_questions()
                    continue

                self.query(question, verbose=True)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n⚠ Error: {e}\n")


def main():
    """Main entry point."""
    # Parse command line arguments (simple version)
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        print("\nUsage:")
        print("  python legal_rag_query.py           # Interactive mode")
        print("  python legal_rag_query.py test      # Run test questions only")
        print("  python legal_rag_query.py --help    # Show this help")
        return

    # Initialize the RAG system
    rag = LegalRAGSystem()

    try:
        # Setup (load models, create/load index)
        rag.setup()

        # Determine mode
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            # Test mode only
            rag.run_test_questions()
        else:
            # Interactive mode
            rag.interactive_mode()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
