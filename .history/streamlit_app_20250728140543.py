import os
import re
import string
import collections
import csv
from PyPDF2 import PdfReader  # Install with: pip install PyPDF2
import nltk

# ========================
# Default sample resume paths (used if user presses Enter)
# ========================
DEFAULT_RESUMES = [
    "test_files/resume1.txt",
    "test_files/resume2.txt",
    "test_files/resume3.txt"
]

# ========================
# File Reading
# ========================

def read_file(filepath):
    """
    Reads and returns the text from a .txt or .pdf file.
    Handles errors and unsupported types gracefully.
    Returns empty string if file cannot be read.
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

# ========================
# Save Results to TXT
# ========================

def save_results_txt(filename, match_percent, matched, missing, job_word_counts):
    """
    Saves results as a human-readable .txt file with frequencies.
    Includes match percent, matched/missing keywords, and their JD frequencies.
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

# ========================
# Save Results to CSV
# ========================

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

# ========================
# Filepath Prompt for CLI
# ========================

def prompt_filepath(prompt_message, default_path=None):
    """
    Prompts user for a file path, checks for existence and correct file type.
    Returns path when valid; otherwise, prompts again.
    """
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

# ========================
# Prompt User for Save Format
# ========================

def prompt_save_format():
    """
    Prompt user for save format: 'none', 'txt', or 'csv'.
    Loops until a valid choice is made.
    """
    valid_choices = {"none", "txt", "csv"}
    while True:
        choice = input("\nSave results? (none/txt/csv): ").strip().lower()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please enter 'none', 'txt', or 'csv'.")

# ========================
# Save Summary Table as CSV
# ========================

def save_summary_csv(filename, summary_rows):
    """
    Saves the summary comparison table (multi-resume) as a CSV.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Resume File', 'Match %', '#Matched', '#Missing'])
            for row in summary_rows:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving summary CSV file: {e}")

# ========================
# Prompt for Resume Paths (CLI)
# ========================

def prompt_resume_paths():
    """
    Prompts user for 1-3 resume file paths (comma-separated).
    Returns a list of valid paths (or sample files if Enter is pressed).
    """
    while True:
        resume_input = input(
            "Enter path(s) to 1–3 resume files (.txt or .pdf). Separate by commas\n"
            f"[Press Enter to use the samples: {', '.join(DEFAULT_RESUMES)}]: "
        ).strip()
        if not resume_input:
            resume_paths = DEFAULT_RESUMES
        else:
            # Split input by comma, strip whitespace, ignore empty values
            resume_paths = [p.strip() for p in resume_input.split(",") if p.strip()]
        if len(resume_paths) == 0:
            print("Please provide at least one resume file.")
            continue
        if len(resume_paths) > 3:
            print("You entered too many resumes. Please enter up to 3 resumes for comparison.")
            continue
        # Optional: check if files exist here and warn/skip as needed
        return resume_paths
