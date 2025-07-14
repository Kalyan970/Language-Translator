from transformers import MarianMTModel, MarianTokenizer
import torch
import os
from pathlib import Path

class TextTranslator:
    def __init__(self):
        try:
            # Try to import required deep learning modules
            import transformers
            self.fallback_mode = False
            print("Deep learning mode activated. Using Hugging Face Transformers", transformers.__version__)
        except ImportError:
            self.fallback_mode = True
            print("TextTranslator initialized in fallback mode - transformers not available")
            return

        self.models = {}
        self.tokenizers = {}
        self.model_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "language_translator_models")
        Path(self.model_cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Language code mappings (ISO language code to language name)
        self.language_code_map = {
            'en': 'english', 'fr': 'french', 'de': 'german', 'es': 'spanish',
            'it': 'italian', 'pt': 'portuguese', 'nl': 'dutch', 'ru': 'russian',
            'zh': 'chinese', 'ar': 'arabic', 'hi': 'hindi', 'ja': 'japanese',
            'ko': 'korean', 'tr': 'turkish', 'pl': 'polish', 'uk': 'ukrainian',
            'vi': 'vietnamese', 'th': 'thai', 'ro': 'romanian', 'sv': 'swedish'
        }
        self.reverse_language_code_map = {v: k for k, v in self.language_code_map.items()}
        
        # Device configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
    
    def get_model_name(self, src_lang, dest_lang):
        # Get the ISO language codes
        src_code = self.reverse_language_code_map.get(src_lang.lower(), src_lang.lower())
        dest_code = self.reverse_language_code_map.get(dest_lang.lower(), dest_lang.lower())
        
        # Special case for English to other languages and other languages to English
        if src_code == 'en':
            return f'Helsinki-NLP/opus-mt-en-{dest_code}'
        elif dest_code == 'en':
            return f'Helsinki-NLP/opus-mt-{src_code}-en'
        else:
            # For non-English language pairs, we use a multi-language model or go through English
            return f'Helsinki-NLP/opus-mt-{src_code}-{dest_code}'
    
    def load_model(self, src_lang, dest_lang):
        if self.fallback_mode:
            print("Cannot load models in fallback mode")
            return None, None
            
        model_key = f"{src_lang}_{dest_lang}"
        
        # If model is already loaded, return it
        if model_key in self.models and model_key in self.tokenizers:
            print(f"Using cached model for {src_lang} to {dest_lang}")
            return self.models[model_key], self.tokenizers[model_key]
        
        try:
            # Try to get a direct translation model
            model_name = self.get_model_name(src_lang, dest_lang)
            print(f"Loading model: {model_name}")
            
            # Try to find a pre-downloaded model to handle offline scenarios
            try:
                # First attempt to load from cache
                tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=self.model_cache_dir, local_files_only=True)
                model = MarianMTModel.from_pretrained(model_name, cache_dir=self.model_cache_dir, local_files_only=True)
                print(f"Loaded model from local cache: {model_name}")
            except Exception as cache_error:
                print(f"Model not found in cache, downloading: {model_name}")
                # If not in cache, download from Hugging Face
                tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=self.model_cache_dir)
                model = MarianMTModel.from_pretrained(model_name, cache_dir=self.model_cache_dir)
                print(f"Downloaded model: {model_name}")
            
            # Move model to the appropriate device (GPU if available)
            model.to(self.device)
            print(f"Model loaded and moved to {self.device}")
            
            # Cache the model and tokenizer
            self.models[model_key] = model
            self.tokenizers[model_key] = tokenizer
            
            return model, tokenizer
        except Exception as e:
            print(f"Error loading direct translation model: {e}")
            
            # Fallback to English as intermediate language if direct translation not available
            if src_lang.lower() != 'english' and dest_lang.lower() != 'english':
                print(f"Will try translating through English instead")
                return None, None
            else:
                raise ValueError(f"Could not load translation model for {src_lang} to {dest_lang}: {str(e)}")

    def translate_text(self, text, src_lang, dest_lang):
        # Fallback mode translation
        if self.fallback_mode:
            print(f"Using fallback translation mode for {src_lang} to {dest_lang}")
            return f"[FALLBACK MODE] Translation from {src_lang} to {dest_lang} would go here.\n\nOriginal text:\n{text}\n\nPlease install all required dependencies to enable actual translation."
            
        # If text is empty, return empty string
        if not text.strip():
            return ""
            
        print(f"Starting translation from {src_lang} to {dest_lang}")
        
        try:
            # Try to load a direct translation model
            print(f"Attempting to load model for {src_lang} to {dest_lang}")
            model, tokenizer = self.load_model(src_lang, dest_lang)
            
            # If direct translation is not available, try translation through English
            if model is None and tokenizer is None:
                print(f"No direct model available for {src_lang} to {dest_lang}")
                if src_lang.lower() != 'english' and dest_lang.lower() != 'english':
                    # First translate from source to English
                    print(f"No direct model for {src_lang} to {dest_lang}, translating via English")
                    english_text = self.translate_text(text, src_lang, 'english')
                    # Then translate from English to destination
                    return self.translate_text(english_text, 'english', dest_lang)
                else:
                    return "Translation not available for this language pair."
            
            # Perform translation
            try:
                print(f"Tokenizing text for translation")
                # Tokenize the text
                batch = tokenizer([text], return_tensors="pt", padding=True, truncation=True, max_length=512)
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                print(f"Generating translation")
                # Generate translation
                with torch.no_grad():
                    generated_ids = model.generate(**batch)
                
                print(f"Decoding translation")
                # Decode the generated tokens
                translated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                print(f"Translation complete")
                return translated_text
            except Exception as e:
                print(f"Translation error during processing: {e}")
                return f"Translation error: {str(e)}"
        except Exception as e:
            print(f"Translation error during model loading: {e}")
            return f"Translation error: {str(e)}"
