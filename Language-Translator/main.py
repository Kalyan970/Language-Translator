from tkinter import *
from tkinter import filedialog, messagebox, ttk
import os
import sys

# Add error handling for imports
try:
    import torch
    print("PyTorch successfully imported, version:", torch.__version__)
except ImportError as e:
    print(f"Error importing torch: {e}")
    messagebox.showerror("Import Error", f"Failed to import torch: {e}\nPlease install it using: pip install torch")
    sys.exit(1)

try:
    import fitz  # PyMuPDF
    print("PyMuPDF successfully imported")
except ImportError as e:
    print(f"Error importing fitz (PyMuPDF): {e}")
    messagebox.showerror("Import Error", f"Failed to import PyMuPDF: {e}\nPlease install it using: pip install PyMuPDF")
    sys.exit(1)

try:
    from fpdf import FPDF
    print("FPDF successfully imported")
except ImportError as e:
    print(f"Error importing FPDF: {e}")
    messagebox.showerror("Import Error", f"Failed to import FPDF: {e}\nPlease install it using: pip install fpdf")
    sys.exit(1)

try:
    from translator import TextTranslator
    print("TextTranslator successfully imported")
except ImportError as e:
    print(f"Error importing TextTranslator: {e}")
    messagebox.showerror("Import Error", f"Failed to import the translator module: {e}\nCheck if translator.py exists and all its dependencies are installed.")
    sys.exit(1)

from threading import Thread

# Language list for the dropdown menu
LANGUAGES = {
    'en': 'english', 'fr': 'french', 'de': 'german', 'es': 'spanish',
    'it': 'italian', 'pt': 'portuguese', 'nl': 'dutch', 'ru': 'russian',
    'zh': 'chinese', 'ar': 'arabic', 'hi': 'hindi', 'ja': 'japanese',
    'ko': 'korean', 'tr': 'turkish', 'pl': 'polish', 'uk': 'ukrainian',
    'vi': 'vietnamese', 'th': 'thai', 'ro': 'romanian', 'sv': 'swedish'
}

root = Tk()
root.title("DEEP LEARNING LANGUAGE TRANSLATOR")
root.geometry("1000x650")
root.configure(bg="#f2f2f2")

# Initialize our deep learning translator
print("Initializing translator...")
translator = TextTranslator()
language_list = list(LANGUAGES.values())

# Add a check button to verify transformers installation
def check_transformers_installation():
    try:
        import transformers
        messagebox.showinfo("Transformers Status", f"Transformers is installed. Version: {transformers.__version__}")
    except ImportError:
        messagebox.showerror("Transformers Status", "Transformers is NOT installed. Translation will run in fallback mode.")
        
# Add a test translation function for debugging
def test_translation():
    test_text = "Hello, this is a test."
    try:
        status_var.set("Running test translation...")
        root.update()
        
        result = translator.translate_text(test_text, 'english', 'french')
        
        messagebox.showinfo("Test Translation", 
                           f"Test translation result:\n\nEnglish: {test_text}\n\nFrench: {result}")
        
        if torch.cuda.is_available():
            status_var.set("Ready - Deep Learning Models using GPU: " + torch.cuda.get_device_name(0))
        else:
            status_var.set("Ready - Deep Learning Models using CPU")
    except Exception as e:
        messagebox.showerror("Test Translation Failed", f"Error: {str(e)}")
        status_var.set("Test translation failed - check console")

def get_lang_code(lang_name):
    for code, name in LANGUAGES.items():
        if name.lower() == lang_name.lower():
            return code
    return "en"

