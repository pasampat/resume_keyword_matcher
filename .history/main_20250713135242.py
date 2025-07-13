# main.py
import os
import re
import string
import collections
import csv
from PyPDF2 import PdfReader  # Install with: pip install PyPDF2

from stopwords import STOP_WORDS

def read_file(filepath):
    """
    Reads and returns the text from a .txt or .pdf file.
    """
    # Get file extension
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext == '.txt':
        try:
            #if text it will open it
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    elif ext == '.pdf':
        try:
            reader = PdfReader(filepath)
            text = ""
            #extracts for pdf
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return ""
    
    else:
        print("Unsupported file type. Please use a .txt or .pdf file.")
        return ""

def clean_text(raw_text, stop_words):
    """
    Lowercases, removes punctuation, splits, and removes stop words.
    Returns a list of cleaned words.
    """
    # Lowercase all text
    text = raw_text.lower()
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    # Split into words (tokens)
    words = text.split()
    # Remove stop words and non-alpha tokens
    cleaned_words = [word for word in words if word not in stop_words and word.isalpha()]
    return cleaned_words


if __name__ == "__main__":
    