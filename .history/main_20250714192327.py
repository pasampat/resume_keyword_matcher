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

from file_utils import (
    read_file,
    save_results_txt,
    save_results_csv,
    save_summary_csv,
    prompt_filepath,
    prompt_resume_paths,
    prompt_save_format,
)

from text_utils import (
    clean_text,
    extract_keywords,
    match_keywords,
    calculate_match_percent,
    extract_nouns_verbs,
)

from stopwords import STOP_WORDS


from stopwords import STOP_WORDS

# Ensure output folder exists
if not os.path.exists('output'):
    os.makedirs('output')

# ----- At the top of your file, define your default sample resumes -----
DEFAULT_RESUMES = [
    "test_files/resume1.txt",
    "test_files/resume2.txt",
    "test_files/resume3.txt"
]

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



def save_summary_csv(filename, summary_rows):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Resume File', 'Match %', '#Matched', '#Missing'])
            for row in summary_rows:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving summary CSV file: {e}")

def prompt_resume_paths():
    while True:
        resume_input = input(
            "Enter path(s) to 1–3 resume files (.txt or .pdf). Separate by commas\n"
            f"[Press Enter to use the samples: {', '.join(DEFAULT_RESUMES)}]: "
        ).strip()
        if not resume_input:
            resume_paths = DEFAULT_RESUMES
        else:
            # Split, strip whitespace, and filter out empty
            resume_paths = [p.strip() for p in resume_input.split(",") if p.strip()]
        if len(resume_paths) == 0:
            print("Please provide at least one resume file.")
            continue
        if len(resume_paths) > 3:
            print("You entered too many resumes. Please enter up to 3 resumes for comparison.")
            continue
        # Optional: check if files exist here and warn/skip as needed
        return resume_paths