def translate_text():
    input_text = input_box.get("1.0", END).strip()
    src_lang = 'english'  # Fixed input language
    dest_lang = output_lang_var.get()
    
    if input_text:
        # Show loading indicator
        output_box.delete("1.0", END)
        output_box.insert(END, "Translating... Please wait.")
        root.update()
        
        def perform_translation():
            try:
                print(f"Starting translation from {src_lang} to {dest_lang}")
                status_var.set(f"Translating from {src_lang} to {dest_lang}...")
                root.update()
                
                translated = translator.translate_text(input_text, src_lang, dest_lang)
                
                output_box.delete("1.0", END)
                output_box.insert(END, translated)
                
                # Reset status
                if torch.cuda.is_available():
                    status_var.set("Ready - Deep Learning Models using GPU: " + torch.cuda.get_device_name(0))
                else:
                    status_var.set("Ready - Deep Learning Models using CPU")
                    
            except Exception as e:
                error_message = str(e)
                print(f"Translation error: {error_message}")
                output_box.delete("1.0", END)
                output_box.insert(END, f"Translation failed: {error_message}\nCheck your input or internet connection.")
                
                # Reset status
                status_var.set("Error occurred - Check console for details")
        
        # Run translation in a separate thread to keep UI responsive
        Thread(target=perform_translation).start()

def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        pdf_path_var.set(file_path)

