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
    Handles errors and unsupported types gracefully.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext == '.txt':
        try:
            # If text, it will open it
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
            # Extracts text for pdf
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
    """
    Saves results as a human-readable .txt file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Match Percent: {match_percent:.1f}%\n\n")
            f.write(f"Matched Keywords ({len(matched)}):\n")
            f.write(", ".join(sorted(list(matched))) + "\n\n")
            f.write(f"Missing Keywords ({len(missing)}):\n")
            f.write(", ".join(sorted(list(missing))) + "\n")
    except Exception as e:
        print(f"Error saving TXT file: {e}")

def save_results_csv(filename, match_percent, matched, missing):
    """
    Saves results as a .csv file.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Match Percent', f"{match_percent:.1f}%"])
            writer.writerow([])
            writer.writerow(['Matched Keywords'] + list(sorted(matched)))
            writer.writerow([])
            writer.writerow(['Missing Keywords'] + list(sorted(missing)))
    except Exception as e:
        print(f"Error saving CSV file: {e}")

def prompt_filepath(prompt_message, default_path=None):
    while True:
        if default_path:
            path = input(f"{prompt_message} [Press Enter for {default_path}]: ").strip()
            if path == "":
                path = default_path
        else:
            path = input(prompt_message).strip()
        if not os.path.isfile(path):
            print("File does not exist. Please try again.")
        elif not path.lower().endswith(('.txt', '.pdf')):
            print("File must be .txt or .pdf. Please try again.")
        else:
            return path

def prompt_save_format():
    """
    Prompt user for save format, accept only valid choices.
    """
    valid_choices = {"none", "txt", "csv"}
    while True:
        choice = input("\nSave results? (none/txt/csv): ").strip().lower()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please enter 'none', 'txt', or 'csv'.")

if __name__ == "__main__":
    print("=== Resume Keyword Matcher ===\n")

    # Prompt for job description and resume file paths
    job_path = prompt_filepath("Enter path to job description (.txt or .pdf)", "test_files/resume1.txt")
    resume_path = prompt_filepath("Enter path to resume (.txt or .pdf)", "test_files/sample_resume.txt")

    # 1. Read and clean job description
    job_text = read_file(job_path)
    if not job_text:
        print("Could not read job description. Exiting.")
        exit()
    job_cleaned = clean_text(job_text, STOP_WORDS)
    job_keywords = extract_keywords(job_cleaned)

    # 2. Read and clean resume
    resume_text = read_file(resume_path)
    if not resume_text:
        print("Could not read resume. Exiting.")
        exit()
    resume_cleaned = clean_text(resume_text, STOP_WORDS)

    # 3. Match
    matched, missing = match_keywords(job_keywords, resume_cleaned)
    match_percent = calculate_match_percent(matched, len(job_keywords))

    # 4. Print Results
    print(f"\n=== RESULTS ===")
    print(f"Match Percent: {match_percent:.1f}%")
    print(f"\nMatched keywords ({len(matched)}):\n{sorted(list(matched))}")
    print(f"\nMissing keywords ({len(missing)}):\n{sorted(list(missing))}")

    # 5. Offer to save results in txt/csv
    save_choice = prompt_save_format()
    if save_choice == "txt":
        filename = input("Enter filename (e.g., output.txt): ").strip()
        save_results_txt(filename, match_percent, matched, missing)
        print(f"Results saved to {filename}")
    elif save_choice == "csv":
        filename = input("Enter filename (e.g., output.csv): ").strip()
        save_results_csv(filename, match_percent, matched, missing)
        print(f"Results saved to {filename}")
    else:
        print("Results not saved to file.")

