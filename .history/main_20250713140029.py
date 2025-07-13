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

def extract_keywords(cleaned_words):
    """
    Returns a set of unique keywords from the cleaned job description words.
    """
    return set(cleaned_words)

def match_keywords(job_keywords, resume_words):
    """
    Compares job keywords to resume words.
    Returns two sets: matched keywords and missing keywords.
    """
    resume_words_set = set(resume_words)
    matched = job_keywords & resume_words_set
    missing = job_keywords - resume_words_set
    return matched, missing

def calculate_match_percent(matched, total):
    """
    Returns the match percent as a float (0-100).
    """
    if total == 0:
        return 0.0
    return 100 * len(matched) / total


