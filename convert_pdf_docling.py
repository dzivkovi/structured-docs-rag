#!/usr/bin/env python3
"""
PDF Converter - Convert PDFs to markdown using Docling

Usage:
    python convert_pdf.py Janna/in/book.pdf Janna/ai-prd
    python convert_pdf.py Joseph/in Joseph/project-management
"""

import argparse
import sys
from pathlib import Path

try:
    from docling.datamodel.accelerator_options import (
        AcceleratorDevice,
        AcceleratorOptions,
    )
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
except ImportError:
    print("Error: docling not installed. Run: pip install docling")
    sys.exit(1)


def get_accelerator_device() -> AcceleratorDevice:
    """
    Detect and return best available accelerator device.

    Returns:
        AcceleratorDevice enum value (AUTO for GPU, CPU for fallback)
    """
    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            print(f"✓ GPU Detected: {gpu_name}")
            print(f"✓ CUDA Version: {cuda_version}")
            return AcceleratorDevice.AUTO
        else:
            print("⚠ No GPU detected, using CPU")
            return AcceleratorDevice.CPU
    except ImportError:
        print("⚠ PyTorch not found, using CPU")
        return AcceleratorDevice.CPU


def convert_pdf(input_path: str, output_dir: str, use_gpu: bool = True) -> None:
    """
    Convert PDF to markdown using Docling with optional GPU acceleration.

    Args:
        input_path: Path to input PDF file or directory
        output_dir: Directory to save converted markdown
        use_gpu: Enable GPU acceleration (default: True)
    """
    input_path = Path(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Configure accelerator
    if use_gpu:
        device = get_accelerator_device()
    else:
        device = AcceleratorDevice.CPU
        print("✓ GPU disabled by user, using CPU")

    accelerator_options = AcceleratorOptions(device=device, num_threads=8)

    # Initialize converter with accelerator options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator_options

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Process single file or directory
    pdf_files = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            pdf_files = [input_path]
        else:
            print(f"Error: {input_path} is not a PDF file")
            sys.exit(1)
    elif input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            print(f"Error: No PDF files found in {input_path}")
            sys.exit(1)
    else:
        print(f"Error: {input_path} does not exist")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF(s) to convert")
    print(f"Output directory: {output_path.absolute()}")
    print()

    # Convert each PDF
    for pdf_file in pdf_files:
        print(f"Converting: {pdf_file.name}...")

        try:
            # Convert the document
            result = converter.convert(str(pdf_file))

            # Generate output filename
            output_filename = pdf_file.stem + ".md"
            output_filepath = output_path / output_filename

            # Export to markdown
            markdown = result.document.export_to_markdown()

            # Add metadata header
            header = f"# {pdf_file.stem}\n\n"
            header += f"**Source:** {pdf_file.name}\n"
            header += f"**Pages:** {len(result.document.pages)}\n\n"
            header += "---\n\n"

            full_content = header + markdown

            # Save markdown file
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(full_content)

            print(f"  ✓ Saved: {output_filename}")
            print(f"  ✓ Size: {len(markdown):,} characters")

            # Optionally save structured JSON for advanced use
            json_filepath = output_path / (pdf_file.stem + ".json")
            json_data = result.document.export_to_dict()

            import json

            with open(json_filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            print(f"  ✓ Saved JSON: {json_filepath.name}")
            print()

        except Exception as e:
            print(f"  ✗ Error converting {pdf_file.name}: {e}")
            continue

    print(f"✓ Complete! Converted {len(pdf_files)} PDF(s) to {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to markdown using Docling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single PDF
  python convert_pdf_docling.py data/pdf/ost_subcommittee_charter.pdf data/converted_markdown --cpu

  # Convert all PDFs in a directory
  python convert_pdf_docling.py data/pdf/ data/converted_markdown --cpu

  # With GPU acceleration (if available)
  python convert_pdf_docling.py data/pdf/document.pdf data/converted_markdown

Output:
  - Creates .md files with the converted markdown
  - Creates .json files with structured document data for advanced use
        """,
    )

    parser.add_argument("input", help="Input PDF file or directory containing PDFs")

    parser.add_argument(
        "output_dir", help="Output directory for markdown files (e.g., Janna/ai-prd)"
    )

    parser.add_argument(
        "--cpu", action="store_true", help="Force CPU usage (disable GPU acceleration)"
    )

    args = parser.parse_args()

    convert_pdf(input_path=args.input, output_dir=args.output_dir, use_gpu=not args.cpu)


if __name__ == "__main__":
    main()