def translate_pdf():
    file_path = pdf_path_var.get()
    dest_lang = pdf_lang_var.get()
    if not file_path or not dest_lang:
        messagebox.showerror("Error", "Please select PDF and output language.")
        return
    
    # Show loading indicator
    pdf_output_box.delete("1.0", END)
    pdf_output_box.insert(END, "Translating PDF... This may take a while for large documents.")
    root.update()
    
    def perform_pdf_translation():
        try:
            print(f"Opening PDF file: {file_path}")
            status_var.set("Reading PDF...")
            root.update()
            
            doc = fitz.open(file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            print(f"PDF extracted, text length: {len(full_text)}")
            
            # Translate in chunks to avoid exceeding model capacity
            max_chunk_size = 500  # Characters
            chunks = [full_text[i:i+max_chunk_size] for i in range(0, len(full_text), max_chunk_size)]
            
            print(f"Split into {len(chunks)} chunks for translation")
            
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                # Update progress
                status_message = f"Translating chunk {i+1}/{len(chunks)}..."
                pdf_output_box.delete("1.0", END)
                pdf_output_box.insert(END, f"Translating chunk {i+1}/{len(chunks)}... Please wait.")
                status_var.set(status_message)
                root.update()
                
                print(f"Translating chunk {i+1}/{len(chunks)}")
                translated = translator.translate_text(chunk, 'english', dest_lang)
                translated_chunks.append(translated)
            
            complete_translation = ' '.join(translated_chunks)
            pdf_output_box.delete("1.0", END)
            pdf_output_box.insert(END, complete_translation)
            
            # Reset status
            if torch.cuda.is_available():
                status_var.set("Ready - Deep Learning Models using GPU: " + torch.cuda.get_device_name(0))
            else:
                status_var.set("Ready - Deep Learning Models using CPU")
                
        except Exception as e:
            error_message = str(e)
            print(f"PDF Translation error: {error_message}")
            pdf_output_box.delete("1.0", END)
            pdf_output_box.insert(END, f"PDF Translation failed: {error_message}")
            
            # Reset status
            status_var.set("Error occurred - Check console for details")
    
    # Run PDF translation in a separate thread to keep UI responsive
    Thread(target=perform_pdf_translation).start()

def download_translated_pdf():
    translated_text = pdf_output_box.get("1.0", END).strip()
    if not translated_text:
        messagebox.showerror("Error", "No translated text to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            
            # Split text into manageable chunks to avoid FPDF line length limits
            lines = []
            for paragraph in translated_text.split('\n'):
                # Split long paragraphs
                if len(paragraph) > 80:
                    words = paragraph.split()
                    line = ""
                    for word in words:
                        if len(line + " " + word) <= 80:
                            line += " " + word if line else word
                        else:
                            lines.append(line)
                            line = word
                    if line:
                        lines.append(line)
                else:
                    lines.append(paragraph)
            
            for line in lines:
                pdf.multi_cell(0, 10, line)
            
            pdf.output(file_path)
            messagebox.showinfo("Success", "PDF saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

def show_model_info():
    # Create a popup window to display model information
    info_window = Toplevel(root)
    info_window.title("Deep Learning Model Information")
    info_window.geometry("600x400")
    info_window.configure(bg="#f2f2f2")
    
    # Device info
    device_info = "Using GPU" if torch.cuda.is_available() else "Using CPU (GPU not available)"
    
    # Model info text
    info_text = f"""
    Deep Learning Translation Models Information:
    
    This application uses state-of-the-art neural machine translation models
    from the Hugging Face Transformers library.
    
    Model Type: MarianMT (Marian Neural Machine Translation)
    
    Features:
    - Models are downloaded and cached on first use for each language pair
    - Supports translation between multiple languages
    - Uses sequence-to-sequence transformer architecture
    - High-quality translations powered by deep learning
    
    Hardware Acceleration: {device_info}
    
    Note: The first translation for each language pair might take 
    longer as the model is downloaded and loaded.
    """
    
    info_label = Label(info_window, text=info_text, justify=LEFT, bg="#f2f2f2", font=("Arial", 11))
    info_label.pack(padx=20, pady=20)
    
    Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)

# Variables
output_lang_var = StringVar(value='hindi')
pdf_path_var = StringVar()
pdf_lang_var = StringVar(value='hindi')

# Title
title_frame = Frame(root, bg="#4a6fa5", padx=10, pady=10)
title_frame.pack(fill=X)
Label(title_frame, text="DEEP LEARNING LANGUAGE TRANSLATOR", font=("Helvetica", 18, "bold"), 
      bg="#4a6fa5", fg="white").pack(side=LEFT, padx=10)

# Add buttons for debugging
debug_frame = Frame(title_frame, bg="#4a6fa5")
debug_frame.pack(side=RIGHT)
Button(debug_frame, text="Check Deps", command=check_transformers_installation, 
       bg="#2c3e50", fg="white", font=("Arial", 9)).pack(side=LEFT, padx=5)
Button(debug_frame, text="Test Trans", command=test_translation, 
       bg="#2c3e50", fg="white", font=("Arial", 9)).pack(side=LEFT, padx=5)
Button(debug_frame, text="Model Info", command=show_model_info, 
       bg="#2c3e50", fg="white", font=("Arial", 9)).pack(side=LEFT, padx=5)

# Frame for Text Translation
main_frame = Frame(root, bg="#f2f2f2", padx=20, pady=10)
main_frame.pack(fill=BOTH, expand=True)

# Create a nice header for the text translation section
text_header = Frame(main_frame, bg="#e1e5eb", padx=10, pady=5)
text_header.pack(fill=X, pady=(10, 0))
Label(text_header, text="Text Translation", font=("Arial", 12, "bold"), bg="#e1e5eb").pack(anchor=W)

# Input and Output in a frame
io_frame = Frame(main_frame, bg="#f2f2f2")
io_frame.pack(fill=X, pady=10)

# Input
input_frame = Frame(io_frame, bg="#f2f2f2")
input_frame.grid(row=0, column=0, padx=20)
Label(input_frame, text="Input Language: English", font=("Arial", 10, "bold"), bg="#f2f2f2").grid(row=0, column=0, sticky=W)
Label(input_frame, text="Enter Text", font=("Arial", 10), bg="#f2f2f2").grid(row=1, column=0, sticky=W, pady=5)
input_box = Text(input_frame, height=10, width=40, font=("Arial", 12), bd=2, relief=GROOVE)
input_box.grid(row=2, column=0)

# Output
output_frame = Frame(io_frame, bg="#f2f2f2")
output_frame.grid(row=0, column=1, padx=20)
Label(output_frame, text="Output Language", font=("Arial", 10, "bold"), bg="#f2f2f2").grid(row=0, column=0, sticky=W)
output_lang_combo = ttk.Combobox(output_frame, textvariable=output_lang_var, values=language_list, width=20, state='readonly')
output_lang_combo.grid(row=1, column=0, sticky=W, pady=5)
output_box = Text(output_frame, height=10, width=40, font=("Arial", 12), bd=2, relief=GROOVE)
output_box.grid(row=2, column=0)

# Translate Button with better styling
translate_btn_frame = Frame(main_frame, bg="#f2f2f2")
translate_btn_frame.pack(pady=10)
translate_btn = Button(translate_btn_frame, text="Translate Text", font=("Arial", 11, "bold"), 
                       bg="#3498db", fg="white", padx=15, pady=5, command=translate_text)
translate_btn.pack()

# Create a separator
separator = Frame(root, height=2, bg="#cccccc")
separator.pack(fill=X, padx=20, pady=5)

# Frame for PDF translation with better styling
pdf_header = Frame(root, bg="#e1e5eb", padx=10, pady=5)
pdf_header.pack(fill=X, pady=(10, 0), padx=20)
Label(pdf_header, text="PDF Translator", font=("Arial", 12, "bold"), bg="#e1e5eb").pack(anchor=W)

pdf_frame = Frame(root, bg="#f2f2f2", bd=2, relief=GROOVE, padx=10, pady=10)
pdf_frame.pack(pady=10, fill=X, padx=20)

pdf_file_frame = Frame(pdf_frame, bg="#f2f2f2")
pdf_file_frame.pack(fill=X, pady=5)
Label(pdf_file_frame, text="PDF File:", bg="#f2f2f2", font=("Arial", 10)).pack(side=LEFT, padx=5)
Entry(pdf_file_frame, textvariable=pdf_path_var, width=50, bd=2).pack(side=LEFT, padx=5)
Button(pdf_file_frame, text="Browse", command=select_pdf, bg="#7f8c8d", fg="white").pack(side=LEFT, padx=5)

pdf_lang_frame = Frame(pdf_frame, bg="#f2f2f2")
pdf_lang_frame.pack(fill=X, pady=5)
Label(pdf_lang_frame, text="Output Language:", bg="#f2f2f2", font=("Arial", 10)).pack(side=LEFT, padx=5)
ttk.Combobox(pdf_lang_frame, textvariable=pdf_lang_var, values=language_list, width=20, state='readonly').pack(side=LEFT, padx=5)
Button(pdf_lang_frame, text="Translate PDF", command=translate_pdf, bg="#3498db", fg="white").pack(side=LEFT, padx=10)

pdf_output_frame = Frame(pdf_frame, bg="#f2f2f2")
pdf_output_frame.pack(fill=X, pady=5)
Label(pdf_output_frame, text="Translation Result:", bg="#f2f2f2", font=("Arial", 10, "bold")).pack(anchor=W, padx=5, pady=5)
pdf_output_box = Text(pdf_output_frame, height=10, width=100, font=("Arial", 11), bd=2, relief=GROOVE)
pdf_output_box.pack(padx=5, pady=5, fill=X)

pdf_download_frame = Frame(pdf_frame, bg="#f2f2f2")
pdf_download_frame.pack(fill=X, pady=10)
Button(pdf_download_frame, text="Download Translated PDF", command=download_translated_pdf, 
       bg="#2ecc71", fg="white", font=("Arial", 10, "bold")).pack()

# Status bar at the bottom
status_frame = Frame(root, bg="#2c3e50", height=25)
status_frame.pack(side=BOTTOM, fill=X)
status_var = StringVar(value="Ready - Deep Learning Models")
status_label = Label(status_frame, textvariable=status_var, bg="#2c3e50", fg="white", font=("Arial", 9))
status_label.pack(side=LEFT, padx=10, pady=2)

# Check if GPU is available and update status
try:
    if torch.cuda.is_available():
        status_var.set("Ready - Deep Learning Models using GPU: " + torch.cuda.get_device_name(0))
    else:
        status_var.set("Ready - Deep Learning Models using CPU")
except:
    status_var.set("FALLBACK MODE - Deep Learning Models not loaded")
    
# Show a popup about the fallback mode
if hasattr(translator, 'fallback_mode') and translator.fallback_mode:
    messagebox.showinfo("Fallback Mode", 
                       "The application is running in fallback mode because some dependencies are missing.\n\n"
                       "For full functionality, please install all required packages:\n\n"
                       "pip install torch transformers sentencepiece PyMuPDF fpdf tqdm sacremoses protobuf datasets")

root.mainloop()
