# PDF to Markdown Converter

This tool converts PDF documents to clean Markdown format using the Qwen2.5-VL vision-language model.

## Features

- Direct PDF to Markdown conversion using vision-language model
- Preserves document structure, tables, and formatting
- Processes each page individually for better memory management
- Configurable prompts for different page types
- Progress tracking and error handling

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your PDF:**
   - Place your PDF file in the `input/` directory (optional)
   - Or specify the full path when running

## Usage

### Method 1: Interactive Runner
```bash
cd scripts
python run_processor.py
```

### Method 2: Command Line
```bash
cd scripts
python pdf_processor.py path/to/your/file.pdf -o ../output
```

### Method 3: Direct Usage
```bash
cd scripts
python pdf_processor.py ../input/your_file.pdf
```

## Configuration

Edit `scripts/config.py` to customize:

- **Model settings:** Model name, torch dtype, device mapping
- **Processing options:** DPI, batch size, retry settings
- **Output format:** File naming, markdown extensions
- **Prompts:** Customize prompts for different page types

## Output

The tool generates:
- One markdown file per page: `page_001.md`, `page_002.md`, etc.
- Files saved in the `output/` directory (or specified directory)
- Preserves original document structure and formatting

## Directory Structure

```
pdf-processor/
├── input/           # Place PDF files here (optional)
├── output/          # Generated markdown files
├── temp/            # Temporary files (if enabled)
├── scripts/         # Processing scripts
│   ├── pdf_processor.py    # Main processor
│   ├── run_processor.py    # Interactive runner
│   └── config.py           # Configuration
└── requirements.txt # Dependencies
```

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended) or CPU
- ~8GB GPU memory for 7B model
- PyTorch, Transformers, PyMuPDF

## Tips

- Use high-resolution PDFs for better results
- The model works best with text-heavy documents
- Tables and structured content are handled automatically
- Processing time depends on page count and hardware

## Troubleshooting

- **Out of memory:** Reduce batch size or use CPU mode
- **Model loading issues:** Check internet connection and disk space
- **Poor OCR quality:** Increase DPI in config or use higher resolution PDF