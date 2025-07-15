# Deep Learning Language Translator

This is an advanced language translation application that uses deep learning models to perform high-quality translations between multiple languages. The application features both text and PDF translation capabilities.

## Features

- Text translation using state-of-the-art neural machine translation models
- PDF document translation with support for multi-page documents
- Modern and responsive UI built with Tkinter
- Support for 20+ languages
- GPU acceleration (when available)
- Export translated PDFs

## Technology Stack

- **Deep Learning**: Hugging Face Transformers, MarianMT models
- **Backend**: Python, PyTorch
- **UI**: Tkinter
- **PDF Processing**: PyMuPDF, FPDF

## How It Works

This application uses the Hugging Face Transformers library with pre-trained MarianMT neural machine translation models. These models implement a sequence-to-sequence transformer architecture that provides high-quality translations.

When a translation is requested:

1. The text is tokenized using a language-specific tokenizer
2. The tokens are passed through the neural network
3. The model generates output tokens in the target language
4. These tokens are decoded back into readable text

Models are automatically downloaded and cached the first time a specific language pair is used.

## Language Support

The application supports translation between numerous languages including:

- English
- French
- German
- Spanish
- Italian
- Portuguese
- Dutch
- Russian
- Chinese
- Arabic
- Hindi
- Japanese
- Korean
- Turkish
- Polish
- Ukrainian
- Vietnamese
- Thai
- Romanian
- Swedish

## Requirements

- Python 3.8+
- PyTorch
- Transformers
- SentencePiece
- PyMuPDF
- FPDF

## Installation

1. Clone this repository
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

## First-time Use

The first time you translate between a specific language pair, the application will download the required model, which may take some time depending on your internet connection. Subsequent translations using the same language pair will be much faster as the model will be loaded from the local cache.

## Hardware Acceleration

This application automatically uses GPU acceleration if available, which significantly improves translation speed. To check if GPU acceleration is being used, look at the status bar at the bottom of the application window.
