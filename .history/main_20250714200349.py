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

from display_utils import (
    print_intro,
    print_single_resume_results,
    print_summary_table,
    print_keyword_matrix,
)

# Ensure output folder exists
if not os.path.exists('output'):
    os.makedirs('output')

# ----- At the top of your file, define your default sample resumes -----
DEFAULT_RESUMES = [
    "test_files/resume1.txt",
    "test_files/resume2.txt",
    "test_files/resume3.txt"
]


def process_job_description(job_path):
    job_text = read_file(job_path)
    if not job_text:
        print("Could not read job description. Exiting.")
        exit()
    job_cleaned = clean_text(job_text, STOP_WORDS)

    while True:
        print("\nKeyword extraction mode:")
        print("1. All words (default)")
        print("2. Only nouns/verbs (recommended for most jobs)")
        mode = input("Choose 1 or 2 and press Enter: ").strip()
        if mode in ("1", "2"):
            break
        print("Invalid input. Please enter 1 or 2.")

        if mode == "2":
            job_cleaned = extract_nouns_verbs(job_cleaned)
            print("(Extracting only nouns and verbs as keywords.)")
        else:
            print("(Using all cleaned words as keywords.)")

    job_keywords = extract_keywords(job_cleaned)
    job_word_counts = collections.Counter(job_cleaned)
    return job_keywords, job_word_counts

def process_resumes(resume_paths, job_keywords, job_word_counts):
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
    return valid_results

def save_single_result(result, job_word_counts):
    save_choice = prompt_save_format()
    if save_choice in ("txt", "csv"):
        filename = input(f"Enter filename (e.g., output.{save_choice}): ").strip()
        if not filename.startswith("output/"):
            filename = os.path.join("output", filename)
        if save_choice == "txt":
            save_results_txt(filename, result["match_percent"], result["matched"], result["missing"], job_word_counts)
        else:
            save_results_csv(filename, result["match_percent"], result["matched"], result["missing"], job_word_counts)
        print(f"Results saved to {filename}")
    else:
        print("Results not saved to file.")

def save_all_results(valid_results, all_keywords, job_word_counts, header):
    save_choice = prompt_save_format()  # <<== USE PROMPT HERE
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


def main():
    print_intro()
    job_path = prompt_filepath("Enter path to the job description (.txt or .pdf)", "test_files/job1.txt")
    resume_paths = prompt_resume_paths()
    job_keywords, job_word_counts = process_job_description(job_path)
    valid_results = process_resumes(resume_paths, job_keywords, job_word_counts)

    if not valid_results:
        print("No valid resumes processed. Exiting.")
        return

    if len(valid_results) == 1:
        print_single_resume_results(valid_results[0], job_word_counts)
        save_single_result(valid_results[0], job_word_counts)
    else:
        print_summary_table(valid_results)
        all_keywords = sorted(job_keywords, key=lambda w: (-job_word_counts[w], w))
        header = print_keyword_matrix(all_keywords, valid_results)
        save_all_results(valid_results, all_keywords, job_word_counts, header)

if __name__ == "__main__":
    main()