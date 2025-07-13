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


def save_results_txt(filename, match_percent, matched, missing):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Match Percent: {match_percent:.1f}%\n\n")
        f.write(f"Matched Keywords ({len(matched)}):\n")
        f.write(", ".join(sorted(list(matched))) + "\n\n")
        f.write(f"Missing Keywords ({len(missing)}):\n")
        f.write(", ".join(sorted(list(missing))) + "\n")

def save_results_csv(filename, match_percent, matched, missing):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Match Percent', f"{match_percent:.1f}%"])
        writer.writerow([])
        writer.writerow(['Matched Keywords'] + list(sorted(matched)))
        writer.writerow([])
        writer.writerow(['Missing Keywords'] + list(sorted(missing)))



if __name__ == "__main__":
    # 1. Read and clean job description
    job_path = "test_files/job1.txt"  # or job1.pdf
    job_text = read_file(job_path)
    job_cleaned = clean_text(job_text, STOP_WORDS)
    job_keywords = extract_keywords(job_cleaned)

    # 2. Read and clean resume
    resume_path = "test_files/resume1.txt"  # or resume1.pdf
    resume_text = read_file(resume_path)
    resume_cleaned = clean_text(resume_text, STOP_WORDS)

    # 3. Match
    matched, missing = match_keywords(job_keywords, resume_cleaned)
    match_percent = calculate_match_percent(matched, len(job_keywords))

    # 4. Print Results
    print(f"\nMATCH PERCENT: {match_percent:.1f}%")
    print(f"\nMatched keywords ({len(matched)}): {sorted(list(matched))}")
    print(f"\nMissing keywords ({len(missing)}): {sorted(list(missing))}")
