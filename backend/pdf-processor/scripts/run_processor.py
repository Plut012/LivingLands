#!/usr/bin/env python3
"""
Simple runner script for the PDF processor.
"""

import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from pdf_processor import PDFProcessor

def main():
    """Simple interactive runner."""
    print("PDF to Markdown Converter using Qwen2.5-VL")
    print("=" * 50)
    
    # Get PDF file path
    pdf_path = input("Enter path to PDF file: ").strip().strip('"')
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    # Get output directory
    output_dir = input("Enter output directory (default: ../output): ").strip()
    if not output_dir:
        output_dir = script_dir.parent / "output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nInput PDF: {pdf_path}")
    print(f"Output directory: {output_dir}")
    print("\nStarting processing...")
    
    # Process PDF
    processor = PDFProcessor()
    try:
        output_files = processor.process_pdf(pdf_path, output_dir)
        print(f"\n✅ Success! Generated {len(output_files)} markdown files")
        print(f"Files saved to: {output_dir}")
        
        # List output files
        print("\nGenerated files:")
        for file_path in sorted(output_files):
            print(f"  - {file_path.name}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())