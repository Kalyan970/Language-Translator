try:
    import fitz  # PyMuPDF
    print("PyMuPDF successfully imported in pdf_utils")
    FITZ_AVAILABLE = True
except ImportError:
    print("Error importing fitz (PyMuPDF) in pdf_utils")
    FITZ_AVAILABLE = False

from translator import TextTranslator
import torch

# Initialize the translator with deep learning models
translator = TextTranslator()

def extract_pdf_text(path):
    if not FITZ_AVAILABLE:
        return "PDF extraction not available - PyMuPDF not installed"
    
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def translate_pdf_text(text, src, dest):
    # Break the text into chunks to avoid exceeding model capacity
    max_chunk_size = 500  # Characters
    chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    translated_chunks = []
    for chunk in chunks:
        translated = translator.translate_text(chunk, src, dest)
        translated_chunks.append(translated)
    
    return ' '.join(translated_chunks)

def write_pdf(output_text, output_path):
    if not FITZ_AVAILABLE:
        return False
    
    try:
        doc = fitz.open()
        
        # Split the text into pages (roughly 3000 characters per page)
        text_length = len(output_text)
        chars_per_page = 3000
        num_pages = max(1, text_length // chars_per_page + (1 if text_length % chars_per_page > 0 else 0))
        
        for i in range(num_pages):
            page = doc.new_page()
            start_idx = i * chars_per_page
            end_idx = min((i + 1) * chars_per_page, text_length)
            page_text = output_text[start_idx:end_idx]
            
            # Insert text
            page.insert_text((72, 72), page_text, fontsize=12)
        
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Error writing PDF: {str(e)}")
        return False
