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
    # Test with a TXT file
    txt_path = "test_files/resume1.txt"  # Update if needed
    print("----- TXT FILE OUTPUT (RAW) -----")
    txt_content = read_file(txt_path)
    print(txt_content[:500])  # Print first 500 chars for sanity

    print("\n----- TXT FILE OUTPUT (CLEANED WORDS) -----")
    txt_cleaned = clean_text(txt_content, STOP_WORDS)
    print(txt_cleaned[:50])  # Print first 50 words

    print("\n\n")

    # Test with a PDF file
    pdf_path = "test_files/resume1.pdf"  # Update if needed
    print("----- PDF FILE OUTPUT (RAW) -----")
    pdf_content = read_file(pdf_path)
    print(pdf_content[:500])  # Print first 500 chars for sanity

    print("\n----- PDF FILE OUTPUT (CLEANED WORDS) -----")
    pdf_cleaned = clean_text(pdf_content, STOP_WORDS)
    print(pdf_cleaned[:50])  # Print first 50 words