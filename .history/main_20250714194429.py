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


def main():
    print_intro()
    job_path = prompt_job_path()
    resume_paths = prompt_resume_paths()
    job_keywords, job_word_counts = process_job_description(job_path)
    valid_results = process_resumes(resume_paths, job_keywords, job_word_counts)
    if len(valid_results) == 1:
        print_single_resume_results(valid_results[0], job_word_counts)
        save_single_result(valid_results[0], job_word_counts)
    else:
        print_summary_table(valid_results)
        header = print_keyword_matrix(all_keywords, valid_results)
        save_all_results(valid_results, all_keywords, job_word_counts, header)

if __name__ == "__main__":
    main()