if __name__ == "__main__":
    print("=== Resume Keyword Matcher ===\n")
    print("Compare up to 3 resumes against a job description.")
    print("See which resume covers the most important keywords for the job.\n")
    print("Resumes with more keyword matches may stand out more to employers.\n")

    # Prompt for job description
    job_path = prompt_filepath("Enter path to the job description (.txt or .pdf)",
                              "test_files/job1.txt")

    # Prompt for 1–3 resumes
    resume_paths = prompt_resume_paths()

    # 1. Read and clean job description
    job_text = read_file(job_path)
    if not job_text:
        print("Could not read job description. Exiting.")
        exit()
    job_cleaned = clean_text(job_text, STOP_WORDS)

    # Extraction mode
    print("\nKeyword extraction mode:")
    print("1. All words (default)")
    print("2. Only nouns/verbs (recommended for most jobs)")
    mode = input("Choose 1 or 2 and press Enter: ").strip()
    if mode == "2":
        job_cleaned = extract_nouns_verbs(job_cleaned)
        print("(Extracting only nouns and verbs as keywords.)")
    else:
        print("(Using all cleaned words as keywords.)")
    job_keywords = extract_keywords(job_cleaned)
    job_word_counts = collections.Counter(job_cleaned)

    # 2. Process each resume
    valid_results = []
    for resume_path in resume_paths:
        print(f"\nProcessing: {resume_path}")
        resume_text = read_file(resume_path)
        if not resume_text:
            print(f"Could not read {resume_path}. Skipping.")
            continue
        resume_cleaned = clean_text(resume_text, STOP_WORDS)
        matched, missing = match_keywords(job_keywords, resume_cleaned)
        resume_counts = collections.Counter(resume_cleaned)
        valid_results.append({
            "resume_path": resume_path,
            "resume_counts": resume_counts,
            "match_percent": calculate_match_percent(matched, len(job_keywords)),
            "num_matched": len(matched),
            "num_missing": len(missing),
            "matched": matched,
            "missing": missing
        })

    if not valid_results:
        print("No valid resumes processed. Exiting.")
        exit()

    # 3. Single resume (detailed output, as before)
    if len(valid_results) == 1:
        r = valid_results[0]
        print(f"\n=== RESULTS for {os.path.basename(r['resume_path'])} ===")
        print(f"Match Percent: {r['match_percent']:.1f}%\n")
        print(f"Matched Keywords ({r['num_matched']}):")
        print(f"{'Keyword':<20} {'Frequency in JD':>16}")
        print("-" * 36)
        for word in sorted(r['matched'], key=lambda w: (-job_word_counts[w], w)):
            print(f"{word:<20} {job_word_counts[word]:>16}")
        print(f"\nMissing Keywords ({r['num_missing']}):")
        print(f"{'Keyword':<20} {'Frequency in JD':>16}")
        print("-" * 36)
        for word in sorted(r['missing'], key=lambda w: (-job_word_counts[w], w)):
            print(f"{word:<20} {job_word_counts[word]:>16}")
        # Offer to save as txt/csv
        save_choice = prompt_save_format()
        if save_choice in ("txt", "csv"):
            filename = input(f"Enter filename (e.g., output.{save_choice}): ").strip()
            if not filename.startswith("output/"):
                filename = os.path.join("output", filename)
            if save_choice == "txt":
                save_results_txt(filename, r["match_percent"], r["matched"], r["missing"], job_word_counts)
            else:
                save_results_csv(filename, r["match_percent"], r["matched"], r["missing"], job_word_counts)
            print(f"Results saved to {filename}")
        else:
            print("Results not saved to file.")
        exit()

    # 4. Multi-resume: summary table and side-by-side keyword comparison
    # ----- SUMMARY TABLE -----
    print("\n=== SUMMARY ===")
    print(f"{'Resume File':<28} {'Match %':>8} {'#Matched':>10} {'#Missing':>10}")
    print("-" * 60)
    for r in valid_results:
        print(f"{os.path.basename(r['resume_path']):<28} {r['match_percent']:>8.1f} {r['num_matched']:>10} {r['num_missing']:>10}")

    # ----- KEYWORD MATRIX -----
    # Build set of all job keywords in priority order
    all_keywords = sorted(job_keywords, key=lambda w: (-job_word_counts[w], w))
    print("\n=== KEYWORD COMPARISON ===")
    header = ["Keyword"]
    for r in valid_results:
        header.append(os.path.basename(r['resume_path']))
    print(" | ".join(f"{col:<15}" for col in header))
    print("-" * (18 * len(header)))
    for word in all_keywords:
        row = [f"{word:<15}"]
        for r in valid_results:
            row.append(f"{r['resume_counts'].get(word, 0):<15}")
        print(" | ".join(row))

    # 5. Save all results
    save_choice = input("\nSave all comparison results? (none/txt/csv): ").strip().lower()
    if save_choice == "txt":
        filename = input("Enter filename (e.g., output.txt): ").strip()
        if not filename.startswith("output/"):
            filename = os.path.join("output", filename)
        with open(filename, 'w', encoding='utf-8') as f:
            # Write summary
            f.write("=== SUMMARY ===\n")
            f.write(f"{'Resume File':<28} {'Match %':>8} {'#Matched':>10} {'#Missing':>10}\n")
            f.write("-" * 60 + "\n")
            for r in valid_results:
                f.write(f"{os.path.basename(r['resume_path']):<28} {r['match_percent']:>8.1f} {r['num_matched']:>10} {r['num_missing']:>10}\n")
            f.write("\n=== KEYWORD COMPARISON ===\n")
            f.write(" | ".join(f"{col:<15}" for col in header) + "\n")
            f.write("-" * (18 * len(header)) + "\n")
            for word in all_keywords:
                row = [f"{word:<15}"]
                for r in valid_results:
                    row.append(f"{r['resume_counts'].get(word, 0):<15}")
                f.write(" | ".join(row) + "\n")
        print(f"Results saved to {filename}")
    elif save_choice == "csv":
        filename = input("Enter filename (e.g., output.csv): ").strip()
        if not filename.startswith("output/"):
            filename = os.path.join("output", filename)
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write summary
            writer.writerow(["=== SUMMARY ==="])
            writer.writerow(['Resume File', 'Match %', '#Matched', '#Missing'])
            for r in valid_results:
                writer.writerow([
                    os.path.basename(r["resume_path"]),
                    f"{r['match_percent']:.1f}",
                    r["num_matched"],
                    r["num_missing"]
                ])
            writer.writerow([])
            writer.writerow(["=== KEYWORD COMPARISON ==="])
            row_header = ["Keyword"] + [os.path.basename(r['resume_path']) for r in valid_results]
            writer.writerow(row_header)
            for word in all_keywords:
                row = [word]
                for r in valid_results:
                    row.append(r['resume_counts'].get(word, 0))
                writer.writerow(row)
        print(f"Results saved to {filename}")
    else:
        print("Results not saved to file.")

