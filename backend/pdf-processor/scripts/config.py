"""Configuration settings for PDF processor."""

# Model configuration
MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"
TORCH_DTYPE = "float16"  # Options: float16, float32, bfloat16
DEVICE_MAP = "auto"  # Let transformers handle device placement

# Processing configuration
DPI = 300  # Resolution for PDF to image conversion
MAX_BATCH_SIZE = 1  # Process one page at a time to manage memory
SAVE_TEMP_IMAGES = False  # Whether to keep temporary image files

# Output configuration
OUTPUT_FORMAT = "page"  # Options: "page" (one file per page), "section" (detect sections)
FILE_PREFIX = "page_"  # Prefix for output markdown files
MARKDOWN_EXTENSION = ".md"

# Prompt templates
PROMPTS = {
    "general": "Convert this page to clean Markdown format, preserving all text, tables, and structure. Maintain the original formatting and hierarchy.",
    "table_heavy": "This page contains tables. Convert to Markdown with proper table formatting using | symbols. Preserve all data and structure.",
    "title_page": "Extract the title, author, publication info, and any metadata from this title page in clean Markdown format.",
    "index": "Convert this table of contents or index page to Markdown format with proper heading hierarchy and page references.",
    "diagram": "This page contains diagrams or figures. Describe the visual elements and convert any text to Markdown format."
}

# Processing options
RETRY_FAILED_PAGES = True
MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for accepting output