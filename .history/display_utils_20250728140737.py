import os

# ================================
# Print the CLI Introduction Banner
# ================================
def print_intro():
    """
    Prints an intro message with basic instructions for the CLI tool.
    """
    print("=== Resume Keyword Matcher ===\n")
    print("Compare up to 3 resumes against a job description.")
    print("See which resume covers the most important keywords for the job.\n")
    print("Resumes with more keyword matches may stand out more to employers.\n")

# ================================
# Print Results for a Single Resume
# ================================
def print_single_resume_results(result, job_word_counts):
    """
    Prints detailed match results for one resume:
      - Match percent
      - List of matched keywords with job description frequencies
      - List of missing keywords with job description frequencies
    """
    print(f"\n=== RESULTS for {os.path.basename(result['resume_path'])} ===")
    print(f"Match Percent: {result['match_percent']:.1f}%\n")
    print(f"Matched Keywords ({result['num_matched']}):")
    print(f"{'Keyword':<20} {'Frequency in JD':>16}")
    print("-" * 36)
    for word in sorted(result['matched'], key=lambda w: (-job_word_counts[w], w)):
        print(f"{word:<20} {job_word_counts[word]:>16}")
    print(f"\nMissing Keywords ({result['num_missing']}):")
    print(f"{'Keyword':<20} {'Frequency in JD':>16}")
    print("-" * 36)
    for word in sorted(result['missing'], key=lambda w: (-job_word_counts[w], w)):
        print(f"{word:<20} {job_word_counts[word]:>16}")

# ================================
# Print the Summary Table (Multi-Resume)
# ================================
def print_summary_table(valid_results):
    """
    Prints a summary table for multiple resumes:
      - File name
      - Match percent
      - Number of matched and missing keywords
    """
    print("\n=== SUMMARY ===")
    print(f"{'Resume File':<28} {'Match %':>8} {'#Matched':>10} {'#Missing':>10}")
    print("-" * 60)
    for r in valid_results:
        print(f"{os.path.basename(r['resume_path']):<28} {r['match_percent']:>8.1f} {r['num_matched']:>10} {r['num_missing']:>10}")

# ================================
# Print the Keyword Comparison Matrix
# ================================
def print_keyword_matrix(all_keywords, valid_results):
    """
    Prints a side-by-side matrix showing, for each job keyword,
    the frequency in each resume.
    Header: Keyword | resume1.txt | resume2.txt | ...
    Returns the header (list of column names) for reuse.
    """
    print("\n=== KEYWORD COMPARISON ===")
    header = ["Keyword"] + [os.path.basename(r['resume_path']) for r in valid_results]
    print(" | ".join(f"{col:<15}" for col in header))
    print("-" * (18 * len(header)))
    for word in all_keywords:
        row = [f"{word:<15}"]
        for r in valid_results:
            row.append(f"{r['resume_counts'].get(word, 0):<15}")
        print(" | ".join(row))
    return header  # Useful if you want to reuse in save logic
