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


if __name__ == "__main__":
    # Test with a TXT file
    txt_path = "test_files/resume1.txt"  # Change to your sample file
    print("----- TXT FILE OUTPUT -----")
    txt_content = read_file(txt_path)
    print(txt_content)

    print("\n\n")

    # Test with a PDF file
    pdf_path = "test_files/resume1.pdf"  # Change to your sample file
    print("----- PDF FILE OUTPUT -----")
    pdf_content = read_file(pdf_path)
    print(pdf_content)