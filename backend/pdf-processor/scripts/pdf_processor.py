#!/usr/bin/env python3
"""
PDF to Markdown converter using Qwen2.5-VL vision-language model.
"""

import os
import sys
import argparse
import logging
import io
from pathlib import Path
from typing import Optional, List, Tuple
import gc

import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm

from config import (
    MODEL_NAME, TORCH_DTYPE, DEVICE_MAP, DPI, MAX_BATCH_SIZE,
    SAVE_TEMP_IMAGES, OUTPUT_FORMAT, FILE_PREFIX, MARKDOWN_EXTENSION,
    PROMPTS, RETRY_FAILED_PAGES, MAX_RETRIES
)


class PDFProcessor:
    """Main class for processing PDF documents with Qwen2.5-VL."""
    
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize the PDF processor with the vision-language model."""
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def load_model(self) -> None:
        """Load the Qwen2.5-VL model and processor."""
        self.logger.info(f"Loading model: {self.model_name}")
        
        try:
            # Configure torch dtype
            dtype_map = {
                "float16": torch.float16,
                "float32": torch.float32,
                "bfloat16": torch.bfloat16
            }
            torch_dtype = dtype_map.get(TORCH_DTYPE, torch.float16)
            
            # Load model with optimizations
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                device_map=DEVICE_MAP,
                trust_remote_code=True
            )
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def convert_page_to_image(self, page: fitz.Page) -> Image.Image:
        """Convert a PDF page to PIL Image."""
        # Get page as pixmap with specified DPI
        mat = fitz.Matrix(DPI/72, DPI/72)  # Scale factor for DPI
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        return img
    
    def classify_page_type(self, image: Image.Image) -> str:
        """Classify the page type to select appropriate prompt."""
        # Simple heuristic - could be enhanced with actual classification
        # For now, return "general" for all pages
        return "general"
    
    def generate_markdown(self, image: Image.Image, prompt_type: str = "general") -> str:
        """Generate markdown content from image using Qwen2.5-VL."""
        if not self.model or not self.processor:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Get prompt
        prompt = PROMPTS.get(prompt_type, PROMPTS["general"])
        
        # Prepare messages for the model
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }]
        
        # Apply chat template
        text = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Prepare inputs
        image_inputs, video_inputs = self.processor.process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = inputs.to(self.model.device)
        
        # Generate response
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=False,
                temperature=0.1
            )
        
        # Decode response
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        return output_text.strip()
    
    def save_output(self, content: str, page_num: int, output_dir: Path) -> Path:
        """Save markdown content to file."""
        filename = f"{FILE_PREFIX}{page_num:03d}{MARKDOWN_EXTENSION}"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def process_pdf(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """Process entire PDF document."""
        if not self.model or not self.processor:
            self.load_model()
        
        # Open PDF
        pdf_doc = fitz.open(str(pdf_path))
        total_pages = pdf_doc.page_count
        
        self.logger.info(f"Processing PDF: {pdf_path}")
        self.logger.info(f"Total pages: {total_pages}")
        
        output_files = []
        failed_pages = []
        
        # Process each page
        for page_num in tqdm(range(total_pages), desc="Processing pages"):
            try:
                # Get page
                page = pdf_doc[page_num]
                
                # Convert to image
                image = self.convert_page_to_image(page)
                
                # Save temp image if configured
                if SAVE_TEMP_IMAGES:
                    temp_path = output_dir.parent / "temp" / f"page_{page_num:03d}.png"
                    image.save(temp_path)
                
                # Classify page type
                page_type = self.classify_page_type(image)
                
                # Generate markdown
                markdown_content = self.generate_markdown(image, page_type)
                
                # Save output
                output_path = self.save_output(markdown_content, page_num + 1, output_dir)
                output_files.append(output_path)
                
                self.logger.info(f"Processed page {page_num + 1}/{total_pages}")
                
                # Clean up memory
                del image
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
                gc.collect()
                
            except Exception as e:
                self.logger.error(f"Failed to process page {page_num + 1}: {e}")
                failed_pages.append(page_num + 1)
        
        # Close PDF
        pdf_doc.close()
        
        # Report results
        self.logger.info(f"Successfully processed {len(output_files)} pages")
        if failed_pages:
            self.logger.warning(f"Failed pages: {failed_pages}")
        
        return output_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using Qwen2.5-VL")
    parser.add_argument("pdf_path", type=str, help="Path to input PDF file")
    parser.add_argument("-o", "--output", type=str, help="Output directory", default="output")
    parser.add_argument("-m", "--model", type=str, help="Model name", default=MODEL_NAME)
    
    args = parser.parse_args()
    
    # Validate input
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process PDF
    processor = PDFProcessor(args.model)
    try:
        output_files = processor.process_pdf(pdf_path, output_dir)
        print(f"\nProcessing complete! Generated {len(output_files)} markdown files in {output_dir}")
    except Exception as e:
        print(f"Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()