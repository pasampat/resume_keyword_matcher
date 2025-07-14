# main.py
import os
import re
import string
import collections
import csv
from PyPDF2 import PdfReader  # Install with: pip install PyPDF2

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

from stopwords import STOP_WORDS

# Ensure output folder exists
if not os.path.exists('output'):
    os.makedirs('output')

def read_file(filepath):
    """
    Reads and returns the text from a .txt or .pdf file.
    Handles errors and unsupported types gracefully.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext == '.txt':
        try:
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

def clean_text(raw_text, stop_words):
    """
    Lowercases, removes punctuation, splits, and removes stop words.
    Returns a list of cleaned words.
    """
    text = raw_text.lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    words = text.split()
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

def save_results_txt(filename, match_percent, matched, missing, job_word_counts):
    """
    Saves results as a human-readable .txt file with frequencies.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Match Percent: {match_percent:.1f}%\n\n")
            f.write(f"Matched Keywords ({len(matched)}):\n")
            f.write(f"{'Keyword':<20} {'Frequency in JD':>16}\n")
            f.write("-" * 36 + "\n")
            for word in matched:
                f.write(f"{word:<20} {job_word_counts[word]:>16}\n")
            f.write("\n")
            f.write(f"Missing Keywords ({len(missing)}):\n")
            f.write(f"{'Keyword':<20} {'Frequency in JD':>16}\n")
            f.write("-" * 36 + "\n")
            for word in missing:
                f.write(f"{word:<20} {job_word_counts[word]:>16}\n")
    except Exception as e:
        print(f"Error saving TXT file: {e}")

def save_results_csv(filename, match_percent, matched, missing, job_word_counts):
    """
    Saves results as a .csv file with frequencies.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Match Percent', f"{match_percent:.1f}%"])
            writer.writerow([])
            writer.writerow(['Matched Keywords', 'Frequency in JD'])
            for word in matched:
                writer.writerow([word, job_word_counts[word]])
            writer.writerow([])
            writer.writerow(['Missing Keywords', 'Frequency in JD'])
            for word in missing:
                writer.writerow([word, job_word_counts[word]])
    except Exception as e:
        print(f"Error saving CSV file: {e}")

def prompt_filepath(prompt_message, default_path=None):
    while True:
        if default_path:
            path = input(f"{prompt_message} [Press Enter to use the sample file: {default_path}]: ").strip()
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

def extract_nouns_verbs(words):
    """
    Uses NLTK POS tagging to return only nouns and verbs from a word list.
    """
    pos_tags = nltk.pos_tag(words)
    allowed = {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    filtered = [word for word, tag in pos_tags if tag in allowed]
    return filtered   

def save_summary_csv(filename, summary_rows):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Resume File', 'Match %', '#Matched', '#Missing'])
            for row in summary_rows:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving summary CSV file: {e}")

